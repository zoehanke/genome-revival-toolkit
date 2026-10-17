"""Constructed and published kernel answers, independent of implementation."""
import copy
from decimal import Decimal
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from dna_design_core.kernel import canonical, ids, material, verdict
from dna_design_core.kernel.errors import ToolkitError


class KernelTests(unittest.TestCase):
    def test_sha256_published_abc(self):
        self.assertEqual(ids.file_sha256(b'abc'),'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
        self.assertEqual(ids.document_id({}),'44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a')

    def test_jcs_utf16_order_and_decimal(self):
        self.assertEqual(canonical.dumps({'\ufb33':1,'\U0001f600':2}),'{"😀":2,"דּ":1}'.encode('utf-8'))
        self.assertEqual(canonical.decimal_string(Decimal('60.10')),'60.10')
        with self.assertRaises(ToolkitError):canonical.dumps({'tm':60.1})
        with self.assertRaises(ToolkitError):canonical.loads('{"x":1,"x":2}')

    def test_material_identity_changes_only_with_content(self):
        source={'sequence':'aagt','topology':None,'strandedness':None,'ends':None,'features':[{'start':1,'end':3,'type':'misc_feature','label':'a','qualifiers':{'x':['v']}}]}
        before=ids.material_id(source)
        decorated={**source,'name':'other','date':'2026-01-01','description':'display only'}
        self.assertEqual(before,ids.material_id(decorated))
        changed=copy.deepcopy(source);changed['features'][0]['label']='b'
        self.assertNotEqual(before,ids.material_id(changed))
        changed=copy.deepcopy(source);changed['sequence']='AAGC'
        self.assertNotEqual(before,ids.material_id(changed))
        self.assertIsNone(material.normalize(source)['topology'])
        source['features'].append({'start':0,'end':1,'type':'misc_feature','label':'b','qualifiers':{'a':['x'],'z':['y']}})
        permuted=copy.deepcopy(source);permuted['features'].reverse()
        self.assertEqual(ids.material_id(source),ids.material_id(permuted))

    def test_verdict_requires_applicability_and_does_not_alias(self):
        args=dict(check={'id':'check.readback','version':'0.0.0'},scope='file',moment='final',subject={'kind':'document','id':'1'*64},outcome='PASS',issuer='check_capability',summary='Constructed verdict.')
        evidence={'length':4}
        value=verdict.make(**args,evidence=evidence)
        evidence['length']=8
        self.assertEqual(value['evidence']['length'],4)
        args['outcome']='NOT_APPLICABLE'
        with self.assertRaises(ToolkitError):verdict.make(**args)
        self.assertEqual(verdict.make(**args,applicability={'reason':'No material.','basis':['1'*64]})['outcome'],'NOT_APPLICABLE')


if __name__=='__main__':unittest.main()
