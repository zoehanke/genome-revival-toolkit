"""Windows directory publication probe. Locks are simulated, not real antivirus."""
import ctypes
from ctypes import wintypes
import json
import os
import platform
import tempfile
import threading
import time
from pathlib import Path


def main():
    if os.name!='nt':
        print('P2 requires Windows; not executed.'); return 2
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    create=kernel.CreateFileW
    create.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
    create.restype=wintypes.HANDLE
    close=kernel.CloseHandle
    close.argtypes=[wintypes.HANDLE];close.restype=wintypes.BOOL
    def hold(path,sharing):
        handle=create(str(path),0x80000000,sharing,None,3,0,None)
        if handle==wintypes.HANDLE(-1).value: raise ctypes.WinError(ctypes.get_last_error())
        return handle
    def attempt(source,target):
        start=time.perf_counter()
        try:
            source.rename(target)
            return {'renamed':True,'winerror':None,'seconds':time.perf_counter()-start}
        except OSError as exc:
            return {'renamed':False,'winerror':getattr(exc,'winerror',None),'seconds':time.perf_counter()-start}
    rows=[]
    with tempfile.TemporaryDirectory(prefix='s0_publish_') as directory:
        root=Path(directory)
        def pair(name):
            source=root/(name+'-stage');target=root/(name+'-sealed');source.mkdir()
            (source/'data.txt').write_text('synthetic candidate\n',encoding='utf-8',newline='\n')
            return source,target
        source,target=pair('existing');target.mkdir();(target/'keep.txt').write_bytes(b'existing target\n')
        result=attempt(source,target)
        result.update(case='target_exists',target_unchanged=(target/'keep.txt').read_bytes()==b'existing target\n',source_retained=source.exists())
        result['passed']=not result['renamed'] and result['target_unchanged'] and result['source_retained'];rows.append(result)
        for label,sharing in [('reader_shares_delete',7),('reader_no_delete_share',3)]:
            source,target=pair(label); handle=hold(source/'data.txt',sharing)
            try: result=attempt(source,target)
            finally: close(handle)
            attempts=[result]
            if not result['renamed']: attempts.append(attempt(source,target))
            rows.append({'case':label,'share_flags':sharing,'attempts':attempts,'passed':target.is_dir() and (target/'data.txt').read_text(encoding='utf-8')=='synthetic candidate\n','retry_needed':len(attempts)>1})
        source,target=pair('short_lock'); ready=threading.Event();lock_errors=[]
        def temporary_lock():
            try:
                handle=hold(source/'data.txt',3)
                ready.set()
                time.sleep(0.20)
                close(handle)
            except OSError as exc: lock_errors.append(getattr(exc,'winerror',None));ready.set()
        thread=threading.Thread(target=temporary_lock);thread.start()
        if not ready.wait(5): raise RuntimeError('Lock worker unavailable')
        attempts=[];start=time.perf_counter()
        for index in range(100):
            result=attempt(source,target);attempts.append(result)
            if result['renamed']: break
            time.sleep(0.02)
        thread.join()
        rows.append({'case':'simulated_antivirus_short_lock','hold_seconds':0.20,'retry_interval_seconds':0.02,'attempts':attempts,'elapsed_seconds':time.perf_counter()-start,'lock_errors':lock_errors,'passed':not lock_errors and attempts[-1]['renamed'] and (target/'data.txt').read_bytes()==b'synthetic candidate\n'})
    report={'environment':{'python':platform.python_version(),'os':platform.platform()},'cases':rows,'passed':all(r['passed'] for r in rows),
            'limits':['Synthetic Windows sharing locks, not a test of any installed antivirus.','Successful rename checks bytes and destination, not power-failure durability.']}
    output=Path('probes/runs/p2.json');output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))
    return not report['passed']


if __name__=='__main__': raise SystemExit(main())
