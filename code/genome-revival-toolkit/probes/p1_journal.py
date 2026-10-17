"""D6 OS crash probe, not runtime code or a general JCS implementation.

Synthetic event values are restricted to ASCII and small integers. For this
subset only, sorted compact stdlib JSON has JCS bytes. P3 is a separate gate.
"""
import argparse
import hashlib
import json
import multiprocessing as mp
import os
import platform
import random
import sys
import tempfile
import time
from pathlib import Path

SEED=20261016
GENESIS='0'*64  # Probe-only boundary; production genesis convention is unspecified.


def subset_bytes(value):
    def check(item):
        if isinstance(item,str): item.encode('ascii')
        elif type(item) is int:
            if abs(item)>2**53-1: raise ValueError('Outside probe integer subset')
        elif item is None or isinstance(item,bool): pass
        elif isinstance(item,list):
            for v in item: check(v)
        elif isinstance(item,dict):
            for k,v in item.items(): check(k); check(v)
        else: raise ValueError('Outside probe JSON subset')
    check(value)
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')


def event(seq,prev,padding=64,kind='step.completed',payload=None):
    value={'seq':seq,'time':'2026-01-01T00:00:00.000Z','run_id':'a'*16,'type':kind,'actor':{'kind':'program','name':'synthetic-probe','version':'0.0.0'},
           'payload':payload if payload is not None else {'step_id':'s1','outputs':{'materials':{},'documents':{},'artifacts':[]},'values':{'padding':'x'*padding},'unverified':[],'verdict_ids':[],'duration_ms':0},'refs':[],'prev':prev}
    value['hash']=hashlib.sha256(subset_bytes(value)+prev.encode('ascii')).hexdigest()
    return value


def append(stream,value):
    data=subset_bytes(value)+b'\n'
    count=stream.write(data)  # exactly one write per serialized event
    if count!=len(data): raise OSError('Short write')
    stream.flush()
    os.fsync(stream.fileno())


def validate(data):
    lines=data.splitlines(keepends=True)
    previous=GENESIS; offset=0
    for index,line in enumerate(lines):
        try:
            value=json.loads(line)
            claimed=value.pop('hash')
            if value['seq']!=index+1 or value['prev']!=previous: raise ValueError('Order or predecessor')
            calculated=hashlib.sha256(subset_bytes(value)+previous.encode('ascii')).hexdigest()
            if claimed!=calculated: raise ValueError('Digest')
        except (ValueError,KeyError,UnicodeError):
            if index!=len(lines)-1: raise ValueError('Non-tail corruption')
            return index,offset,previous,len(data)-offset
        previous=claimed; offset+=len(line)
    return len(lines),offset,previous,0


def recover(path):
    before=path.read_bytes()
    count,offset,previous,discarded=validate(before)
    if discarded:
        with path.open('r+b') as stream:
            stream.truncate(offset)
            stream.seek(offset)
            append(stream,event(count+1,previous,kind='journal.recovered',payload={'discarded_bytes':discarded,'reason':'Incomplete or invalid final line.'}))
    after=path.read_bytes()
    final_count,_,_,final_bad=validate(after)
    if final_bad: raise AssertionError('Recovery failed')
    return count,discarded,final_count


def writer(path,ready,phase,ack,size):
    previous=GENESIS
    with Path(path).open('ab') as stream:
        for seq in range(1,1000000):
            phase.value=1
            value=event(seq,previous,size)
            data=subset_bytes(value)+b'\n'
            phase.value=2
            written=stream.write(data)
            if written!=len(data): raise OSError('Short write')
            phase.value=3
            stream.flush()
            phase.value=4
            os.fsync(stream.fileno())
            ack.value=seq
            previous=value['hash']
            if seq==1: ready.set()


