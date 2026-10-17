"""Generate capability, check and vocabulary references from local declarations."""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'src/dna_design_core/resources'
START='<!-- GENERATED:START -->'
END='<!-- GENERATED:END -->'


def documents():
    rows=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((RES/'capabilities').glob('*.json'))]
    result={}
    for filename,role in [('capabilities.md','ACTION'),('checks.md','CHECK')]:
        lines=['# '+('Capabilities' if role=='ACTION' else 'Checks'),'','Generated from exported capability declarations.','']
        for row in rows:
            if row['role']!=role:continue
            lines.extend(['## '+row['id'],'',row['summary'],'','- Version: '+row['version'],'- Effects: '+', '.join(row['effects'])])
            if role=='CHECK':lines.extend(['- Scope: '+row['scope'],'- Offline: '+str(row['offline']).lower()])
            lines.extend(['- Does not establish: '+'; '.join(row['does_not_establish']),'',
                          '```json',json.dumps({key:row[key] for key in ['inputs','params','outputs','final_checks']},ensure_ascii=False,indent=2),'```',''])
        result[ROOT/'docs'/filename]='\n'.join(lines)
    vocab=json.loads((RES/'vocab.json').read_text(encoding='utf-8'));lines=['# Vocabulary','','Generated from vocab.json.','']
    for category,values in vocab.items():
        lines.extend(['## '+category,''])
        lines.extend('- '+str(row['value'])+': '+row['description'] for row in values);lines.append('')
    result[ROOT/'docs/vocabulary.md']='\n'.join(lines)
    skill=ROOT/'skill/SKILL.md';text=skill.read_text(encoding='utf-8')
    listing='\n'.join('- '+r['id']+' ('+r['role']+'): '+r['summary'] for r in rows)
    result[skill]=text.split(START)[0]+START+'\n'+listing+'\n'+END+text.split(END)[1]
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    missing=[]
    for path,text in documents().items():
        if args.check:
            if not path.exists() or path.read_text(encoding='utf-8')!=text:missing.append(path.relative_to(ROOT).as_posix())
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8',newline='\n')
    print(json.dumps({'different':missing}));return bool(missing)


if __name__=='__main__':raise SystemExit(main())
