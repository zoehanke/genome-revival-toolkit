"""Run creation records external-tool fingerprints, never personal paths."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from dna_design_core.application import api


class ExternalEnvironmentTests(unittest.TestCase):
    def test_unavailable_program_does_not_invent_version_or_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);config=folder/'config.json'
            config.write_text(json.dumps({'primer3_core':str(folder/'missing.exe')}),encoding='utf-8')
            with patch.dict('os.environ',{},clear=True),patch('dna_design_core.application.run_service.platform.system',return_value='synthetic platform'):
                created=api.call('run create',directory=folder/'run',config_path=config)
            self.assertEqual(created['problems'],[],created)
            event=json.loads((folder/'run/journal.ndjson').read_text(encoding='utf-8').splitlines()[0])
            self.assertEqual(event['payload']['environment']['external_tools'],[])
            self.assertTrue(any('unavailable' in text for text in created['result']['notices']))

    def test_configured_tool_version_and_actual_file_hash_are_recorded(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);program=folder/'tool.exe';program.write_bytes(b'abc')
            path=folder/'config.json';path.write_text(json.dumps({'primer3_core':str(program)}),encoding='utf-8')
            with patch.dict('os.environ',{},clear=True),patch('dna_design_core.application.run_service.platform.system',return_value='synthetic platform'),patch('dna_design_core.application.config.shutil.which',return_value=None),patch('dna_design_core.engine.invoker.subprocess.run',return_value=subprocess.CompletedProcess([],0,'primer3_core release 2.6.1\n','')) as launch:
                created=api.call('run create',directory=folder/'run',config_path=path)
            self.assertEqual(created['problems'],[],created)
            event=json.loads((folder/'run/journal.ndjson').read_text(encoding='utf-8').splitlines()[0])
            self.assertEqual(event['payload']['environment']['external_tools'],[
                {'name':'primer3_core','version':'2.6.1','sha256':'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'}])
            self.assertNotIn(str(program),json.dumps(event));launch.assert_called_once()

    def test_no_configuration_records_empty_tools_without_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict('os.environ',{},clear=True),patch('dna_design_core.application.run_service.platform.system',return_value='synthetic platform'),patch('dna_design_core.application.config.shutil.which',return_value=None),patch('dna_design_core.engine.invoker.subprocess.run') as launch:
                created=api.call('run create',directory=Path(folder)/'run')
            self.assertEqual(created['problems'],[],created)
            event=json.loads((Path(folder)/'run/journal.ndjson').read_text(encoding='utf-8').splitlines()[0])
            self.assertEqual(event['payload']['environment']['external_tools'],[]);launch.assert_not_called()


if __name__=='__main__':unittest.main()