def controls(directory):
    first=event(1,GENESIS); second=event(2,first['hash']); third=event(3,second['hash'])
    lines=[subset_bytes(v)+b'\n' for v in [first,second,third]]
    rows=[]
    for label,data,expected,discarded in [('partial_tail',lines[0]+lines[1][:20],1,20),('bad_tail_hash',lines[0]+lines[1].replace(b'"seq":2',b'"seq":9'),1,len(lines[1]))]:
        path=directory/(label+'.ndjson');path.write_bytes(data)
        count,removed,total=recover(path)
        assert (count,removed,total)==(expected,discarded,expected+1)
        rows.append({'case':label,'passed':True,'retained':count,'discarded':removed})
    path=directory/'bad_middle.ndjson'; data=lines[0]+lines[1].replace(b'"seq":2',b'"seq":9')+lines[2];path.write_bytes(data)
    rejected=False
    try: recover(path)
    except ValueError: rejected=True
    assert rejected and path.read_bytes()==data
    rows.append({'case':'non_tail_corruption','passed':True,'unchanged':True})
    return rows


def benchmark(path,count):
    previous=GENESIS;start=time.perf_counter()
    with path.open('wb') as stream:
        for seq in range(1,count+1):
            value=event(seq,previous)
            append(stream,value); previous=value['hash']
            if seq%10000==0: print(f'benchmark {count}: {seq} fsynced',flush=True)
    write_s=time.perf_counter()-start;start=time.perf_counter()
    actual,_,_,bad=validate(path.read_bytes());validate_s=time.perf_counter()-start
    assert actual==count and bad==0
    return {'events':count,'bytes':path.stat().st_size,'append_seconds':round(write_s,6),'validate_seconds':round(validate_s,6),'fsync_per_event':True}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials',type=int,default=200)
    parser.add_argument('--output',type=Path,default=Path('probes/runs/p1.json'))
    args=parser.parse_args()
    if args.trials<200: parser.error('P1 acceptance requires at least 200 trials')
    rng=random.Random(SEED); rows=[]
    context=mp.get_context('spawn')
    with tempfile.TemporaryDirectory(prefix='s0_journal_') as directory:
        directory=Path(directory)
        control_rows=controls(directory)
        for trial in range(args.trials):
            path=directory/f'trial-{trial}.ndjson'
            ready=context.Event();phase=context.RawValue('i',0);ack=context.RawValue('i',0)
            size=rng.choice([64,512,4096,65536])
            process=context.Process(target=writer,args=(str(path),ready,phase,ack,size))
            started=time.perf_counter(); process.start()
            if not ready.wait(10):
                process.kill();process.join();raise RuntimeError('Child did not reach first fsync')
            delay=rng.uniform(0,0.035);time.sleep(delay)
            observed_phase=phase.value; acknowledged=ack.value
            process.kill();process.join(10)
            if process.is_alive(): raise RuntimeError('Kill did not terminate child')
            before_size=path.stat().st_size
            count,discarded,final_count=recover(path)
            ok=count>=acknowledged
            rows.append({'trial':trial+1,'delay_ms':round(delay*1000,4),'phase_observed':observed_phase,'padding_bytes':size,'acknowledged_fsync':acknowledged,'retained':count,'discarded_bytes':discarded,'final_count':final_count,'bytes_before':before_size,'passed':ok,'seconds':round(time.perf_counter()-started,6)})
            path.unlink()
            if (trial+1)%25==0: print(f'kill trials {trial+1}/{args.trials}',flush=True)
        timings=[benchmark(directory/f'bench-{n}.ndjson',n) for n in [10000,100000]]
    report={'environment':{'python':platform.python_version(),'os':platform.platform()},'seed':SEED,'trials':rows,'controls':control_rows,'benchmarks':timings,
            'passed':all(r['passed'] for r in rows),'limits':['Synthetic ASCII/safe-integer serialization subset only; not JCS conformance.','Hard process termination, not power loss or disk-controller failure.','Probe genesis is not a production decision.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'trials':len(rows),'failures':sum(not r['passed'] for r in rows),'recovered_tails':sum(r['discarded_bytes']>0 for r in rows),'benchmarks':timings},indent=2),flush=True)
    return not report['passed']


if __name__=='__main__': raise SystemExit(main())
