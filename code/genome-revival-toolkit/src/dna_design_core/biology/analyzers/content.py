"""Structural material findings, with no empirical thresholds or phenotype claims."""
from ..materials import record_from_material,make_material
from ..sequence.preparation import inspect_cds


def annotation_findings(material: dict) -> list[dict]:
    findings=[];size=len(material['sequence'])
    for index,feature in enumerate(material['features']):
        codes=[];parts=feature.get('parts') or [feature]
        if not isinstance(parts,list) or not all(isinstance(part,dict) for part in parts):codes.append('INVALID_PARTS')
        else:
            for part in parts:
                if any(type(part.get(key)) is not int for key in ['start','end']) or not 0<=part.get('start',-1)<=part.get('end',-1)<=size:
                    codes.append('PART_OUT_OF_BOUNDS')
                if part.get('strand') not in (None,-1,0,1):codes.append('INVALID_STRAND')
            if parts and all(type(p.get(k)) is int for p in parts for k in ['start','end']):
                if (min(p['start'] for p in parts),max(p['end'] for p in parts))!=(feature['start'],feature['end']):codes.append('ENVELOPE_MISMATCH')
            if len(parts)>1 and feature.get('operator') not in ('join','order'):codes.append('INVALID_OPERATOR')
            if 'strand' in feature and feature['strand'] not in (None,-1,0,1):codes.append('INVALID_STRAND')
            if feature.get('strand') in (-1,1) and any(p.get('strand') not in (None,feature['strand']) for p in parts):codes.append('STRAND_CONFLICT')
        qualifiers=feature.get('qualifiers',{})
        if not isinstance(qualifiers,dict) or any(not isinstance(k,str) or not isinstance(v,list) or any(not isinstance(s,str) for s in v) for k,v in qualifiers.items()):codes.append('INVALID_QUALIFIERS')
        findings.extend({'feature_index':index,'code':code} for code in sorted(set(codes)))
    return findings


def cds_findings(material: dict) -> list[dict]:
    findings=[]
    for index,feature in enumerate(material['features']):
        if feature['type']!='CDS':continue
        try:
            qualifiers=feature.get('qualifiers',{})
            if 'pseudo' in qualifiers or 'pseudogene' in qualifiers:continue
            # NCBI Genetic Codes: omitted GenBank transl_table means standard 1.
            # https://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi#SG1
            table=qualifiers.get('transl_table',['1']);start=qualifiers.get('codon_start',['1'])
            if len(table)!=1 or len(start)!=1:raise ValueError('ambiguous coding qualifiers')
            partial='partial' in qualifiers and qualifiers['partial'] not in (['false'],['0'])
            record=record_from_material({**material,'features':[feature]})
            sequence=str(record.features[0].extract(record.seq))
            report=inspect_cds(sequence,int(table[0]),codon_start=int(start[0]),partial=partial)
            codes=[]
            if not partial:
                if report['trailing_bases']:codes.append('FRAME_LENGTH')
                if not report['start_codon_present']:codes.append('START_CODON')
                if not report['terminal_stop_present']:codes.append('TERMINAL_STOP')
            if report['internal_stop_count']:codes.append('INTERNAL_STOP')
            if report['ambiguous_base_count']:codes.append('AMBIGUOUS_CDS')
            findings.extend({'feature_index':index,'code':code,'coding_length':report['coding_length'],
                'internal_stop_count':report['internal_stop_count'],'translation_table':int(table[0])} for code in codes)
        except (ValueError,TypeError,KeyError,IndexError):
            findings.append({'feature_index':index,'code':'UNASSESSABLE_CDS'})
    return findings


def sanity_findings(material: dict) -> list[dict]:
    findings=[];sequence=material['sequence']
    # The alphabet is the existing kernel material DNA value contract.
    if not sequence:findings.append({'code':'EMPTY_MATERIAL'})
    if not set(sequence)<={'A','C','G','T','R','Y','S','W','K','M','B','D','H','V','N'}:findings.append({'code':'INVALID_DNA_SYMBOL'})
    if material.get('topology') not in (None,'linear','circular'):findings.append({'code':'INVALID_TOPOLOGY'})
    if material.get('strandedness') not in (None,'single','double'):findings.append({'code':'INVALID_STRANDEDNESS'})
    ends=material.get('ends')
    if ends is not None:
        if material.get('topology')!='linear' or material.get('strandedness')!='double':
            findings.append({'code':'PHYSICAL_END_CONFLICT'})
        elif not isinstance(ends,dict) or set(ends)!={'left','right'}:findings.append({'code':'INVALID_END_SHAPE'})
        else:
            for end in ends.values():
                if end is None:continue
                if not isinstance(end,dict) or set(end)!={'kind','overhang'} or end['kind'] not in ('blunt','5prime','3prime'):
                    findings.append({'code':'INVALID_END_SHAPE'});continue
                if not isinstance(end['overhang'],str) or (end['kind']=='blunt' and end['overhang']!='') or (end['kind']!='blunt' and (not end['overhang'] or not set(end['overhang'])<={'A','C','G','T'})):
                    findings.append({'code':'INVALID_OVERHANG'})
            if not findings and set(sequence)<={'A','C','G','T'}:
                try:make_material(**{**material,'features':[]})
                except (ValueError,TypeError,KeyError):findings.append({'code':'INVALID_DUPLEX_GEOMETRY'})
    return findings
