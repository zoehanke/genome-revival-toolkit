"""Assess marked preparation primers using recorded, explicit constraints only."""
from decimal import Decimal, InvalidOperation

from dna_design_core.kernel.public import ToolkitError
from dna_design_core.biology.public import calculate_tm_explicit
from .primers import primer_documents,primer_uses
from .builtin.check.content import verdict

THERMAL_NOT_ASSESSED='Thermal acceptance was not assessed: no temperature window and concentrations were supplied.'


def assess(ctx):
    checked=[];differences=[];unknown=[];limits=[]
    try:
        documents=primer_documents(ctx.view)
        if not documents:
            return verdict(ctx,'check.primer_quality','NOT_APPLICABLE','No bound preparation primer output was recorded.',{},'preparation_model')
        for item in documents:
            if item.get('invalid'):
                unknown.append(item['invalid']);continue
            doc=item['document'];params=item['producer_parameters'];uses=primer_uses(ctx.view,item['parent'])
            # PROVISIONAL(C5/C7): reuse existing primer-set-v1 declarations;
            # no synthetic temperature, length, dimer or hairpin threshold.
            low=params.get('primer_length',params.get('length_min',doc.get('length_min')))
            high=params.get('primer_length',params.get('length_max',doc.get('length_max')))
            if type(low) is not int or type(high) is not int or not 1 <= low <= high:
                unknown.append('No valid explicit annealing-length window.');continue
            for key,expected in (('length_min',low),('length_max',high)):
                if key in doc and doc[key]!=expected:differences.append({'document_id':item['document_id'],'field':key})
            thermal=any(key in doc or key in params and params[key] is not None for key in ('tm_min','tm_max','tm_parameters'))
            if thermal:
                for key in ('tm_min','tm_max','tm_parameters'):
                    if key not in doc:raise ValueError('Incomplete explicit thermal criteria')
                    if params.get(key) is not None and doc[key]!=params[key]:differences.append({'document_id':item['document_id'],'field':key})
                t_low,t_high=Decimal(doc['tm_min']),Decimal(doc['tm_max'])
                if not t_low.is_finite() or not t_high.is_finite() or t_low>t_high:raise ValueError('Invalid thermal window')
            else:
                limits.append(THERMAL_NOT_ASSESSED)
            if not doc['primers'] or not uses:
                unknown.append('No primer rows or recorded complete oligo uses.');continue
            for row in doc['primers']:
                identity={'document_id':item['document_id'],'primer_id':row['id']}
                sequence=row['sequence'].upper();length=row['core_length']
                if type(length) is not int or not 1<=length<=len(sequence) or set(sequence)-set('ACGT'):
                    differences.append({**identity,'field':'core_length_or_sequence'});continue
                matching=[use for use in uses if use['material']['sequence'].upper()==sequence]
                if not matching:
                    unknown.append('No recorded use matches a declared complete oligo.');continue
                faults=[]
                if not low<=length<=high:faults.append('core_length_window')
                if any(use['core_length']!=length for use in matching):faults.append('recorded_core_length')
                report={**identity,'full_length':len(sequence),'core_length':length,'length_window':[low,high]}
                if thermal:
                    tm=calculate_tm_explicit(sequence[-length:],doc['tm_parameters'])
                    report['annealing_tm']=tm;report['temperature_window']=[doc['tm_min'],doc['tm_max']]
                    if not t_low<=Decimal(tm['tm'])<=t_high:faults.append('annealing_tm_window')
                checked.append(report)
                differences.extend({**identity,'field':field} for field in faults)
    except ToolkitError as error:
        if error.problem.code=='STORE_CORRUPT':differences.append({'field':'recorded_parameter_digest'})
        else:unknown.append('Recorded primer values or parameters unavailable.')
    except (ValueError,TypeError,KeyError,InvalidOperation):
        unknown.append('Primer declaration or explicit constraints unavailable or invalid.')
    return verdict(ctx,'check.primer_quality','FAIL' if differences else 'UNKNOWN' if unknown else 'PASS',
                   'Marked preparation primers assessed against explicit criteria only.',
                   {'primers':checked,'differences':differences,'unavailable':unknown},'preparation_model',limits)
