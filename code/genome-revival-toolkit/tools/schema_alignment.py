"""Compare named fields in the actual A/D/E text with draft schema properties.

This is field alignment, not interpretation of unspecified inner shapes or types.
It uses the field notation and referenced JSON examples, never runtime imports.
"""
import json
import re
import copy
from pathlib import Path


def split_fields(text):
    parts=[]; start=0; depth=0
    for index,char in enumerate(text):
        if char in '{[': depth+=1
        elif char in '}]': depth-=1
        elif char in ',，' and depth==0:
            parts.append(text[start:index]); start=index+1
    parts.append(text[start:])
    return parts


def parse_fields(text):
    # Parentheses describe types/constraints, never protocol field names.
    while re.search(r'\([^()]*\)|（[^（）]*）',text):
        text=re.sub(r'\([^()]*\)|（[^（）]*）','',text)
    text=text.strip().strip('`')
    if text.startswith('{') and text.endswith('}'): text=text[1:-1]
    result={}
    for part in split_fields(text):
        match=re.match(r'\s*([a-z][a-z0-9_]*)',part)
        if not match: continue
        name=match.group(1)
        tail=part[match.end():]
        if tail.startswith('-'): continue  # document format names, not fields
        child={}
        if '{' in tail:
            inside=tail[tail.index('{')+1:tail.rfind('}')]
            child=parse_fields(inside)
        array='[' in tail.split('{',1)[0]
        result[name+('[]' if array else '')]=child
    return result


def backtick_fields(text):
    result={}
    for token in re.findall(r'`([^`]+)`',text):
        if re.match(r'^[a-z][a-z0-9_]*(?:\?|\[|\{|\(|$)',token): result.update(parse_fields(token))
    return result


def shape_example(value):
    if isinstance(value,dict): return {k+('[]' if isinstance(v,list) else ''):shape_example(v) for k,v in value.items()}
    if isinstance(value,list) and value: return shape_example(value[0])
    return {}


def example(text,marker):
    section=text.split(marker,1)[1]
    block=re.search(r'```json\n(.*?)\n```',section,re.S).group(1)
    return shape_example(json.loads(block))


