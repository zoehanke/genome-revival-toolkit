"""Independent mutations of text and schema, through the spec-lint CLI."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT.parents[1]
SCHEMAS=ROOT/'src/dna_design_core/resources/schemas'


class AlignmentTests(unittest.TestCase):
    def check_copy(self,edit_schema=None,edit_spec=None):
        with tempfile.TemporaryDirectory(prefix='s0_fields_') as directory:
            root=Path(directory)
            schemas=root/'schemas'
            shutil.copytree(SCHEMAS,schemas)
            if edit_schema: edit_schema(schemas)
            text=(REPO/'spec/SPEC.md').read_text(encoding='utf-8')
            if edit_spec: text=edit_spec(text)
            path=root/'SPEC.md'; path.write_text(text,encoding='utf-8',newline='\n')
            report=root/'report.json'
            result=subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/spec_lint.py'),str(path),'--schemas',str(schemas),'--fields-report',str(report)],capture_output=True,text=True,encoding='utf-8')
            return result,json.loads(report.read_text(encoding='utf-8'))

    @staticmethod
    def change(directory,name,mutator):
        path=directory/(name+'.json')
        data=json.loads(path.read_text(encoding='utf-8')); mutator(data)
        path.write_text(json.dumps(data),encoding='utf-8',newline='\n')

    def test_baseline_matches_updated_appendix(self):
        result,report=self.check_copy()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        # SPEC 8ad9c44 A2/A9 now lists the former body-only fields.
        self.assertEqual(report['counts'],{'schemas_compared':35,'field_differences':0,'unresolved':0})
        self.assertEqual(report['differences'],[])

    def test_unknown_schema_field_is_hard(self):
        result,report=self.check_copy(lambda p:self.change(p,'goal-v1',lambda s:s['properties'].update(invented={'type':'string'})))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='invented' and r['status']=='unresolved' for r in report['differences']))

    def test_missing_nested_field_is_hard(self):
        result,report=self.check_copy(lambda p:self.change(p,'goal-v1',lambda s:s['properties']['sources']['items']['properties'].pop('sha256')))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='sources[].sha256' for r in report['differences']))

    def test_new_spec_field_is_not_ignored(self):
        result,report=self.check_copy(edit_spec=lambda s:s.replace('`original_request`（字符串，宿主报告的用户原话）','`invented`、`original_request`（字符串，宿主报告的用户原话）',1))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['kind']=='missing_from_schema' and r['field']=='invented' for r in report['differences']))

    def test_appendix_field_cannot_be_removed(self):
        result,report=self.check_copy(lambda p:self.change(p,'capability-v1',lambda s:s['properties'].pop('offline')))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['kind']=='missing_from_schema' and r['field']=='offline' for r in report['differences']))

    def test_authorship_does_not_allow_new_children(self):
        result,report=self.check_copy(lambda p:self.change(p,'rule-v1',lambda s:s['properties']['authorship']['properties'].update(certified={'type':'boolean'})))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='authorship.certified' and r['status']=='unresolved' for r in report['differences']))

    def test_a14_profile_field_cannot_be_removed(self):
        result,report=self.check_copy(lambda p:self.change(p,'manifest-v1',lambda s:s['properties']['profile']['properties'].pop('profiles_digest')))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='profile.profiles_digest' for r in report['differences']))

    def test_a14_cause_field_cannot_be_added(self):
        result,report=self.check_copy(lambda p:self.change(p,'failure-v1',lambda s:s['properties']['cause_chain']['items']['properties'].update(stack={'type':'string'})))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='cause_chain[].stack' for r in report['differences']))

    def test_actor_fields_are_read_from_a14(self):
        result,report=self.check_copy(edit_spec=lambda s:s.replace('actor{kind,name,version?}','actor{kind,name,version?,invented}',1))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='created_by.invented' for r in report['differences']))

    def test_pipeline_revised_does_not_gain_diff(self):
        result,report=self.check_copy(lambda p:self.change(p,'events/pipeline.revised-payload-v1',lambda s:s['properties'].update(diff={'type':'array'})))
        self.assertEqual(result.returncode,1)
        self.assertTrue(any(r['field']=='diff' and r['kind']=='extra_in_schema' for r in report['differences']))


if __name__=='__main__': unittest.main()
