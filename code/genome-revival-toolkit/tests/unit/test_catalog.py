import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from dna_design_core.catalog.registry import Catalog


def toy(root,body='raise AssertionError("discovery imported implementation")\n',name='toy'):
    root.mkdir(parents=True)
    (root/'capabilities').mkdir()
    declaration=json.loads((ROOT/'tests/fixtures/schemas/capability-v1.valid.json').read_text(encoding='utf-8'))['data']
    declaration.update(id='toy.length',owner='kit:toy')
    declaration['source']['implemented_in']='toy.capabilities.unit:run'
    (root/'capabilities/unit.py').write_text(body,encoding='utf-8')
    (root/'capabilities/unit.json').write_text(json.dumps(declaration),encoding='utf-8')
    manifest={'schema':'kit-v1','name':name,'title':'Toy','version':'0.0.0','requires_core':{'minimum':'0.0.0','maximum_exclusive':'1.0.0'},'contributes':{'capabilities':['capabilities/unit.json'],'knowledge':[],'templates':[],'text':[]},'does_not_establish':['Science.'],'review':'knowledge/review/'}
    (root/'kit.json').write_text(json.dumps(manifest),encoding='utf-8')
    return manifest


class CatalogTests(unittest.TestCase):
    def test_bundled_discovery_and_explicit_duplicate_are_distinct_from_external(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'toy';toy(root)
            with patch('dna_design_core.catalog.registry.BUNDLED',Path(d)):
                catalog=Catalog([root]);self.assertEqual(len(catalog.kit_receipts),1)
                self.assertEqual(catalog.kit_receipts[0]['origin'],'bundled');self.assertEqual(catalog.notices,[])

    def test_metadata_discovery_and_removal(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'toy';toy(root)
            catalog=Catalog([root])
            self.assertEqual(catalog.declaration('toy.length')['role'],'ACTION')
            self.assertTrue(catalog.notices)
            snap=catalog.snapshot('dev-tree')
            self.assertIn('always',snap['profiles'])
            self.assertEqual(snap['capabilities'][-1]['declaration']['granularity'],'atomic')
            self.assertNotIn('toy.length',[c['id'] for c in Catalog().describe('capabilities')])

    def test_bad_kit_is_isolated(self):
        with tempfile.TemporaryDirectory() as d:
            good=Path(d)/'good';toy(good)
            bad=Path(d)/'bad';bad.mkdir();(bad/'kit.json').write_text('{}',encoding='utf-8')
            catalog=Catalog([bad,good])
            self.assertTrue(catalog.declaration('toy.length'))
            self.assertEqual(catalog.problems[0]['code'],'KIT_MANIFEST_INVALID')

    def test_conflicting_external_implementations_disable_both(self):
        with tempfile.TemporaryDirectory() as d:
            left=Path(d)/'left';right=Path(d)/'right'
            toy(left,body='x=1\n');toy(right,body='x=2\n')
            catalog=Catalog([left,right])
            self.assertNotIn('toy.length',[c['id'] for c in catalog.describe('capabilities')])
            self.assertTrue(any(p['code']=='KIT_NAME_CONFLICT' for p in catalog.problems))


if __name__=='__main__':unittest.main()
