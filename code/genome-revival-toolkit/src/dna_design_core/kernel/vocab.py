"""Single runtime vocabulary, loaded from the reviewed resource."""
import json
from pathlib import Path

RESOURCES=Path(__file__).resolve().parents[1]/'resources'


def values(category):
    document=json.loads((RESOURCES/'vocab.json').read_text(encoding='utf-8'))
    return tuple(item['value'] for item in document[category])
