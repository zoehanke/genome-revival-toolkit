"""Explain the retained shared-primer failure without Core/Kit imports."""
import json
from pathlib import Path
import sys
from check import bands,fasta,rc


def check(root):
    root=Path(root);reference=fasta(root/'inputs/reference.fasta');marker=fasta(root/'inputs/marker.fasta')
    assert reference[300:420]=='ATG'+'AAA'*38+'TAA'
    edited=reference[:300]+marker+reference[420:]
    left=(reference[230:250],rc(marker[:20]));right=(marker[-20:],rc(reference[470:490]))
    result={name:{'original':bands(reference,*pair),'edited':bands(edited,*pair)} for name,pair in [('left',left),('right',right)]}
    assert result=={'left':{'original':[90],'edited':[90]},'right':{'original':[90],'edited':[90]}},result
    issued=[]
    for line in (root/'construct/run/journal.ndjson').read_text(encoding='utf-8').splitlines():
        event=json.loads(line)
        if event['type']=='verdict.issued':issued.append(event['payload']['verdict'])
    assert any(v['check']['id']=='construct.check_junction_assay' and v['outcome']=='FAIL' for v in issued)
    result['meaning']='Original and edited backgrounds both amplify: junction discrimination fails. The gate correctly refused sealing.'
    (root/'independent-negative.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');return result


if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1])),indent=2))
