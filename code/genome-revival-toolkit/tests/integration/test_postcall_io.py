"""Real API/Invoker controls: detect completed writes, do not claim a sandbox."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from dna_design_core.application import api
from tests.fixtures.contract_probe import action,port,build,goal,plan,step


def run_case(folder,body,effects=('pure',),*,composite=False,child=None,module_write=False,helper_import=False,dispatch=None):
    folder=Path(folder);source=folder/'source.txt';source.write_bytes(b'unchanged')
    original=action('file_task',[port('file','artifact',input=True)],[port('number','value')])
    original['effects']=list(effects);original['granularity']='composite' if composite else 'atomic'
    declarations=[(original,'def file_task(ctx, file):\n    from pathlib import Path\n'+''.join('    '+line+'\n' for line in body.splitlines())+'    return Outcome(values={"number":7})\n')]
    if child:
        helper=action('child',outputs=[port('number','value')]);helper['effects']=['writes_files']
        declarations.append((helper,'def child(ctx):\n    from pathlib import Path\n'+''.join('    '+line+'\n' for line in child.splitlines())+'    return Outcome(values={"number":7})\n'))
    kit=build(folder/'external',declarations);root=folder/'run';receipts=[]
    if helper_import:(kit/'capabilities/helper.py').write_text('VALUE=7\n',encoding='utf-8')
    if module_write:
        path=kit/'capabilities/unit.py';text=path.read_text(encoding='utf-8')
        path.write_text('from pathlib import Path\n(Path(__file__).resolve().parents[2]/"import-side-effect.txt").write_text("written",encoding="utf-8")\n'+text,encoding='utf-8')
    def call(verb,**options):
        result=(dispatch or api.call)(verb,root=root,kit_dirs=[kit],**options);receipts.append({'verb':verb,'receipt':result})
        (folder/'receipts.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8');return result
    assert not call('run create',directory=root)['problems']
    declared=call('goal declare',request=goal([{'source_id':'input','from':str(source),'as':'artifact','input_origin':'user_file','declared':{}}]));assert not declared['problems'],declared
    submitted=call('pipeline submit',request=plan(declared['result']['goal_digest'],[step('s1','file_task',{'file':{'source':'input'}})],{'step':'s1','port':'number'}));assert not submitted['problems'],submitted
    return root,call('run execute')


class PostCallIOTests(unittest.TestCase):
    def check_case(self,body,*,effects=('pure',),should_fail=True,child=None,module_write=False,helper_import=False):
        with tempfile.TemporaryDirectory() as folder:
            root,result=run_case(folder,body,effects,composite=child is not None,child=child,module_write=module_write,helper_import=helper_import)
            self.assertEqual(result['state'],'HALTED' if should_fail else 'COMPLETED',result)
            if should_fail:
                self.assertEqual(result['result']['failure']['code'],'CAPABILITY_OUTPUT_INVALID',result)
                self.assertIn('file',result['result']['failure']['message'].lower())
            return {p.relative_to(Path(folder)).as_posix():p.read_bytes() for p in Path(folder).rglob('*.txt')}

    def test_declared_write_inside_workdir_passes(self):
        files=self.check_case('(ctx.workdir/"allowed.txt").write_text("allowed",encoding="utf-8")',effects=('writes_files',),should_fail=False)
        self.assertEqual(files['run/work/s1/allowed.txt'],b'allowed')

    def test_declared_file_read_passes(self):
        self.check_case('assert Path(file).read_bytes()==b"unchanged"',effects=('reads_files',),should_fail=False)

    def test_interpreter_cache_is_not_a_capability_file_effect(self):
        previous=sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode=False
            self.check_case('pass',should_fail=False)
            self.assertFalse(sys.dont_write_bytecode)
        finally:sys.dont_write_bytecode=previous

    def test_lazy_helper_import_cache_is_not_a_capability_file_effect(self):
        previous=sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode=False
            self.check_case('from . import helper\nassert helper.VALUE==7',helper_import=True,should_fail=False)
            self.assertFalse(sys.dont_write_bytecode)
        finally:sys.dont_write_bytecode=previous

    def test_declared_writer_cannot_change_its_input(self):
        files=self.check_case('Path(file).write_text("changed",encoding="utf-8")',effects=('writes_files',))
        self.assertEqual(files['run/inputs/input/source.txt'],b'changed')

    def test_module_initialization_write_is_part_of_loading_the_capability(self):
        files=self.check_case('pass',module_write=True)
        self.assertEqual(files['import-side-effect.txt'],b'written')

    def test_new_file_outside_workdir_is_detected_after_it_was_written(self):
        files=self.check_case('(ctx.workdir.parent.parent/"outside.txt").write_text("written",encoding="utf-8")')
        self.assertEqual(files['run/outside.txt'],b'written')

    def test_transient_undeclared_write_cannot_hide_by_deleting(self):
        self.check_case('p=ctx.workdir/"transient.txt"\np.write_text("written",encoding="utf-8")\np.unlink()')

    def test_write_then_exception_still_reports_write_violation(self):
        files=self.check_case('(ctx.workdir.parent.parent/"outside.txt").write_text("written",encoding="utf-8")\nraise ValueError("deliberate body failure")')
        self.assertEqual(files['run/outside.txt'],b'written')

    def test_new_store_file_is_not_an_authorized_work_output(self):
        self.check_case('(ctx.workdir.parent.parent/"store/documents/unregistered.json").write_text("{}",encoding="utf-8")',effects=('writes_files',))

    def test_outside_run_write_is_observed_without_monitoring_whole_computer(self):
        files=self.check_case('(ctx.workdir.parent.parent.parent/"escaped.txt").write_text("written",encoding="utf-8")',effects=('writes_files',))
        self.assertEqual(files['escaped.txt'],b'written')

    def test_nested_broker_store_and_journal_writes_are_allowed(self):
        self.check_case('ctx.call("contract_probe.child",inputs={},params={})',effects=('writes_files',),child='(ctx.workdir/"allowed.txt").write_text("allowed",encoding="utf-8")',should_fail=False)

    def test_parent_cannot_swallow_nested_write_violation(self):
        self.check_case('try:\n    ctx.call("contract_probe.child",inputs={},params={})\nexcept Exception:\n    pass',effects=('writes_files',),child='(ctx.workdir.parent.parent/"outside.txt").write_text("written",encoding="utf-8")')


if __name__=='__main__':unittest.main()
