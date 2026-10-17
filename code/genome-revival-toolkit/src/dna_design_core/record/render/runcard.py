"""Offline English HTML with a data chain and foldable technical records."""
from html import escape
import json
from ..projections import project
from .report import render as markdown


def _graph(card):
    positions={};parts=[];counts=[0,0,0]
    for node in card['nodes']:
        lane=node['lane'];x=20+lane*300;y=45+counts[lane]*105;counts[lane]+=1;positions[node['id']]=(x,y)
    height=max(counts)*105+80
    parts.append(f'<svg class="chain" viewBox="0 0 900 {height}" role="img" aria-label="Recorded data chain">')
    for index,title in enumerate(['Input sources','Executed steps','Retained outputs']):
        parts.append(f'<text x="{20+index*300}" y="22" class="lane">{title}</text>')
    for link in card['links']:
        x,y=positions[link['source']];xx,yy=positions[link['target']]
        x+=265;y+=32;yy+=32
        style={None:'structure','declared':'declared','hash_equal':'verified'}[link['basis']]
        parts.append(f'<path class="link {style}" data-basis="{link["basis"] or ""}" d="M{x} {y} C{x+30} {y} {xx-30} {yy} {xx} {yy}"/>')
    for node in card['nodes']:
        x,y=positions[node['id']];label=node['label']
        # SVG text is bounded by fixed line lengths, without clipping the title.
        lines=[label[i:i+32] for i in range(0,len(label),32)]
        parts.append(f'<g><title>{escape(label)}</title><rect x="{x}" y="{y}" width="265" height="82" rx="7"/>')
        for index,line in enumerate(lines[:2]):parts.append(f'<text x="{x+10}" y="{y+22+index*17}">{escape(line)}</text>')
        parts.append(f'<text x="{x+10}" y="{y+67}" class="hash">{escape(node["hash"][:12])}</text></g>')
    parts.append('</svg>');return ''.join(parts)


def render(events,snapshot,labels,not_verified):
    card=project(events,snapshot,labels,not_verified)
    columns=[]
    for title,key in [('Checked by the program','checked'),('Declared only','declared'),('Not done','not_done')]:
        body=''.join('<li>'+escape(text)+'</li>' for text in card[key]) or '<li>No entries.</li>'
        columns.append('<section><h2>'+title+'</h2><ul>'+body+'</ul></section>')
    detail=escape(json.dumps(card['timeline'],ensure_ascii=False,indent=2))
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Run card</title><style>
*{box-sizing:border-box}body{margin:0;background:#f4f4f0;color:#192720;font:15px/1.55 system-ui,sans-serif}
main{max-width:1180px;margin:32px auto;padding:0 20px}h1{margin:0}header p{margin:6px 0}.head{overflow-wrap:anywhere;font-size:12px}
.chain{width:100%;height:auto;background:white;border:1px solid #d5dad5;border-radius:10px;margin:20px 0}.chain rect{fill:#f3f6f3;stroke:#b5c5ba}.chain text{fill:#192720;font:12px system-ui}.chain .hash{font:11px monospace;fill:#4d6858}.chain .lane{font-weight:700}
.link{fill:none}.verified{stroke:#176246;stroke-width:2.5}.declared{stroke:#6c706d;stroke-width:1.5;stroke-dasharray:5 4}.structure{stroke:#b8bdb9;stroke-width:1}
.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.columns section{background:#fff;border-top:3px solid #527c63;padding:16px;overflow-wrap:anywhere}h2{font-size:17px;margin:0 0 12px}ul{padding-left:20px}li{margin:8px 0}details{margin:24px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px}footer{border-top:1px solid #b5c5ba;padding:18px 0}
@media(max-width:700px){main{margin:20px auto}.columns{grid-template-columns:1fr}}
</style><main><header><h1>Run card</h1>'''
    html+=f'<p>Through event {card["cutoff"]}</p><p class="head">Journal head: {escape(card["head"])}</p></header>'
    html+=_graph(card)+'<p>Solid: explicit input binding and equal content hashes. Dashed: declared only. Thin gray: record structure.</p>'
    html+='<div class="columns">'+''.join(columns)+'</div><details><summary>Technical details</summary><pre>'+detail+'</pre></details>'
    html+='<footer>'+card['footer']+'</footer></main></html>\n'
    return {'html':html,'markdown':markdown(card)}
