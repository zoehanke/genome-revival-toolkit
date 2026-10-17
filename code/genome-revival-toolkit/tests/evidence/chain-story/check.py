"""Independent standard-library oracle and demonstration card for sealed runs.

No Core/Kit imports. Expected DNA and bands follow fixed-seed construction.
PROVISIONAL(C11): combined card is an example projection of three immutable
records, not a claim that the stock single-run renderer loads multiple runs.
"""
import hashlib
from html import escape
import json
from pathlib import Path
import random
import re
import sys


def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rc(s):return s.translate(str.maketrans('ACGT','TGCA'))[::-1]
def fasta(path):return ''.join(s.strip() for s in path.read_text(encoding='utf-8').splitlines() if not s.startswith('>'))
def gb(path):return re.sub('[^acgt]','',path.read_text(encoding='utf-8').split('ORIGIN',1)[1].lower()).upper()
def bands(sequence,f,r):
    intervals=set()
    for left,right in ((f,r),(r,f)):
        for a in range(len(sequence)-len(left)+1):
            if sequence[a:a+len(left)]!=left:continue
            for b in range(a,len(sequence)-len(right)+1):
                if sequence[b:b+len(right)]==rc(right):intervals.add((a,b+len(right)))
    return sorted(b-a for a,b in intervals)


def events(package):return [json.loads(line) for line in (package/'journal-until-seal.ndjson').read_text(encoding='utf-8').splitlines()]
def incoming(package,name):return next(e['payload']['file_sha256'] for e in events(package) if e['type']=='input.registered' and e['payload']['source_id']==name)


def produced_file(package,step):
    row=next(e['payload'] for e in events(package) if e['type']=='step.completed' and e['payload']['step_id']==step)
    return package/row['outputs']['artifacts'][0]['run_path']


