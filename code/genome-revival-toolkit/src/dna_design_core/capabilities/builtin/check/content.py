"""Read-only content obligations; inherited handling belongs only to two checks."""
from dna_design_core.kernel.public import Outcome,capability,make,core_version
from dna_design_core.biology.public import annotation_findings,cds_findings,sanity_findings
from ...declaration import check
from ...material_evidence import material_rows,root_materials,finding_origin
from ...recorded import catalog as frozen_catalog


def declaration(identity,function,summary,limits):
    value=check(identity,'content_model',__name__+':'+function,summary)
    value['fixtures']={key:'tests/fixtures/s1c/'+identity+'.'+key+'.json' for key in ['pass','fail']}
    value['source']['algorithm_refs']=['SPEC D7; INV-A10; D8','Biopython SeqFeature exact local location contract']
    value['requires_runtime']=[{'kind':'python_package','name':'biopython','probe':None}]
    value['does_not_establish']=limits
    return value


def verdict(ctx,identity,outcome,summary,evidence,scope='content_model',not_verified=()):
    events=ctx.view.events();candidate=ctx.view.candidate
    declaration=next(r['declaration'] for r in frozen_catalog(ctx.view)['capabilities'] if r['declaration']['id']==identity)
    return Outcome(verdicts=[make(check={'id':identity,'version':core_version()},scope=scope,
        moment=candidate.get('moment','final'),issuer=candidate.get('issuer','check_capability'),
        subject={'kind':'run','id':events[0]['run_id']},constraint_id=candidate.get('constraint',{}).get('id'),
        outcome=outcome,summary=summary,evidence=evidence,basis=[e['hash'] for e in events],
        applicability={'reason':summary,'basis':[e['hash'] for e in events]} if outcome=='NOT_APPLICABLE' else None,
        does_not_establish=list(dict.fromkeys([*declaration['does_not_establish'],*not_verified])))])


def inherited_check(ctx,identity,analyze):
    findings=[];count=0
    for row in material_rows(ctx.view):
        count+=1;source_values,complete=root_materials(ctx.view,row['step_id'])
        for item in analyze(row['material']):
            origin,comparison=finding_origin(row['material'],item,source_values,complete,analyze)
            findings.append({**{k:v for k,v in row.items() if k!='material'},**item,'origin':origin,'comparison':comparison})
    outcome='FAIL' if any(f['origin']!='INHERITED' for f in findings) else 'PASS' if count else 'NOT_APPLICABLE'
    return verdict(ctx,identity,outcome,'Output findings compared with explicitly bound input features.' if count else 'No material output was recorded.',{'materials_checked':count,'findings':findings})


@capability(declaration('check.annotation_integrity','annotation_integrity',
    'Validate annotation locations and classify findings against explicit input ancestry.',
    ['Biological correctness of feature names or strand/function claims.','Experimental function or correct transcription.']))
def annotation_integrity(ctx) -> Outcome:
    return inherited_check(ctx,'check.annotation_integrity',annotation_findings)


CDS=declaration('check.cds_validity','cds_validity',
    'Check annotated coding frames, starts/stops and internal stops with inherited-finding witnesses.',
    ['Gene expression, protein activity, selectable phenotype or wet-laboratory function.',
     'Complete-CDS start/stop validation of explicitly partial or pseudogene annotations.',
     'Programmed frameshifts, recoding or unannotated strain-specific genetic code differences.'])
CDS['source']['algorithm_refs'].append('https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi#SG1')


@capability(CDS)
def cds_validity(ctx) -> Outcome:
    if not any(f['type']=='CDS' for row in material_rows(ctx.view) for f in row['material']['features']):
        return verdict(ctx,'check.cds_validity','NOT_APPLICABLE','No CDS feature was present in recorded material outputs.',{'features_checked':0,'findings':[]})
    return inherited_check(ctx,'check.cds_validity',cds_findings)


SANITY=declaration('check.biological_sanity','biological_sanity',
    'Check nonempty DNA symbols and consistency of declared topology, strands and ends.',
    ['Experimental viability, function, efficiency or host-specific performance.',
     'Unknown physical properties or ambiguous base identities.',
     'Empirical thresholds not supplied by sourced rule data.'])
SANITY['source']['algorithm_refs']=['SPEC D7 biological_sanity','kernel.material DNA value contract','biology.materials explicit duplex-end contract']


@capability(SANITY)
def biological_sanity(ctx) -> Outcome:
    rows=list(material_rows(ctx.view));findings=[]
    for row in rows:
        findings.extend({**{k:v for k,v in row.items() if k!='material'},**item} for item in sanity_findings(row['material']))
    return verdict(ctx,'check.biological_sanity','FAIL' if findings else 'PASS' if rows else 'NOT_APPLICABLE',
        'Nonempty DNA and physical declarations checked without empirical thresholds.' if rows else 'No material output was recorded.',
        {'materials_checked':len(rows),'findings':findings})
