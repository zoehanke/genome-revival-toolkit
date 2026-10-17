import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
from e2e.run_examples import run_examples,GUARD


class EndToEndTests(unittest.TestCase):
    def test_public_cli_examples_and_portable_seals(self):
        with tempfile.TemporaryDirectory() as d:
            summary=run_examples(Path(d)/'examples')
            self.assertEqual(summary['connection_attempts'],0)
            self.assertTrue(summary['cases']['b1']['verified']);self.assertTrue(summary['cases']['b3']['verified'])
            self.assertEqual(summary['cases']['b1']['expected'],{'sequence':'TTCTGACT'})
            self.assertEqual(summary['cases']['b3']['expected'],{'difference':5})

    def test_network_guard_detects_its_deliberate_control(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'attempts.json'
            result=subprocess.run([sys.executable,'-X','utf8','-B',str(GUARD),str(path),'probe'],capture_output=True,text=True,encoding='utf-8')
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(json.loads(path.read_text(encoding='utf-8'))['attempts'],1)


if __name__=='__main__':unittest.main()