def check(root):
    root=Path(root);summary=load(root/'SUMMARY.json')
    packages={n:root/summary[n] for n in ('construct','identity','evidence','foreign_background')}
    c,i,e,w=(packages[n] for n in ('construct','identity','evidence','foreign_background'))
    rng=random.Random(2026101701);reference=''.join(rng.choice('ACGT') for _ in range(800));marker='ATG'+'AAA'*30+'TAA'
    gene='ATG'+'GCT'*38+'TAA';reference=reference[:300]+gene+reference[420:]
    assert len(gene)==120 and all(gene[k:k+3] not in {'TAA','TAG','TGA'} for k in range(3,117,3))
    edited=reference[:300]+marker+reference[420:];donor=reference[250:300]+marker+reference[420:470]
    assert fasta(root/'inputs/reference.fasta')==reference
    assert gb(produced_file(c,'original_file'))==reference and gb(produced_file(c,'edited_file'))==edited and gb(produced_file(c,'donor_file'))==donor
    assert len(donor)==196 and donor[:50]==reference[250:300] and donor[-50:]==reference[420:470]
    assay=load(c/'assay.json');regions={r['id']:(r['start'],r['end']) for r in assay['regions']}
    assert regions=={'replacement':(300,396),'left_arm':(250,300),'right_arm':(396,446)},regions
    f,r=reference[230:250],rc(reference[470:490])
    handoff=load(c/'identity-handoff.json');rows={v['id']:v for v in handoff['primers']}
    assert rows['left_forward']['sequence']==f and rows['right_reverse']['sequence']==r
    expected={'original':bands(reference,f,r),'edited':bands(edited,f,r)}
    assert expected=={'original':[260],'edited':[236]},expected
    table=load(i/'identity-expected-results.json')
    for row in table['backgrounds']:
        name=row['id'];assert row['reference_sha256']==sha(produced_file(c,name+'_file'))
        assert row['expected']=={'product_count':1,'product_bp':expected[name][0],'status':'DISTINGUISHABLE'},row
    good=load(e/'assessment.json');bad=load(w/'assessment.json')
    assert all(row['unit']=='colony' for row in load(root/'inputs/observations.json')['observations'])
    for assessment,wanted in ((good,'SUPPORTED'),(bad,'INSUFFICIENT')):
        local=[v for v in assessment['conclusions'] if v['claim']=='local_prediction_agreement']
        assert len(local)==2 and all(v['status']==wanted for v in local),local
        assert assessment['comparisons'][0]['difference']==8-30
        revival=next(v for v in assessment['conclusions'] if v['claim']=='functional_revival')
        assert revival['status']=='INSUFFICIENT'
    for row in load(root/'inputs/foreign-predictions.json')['backgrounds']:
        path=root/'inputs'/('foreign-'+row['id']+'.fasta')
        assert row['reference_sha256']==sha(path)
        assert bands(fasta(path),f,r)==[row['expected']['product_bp']]
    links=[]
    for source,target,path,registered in [('Construct','Genome Identity',c/'identity-handoff.json',incoming(i,'handoff')),
                                           ('Genome Identity','Revival Evidence',i/'identity-expected-results.json',incoming(e,'predictions'))]:
        digest=sha(path);assert digest==registered
        links.append({'source':source,'target':target,'basis':'hash_equal' if digest==registered else None,'sha256':digest})
    assert all(row['basis']=='hash_equal' for row in links)
    # Counterexample: a changed file does not become a hash-supported link.
    mismatch=hashlib.sha256((c/'identity-handoff.json').read_bytes()+b' ').hexdigest()
    assert mismatch!=incoming(i,'handoff')
    receipt=load(root/'receipts.json')
    assert any(r['receipt'].get('result',{}).get('failure',{}).get('code')=='SOURCE_CHANGED' for r in receipt)
    assert sum(r['network']['attempts'] for r in receipt)==0
    for package in packages.values():
        manifest=load(package/'manifest.json')
        for file in manifest['files']:assert sha(package/file['path'])==file['sha256']
    result={'donor_bp':196,'bands':expected,'local_agreement':'SUPPORTED','foreign_background':'INSUFFICIENT',
            'functional_revival':'INSUFFICIENT','hash_links':links,'mismatch_has_solid_link':False,'connections':0,
            'scope':'developer-assisted synthetic computational evidence; laboratory NOT_PERFORMED'}
    (root/'independent.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    labels=['Construct','Genome Identity','Revival Evidence'];svg=['<svg viewBox="0 0 900 165" role="img" aria-label="Three sealed runs connected by equal file hashes">']
    for j,label in enumerate(labels):
        x=10+j*300;svg.append(f'<rect x="{x}" y="15" width="250" height="75" rx="6"/><text x="{x+12}" y="43">{label}</text>')
        if j<2:
            row=links[j];svg.append(f'<path class="verified" data-basis="hash_equal" d="M{x+250},55 H{x+300}"/><text class="hash" x="{x+12}" y="70">{row["sha256"][:12]}</text>')
    svg.append('<path class="declared" data-basis="declared" d="M735,95 V125"/><text x="530" y="150">Local agreement supported; revival insufficient</text></svg>')
    text='''# Three-Kit sealed chain\n\nSynthetic calculation, not an experiment. Construct donor: 196 bp with two 50 bp arms. Expected local PCR: original 260 bp, edited 236 bp. Reported synthetic observations agree, so local agreement is SUPPORTED. Functional revival is INSUFFICIENT.\n\nTwo solid links mean only identical file SHA-256 between delivered output and registered next input. Other statements are declared. The foreign-background control is INSUFFICIENT and the changed handoff is rejected. Laboratory steps: PLANNED / NOT_PERFORMED.\n\nThis is an example projection composed from three sealed records. Stock single-run cards remain in each package. No causal relation or new runtime format is introduced.\n'''
    (root/'chain-card.md').write_text(text,encoding='utf-8')
    html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Three sealed Kit runs</title><style>body{font:16px/1.5 system-ui;max-width:1000px;margin:24px auto;padding:20px}svg{width:100%}rect{fill:#eff4ef;stroke:#52675a}text{font:16px system-ui}.hash{font:13px monospace}.verified{stroke:#176246;stroke-width:3;fill:none}.declared{stroke:#666;stroke-dasharray:5 4;fill:none}pre{white-space:pre-wrap;overflow-wrap:anywhere}</style><h1>Three sealed Kit runs</h1>'+''.join(svg)+'<p>Solid: equal output/input file hashes. Dashed: declared only.</p><pre>'+escape(text)+'</pre></html>'
    (root/'chain-card.html').write_text(html,encoding='utf-8');return result


if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1])),indent=2))