def expected_fields(text):
    appendix=text.split('# 附录 A 字段表',1)[1].split('# 附录 B',1)[0]
    segments={int(n):body for n,body in re.findall(r'\*\*A(\d+)\b(.*?)(?=\*\*A\d+\b|\Z)',appendix,re.S)}
    result={}
    for name,n in [('goal-v1',1),('capability-v1',2),('pipeline-v1',3),('pipeline-revision-v1',4),('event-v1',5),('verdict-v1',6),('failure-v1',7),('manifest-v1',10),('catalog-v1',11)]:
        section=segments[n]
        if n==3: section=section.split('**引用**',1)[0]
        if n in (2,6,10): section=section.split('。**',1)[0]
        result[name]=backtick_fields(section)
    # These appendix entries explicitly delegate to D examples/tables.
    result['verdict-v1']['schema']={}
    result['kit-v1']=example(text,'*清单 `kit-v1`*')
    result['rule-v1']=example(text,'*规则 `rule-v1`*')
    result['rule-v1']['parameters']={}  # D12 parameters are rule data, not protocol fields.
    result['review-v1']=example(text,'*审核记录 `review-v1`*')
    result['pipeline-template-v1']={**result['pipeline-v1'],'params_schema':{}}
    authorship=backtick_fields(segments[9])['authorship']
    applicability=segments[9].split('适用于',1)[1].split('（D20',1)[0]
    for name in re.findall(r'`([^`]+)`',applicability):
        result[name]['authorship']=copy.deepcopy(authorship)
    result['profiles-v1']=parse_fields(re.search(r'`(\{always:.*?\})`',segments[13]).group(1))
    receipt=re.search(r'\*\*回执信封\*\*.*?`(\{run_id.*?\})`',text).group(1)
    result['receipt-v1']=parse_fields(receipt)
    result['receipt-v1']['problems[]']={k:{} for k in ['code','category','message','location','recovery']}
    config=text.split('| 键 | 环境变量 | 默认 | 作用 |',1)[1].split('旧变量映射',1)[0]
    result['config-v1']={k:{} for k in re.findall(r'^\| `([a-z0-9_]+)`',config,re.M)}
    # A4 and A3 reference D5 and the four reference forms rather than listing their internals twice.
    result['pipeline-revision-v1']['operations[]']={}
    event_catalog=text.split('# 附录 E 日志事件目录',1)[1].split('# 附录 F',1)[0]
    for line in event_catalog.splitlines():
        match=re.match(r'^\| `([a-z]+\.[a-z_]+)` \| [^|]+ \| `(.+?)` \|',line)
        if match:
            name,descriptor=match.groups()
            fields=parse_fields(descriptor)
            if name=='call.recorded': fields['failure']={}
            result[name+'-payload-v1']=fields
    # A14 defines named interiors. Dynamic map keys remain map keys, never fields.
    a14=segments[14]
    def interior(label):
        line=next(line for line in a14.splitlines() if '`'+label+'`' in line)
        notation=re.search(r'`(\{[^`]+\})`',line).group(1)
        return parse_fields(notation)
    result['capability-v1']['requires_runtime[]']=interior('requires_runtime[]')
    result['failure-v1']['cause_chain[]']=interior('failure.cause_chain[]')
    result['manifest-v1']['profile']=interior('manifest.profile')
    result['receipt-v1']['event_range']=interior('event_range')
    actor=parse_fields(re.search(r'`actor\{([^`]+)\}`',a14).group(1))
    for name,field in [('run.created','created_by'),('goal.amended','by'),('run.abandoned','by'),('input.registered','declared_by')]:
        result[name+'-payload-v1'][field]=copy.deepcopy(actor)
    if 'RFC 6902' in a14:
        # A14 delegates operation member names to RFC 6902 sections 4.1–4.6.
        result['goal.amended-payload-v1']['diff']={key:{} for key in ['op','path','from','value']}
    for name in ['judge.finished','seal.rejected']:
        result[name+'-payload-v1']['unsatisfied[]']=interior('unsatisfied[]')
    stepref=parse_fields(re.search(r'`step`→`(\{[^`]+\})`',a14).group(1))
    result['step.started-payload-v1']['inputs']={'*':{'id':{},'origin':{'kind':{},'ref':stepref}}}
    completed=result['step.completed-payload-v1']
    result['step.failed-payload-v1']['retained_outputs']={k:copy.deepcopy(completed[k]) for k in ['outputs','values','unverified[]']}
    return result


def properties_at(schema):
    if schema.get('type')=='array': return properties_at(schema.get('items',{}))
    result=dict(schema.get('properties',{}))
    for key in ('oneOf','anyOf','allOf'):
        for branch in schema.get(key,[]): result.update(properties_at(branch))
    return result


def compare(text,directory):
    expected=expected_fields(text)
    actual={p.stem:json.loads(p.read_text(encoding='utf-8')) for p in Path(directory).rglob('*.json')}
    rows=[]
    def descend(name,fields,schema,prefix=''):
        if '*' in fields:
            for child in schema.get('patternProperties',{}).values():
                descend(name,fields['*'],child,prefix+'*.')
            if not schema.get('patternProperties'):
                rows.append({'schema':name,'field':prefix+'*','kind':'missing_map_shape','status':'unresolved','authority':'A14'})
            return
        props=properties_at(schema)
        wanted={k.removesuffix('[]'):k for k in fields}
        for key in sorted(set(wanted)|set(props)):
            display=wanted.get(key,key)
            path=prefix+display
            if key not in wanted or key not in props:
                rows.append({'schema':name,'field':path,'kind':'extra_in_schema' if key in props else 'missing_from_schema',
                             'status':'unresolved','authority':'A/D/E field table'})
            elif fields[display]: descend(name,fields[display],props[key],path+'.')
    for name,fields in expected.items():
        if name not in actual: rows.append({'schema':name,'field':'','kind':'missing_schema','status':'unresolved','authority':'A/E'})
        else: descend(name,fields,actual[name])
    for name in actual.keys()-expected.keys(): rows.append({'schema':name,'field':'','kind':'unlisted_schema','status':'unresolved','authority':'A/E'})
    return rows,{'schemas_compared':len(expected),'field_differences':len(rows),'unresolved':sum(r['status']=='unresolved' for r in rows)}
