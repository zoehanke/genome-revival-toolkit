"""Markdown view of the same projection as the offline HTML card."""


def render(card):
    lines=['# Run card','',f"Through event {card['cutoff']}",'','Journal head: '+card['head'],'','## Data chain','',
           'Solid = explicit input binding with equal content hashes. Dashed = declared only. Thin gray = record structure.','']
    nodes={n['id']:n for n in card['nodes']}
    for link in card['links']:
        style={'hash_equal':'solid','declared':'dashed',None:'structure'}[link['basis']]
        lines.append('- '+nodes[link['source']]['label']+' → '+nodes[link['target']]['label']+' ('+style+')')
    for title,key in [('Checked by the program','checked'),('Declared only','declared'),('Not done','not_done')]:
        lines.extend(['','## '+title,''])
        lines.extend('- '+value.replace('\n',' ') for value in card[key])
        if not card[key]:lines.append('No entries.')
    lines.extend(['','## Technical details',''])
    lines.extend('- Event '+str(row['seq'])+': '+row['type']+'; '+row['actor']+'; '+row['hash'] for row in card['timeline'])
    lines.extend(['',card['footer'],''])
    return '\n'.join(lines)
