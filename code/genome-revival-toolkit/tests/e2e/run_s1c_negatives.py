"""Persist real public-API failure runs and an inherited-CDS sealing control.

Expectations follow literal edits: invalid strand, internal TAA, inconsistent
circular ends, one changed product base, 5-prime tail or recorded core length.
No result produced by a CHECK is used to manufacture its expected outcome.
"""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tests.s1c_runtime import material,run_material
from tests.s1c_reaction_runtime import prepare


def run(output):
    output=Path(output).resolve();output.mkdir(parents=True,exist_ok=False);summary={}
    bad_ends=material();bad_ends.update(topology='circular',ends={'left':None,'right':None})
    content=[('annotation',material(),material(strand=2),'check.annotation_integrity'),
             ('cds',material(kind='CDS'),material(kind='CDS',sequence='ATGTAATAA'),'check.cds_validity'),
             ('sanity',material(),bad_ends,'check.biological_sanity')]
    for name,source,product,check in content:
        root,kit,call,judged,verdicts=run_material(output/name,source,product)
        assert verdicts[check]['outcome']=='FAIL',verdicts[check]
        sealed=call('seal');assert not sealed['result']['sealed'],sealed
        assert any(row['check']==check and row['outcome']=='FAIL' for row in sealed['result']['unsatisfied'])
        summary[name]={'check':check,'outcome':'FAIL','sealed':False}
    for name,options,expected in [
        ('wrong-product',{'wrong':True},{'check.reaction_chain':'FAIL','check.model_agreement':'FAIL'}),
        ('wrong-tail',{'wrong_order':True},{'check.order_table':'FAIL'}),
        ('wrong-core-length',{'wrong_length':True},{'check.primer_quality':'FAIL'}),
        ('unsupported-route',{'method':'unsupported'},{'check.reaction_chain':'UNKNOWN'})]:
        root,kit,call,service=prepare(output/name,**options)
        judged=call('judge');assert not judged['problems'],judged
        verdicts={r['verdict']['check']['id']:r['verdict'] for r in judged['result']['verdicts']}
        for check,outcome in expected.items():assert verdicts[check]['outcome']==outcome,verdicts[check]
        sealed=call('seal');assert not sealed['result']['sealed'],sealed
        summary[name]={'checks':expected,'sealed':False}
    root,kit,call,judged,verdicts=run_material(output/'inherited-cds',material(kind='CDS',sequence='ATGTAATAA'))
    verdict=verdicts['check.cds_validity'];assert verdict['outcome']=='PASS',verdict
    assert any(f['origin']=='INHERITED' and f['code']=='INTERNAL_STOP' for f in verdict['evidence']['findings'])
    sealed=call('seal');assert sealed['result']['sealed'],sealed
    verified=call('verify',directory=root);assert verified['result']['verified'],verified
    package=Path(sealed['result']['manifest']).parent
    manifest=json.loads((package/'manifest.json').read_text(encoding='utf-8'))
    assert 'INHERITED_FINDINGS' in manifest['labels']
    assert 'Inherited input findings remain' in (package/'views/report.md').read_text(encoding='utf-8')
    summary['inherited-cds']={'outcome':'PASS','origin':'INHERITED','sealed':True,'verified':True,
                              'scope':'component content; no physical preparation asserted'}
    summary['kind']='developer-assisted synthetic computation; no laboratory work'
    (output/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(run(args.out),indent=2))
