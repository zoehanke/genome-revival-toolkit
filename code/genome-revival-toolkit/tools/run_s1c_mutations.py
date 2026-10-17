"""One deliberate comparison mutation per S1c check on disposable copies."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
MUTATIONS={
    'postcall':('src/dna_design_core/engine/invoker.py',
        'if observer.violations:',
        'if False and observer.violations:',
        'tests.integration.test_postcall_io.PostCallIOTests.test_new_file_outside_workdir_is_detected_after_it_was_written'),
    'quality':('src/dna_design_core/capabilities/primer_assessment.py',
        "'FAIL' if differences else 'UNKNOWN' if unknown else 'PASS'",
        "'UNKNOWN' if unknown else 'PASS'",
        'tests.integration.test_s1c_primer_quality.AutomaticPrimerQualityTests.test_recorded_length_passes_but_document_core_length_tamper_fails'),
    'order':('src/dna_design_core/capabilities/builtin/check/preparation.py',
        "'FAIL' if differences else 'UNKNOWN' if unknown else 'PASS'",
        "'UNKNOWN' if unknown else 'PASS'",
        'tests.integration.test_s1c_orders.OrderTableTests.test_full_primers_match_but_changed_5prime_tail_fails'),
    'reaction':('src/dna_design_core/capabilities/reactions.py',
        "fields=[k for k in expected if expected[k]!=actual[k]]",
        "fields=[]",
        'tests.integration.test_s1c_reactions.ReactionChainTests.test_original_route_passes_but_one_base_candidate_fails_both_checks'),
    'sanity':('src/dna_design_core/capabilities/builtin/check/content.py',
        "'FAIL' if findings else 'PASS' if rows else 'NOT_APPLICABLE'",
        "'PASS' if rows else 'NOT_APPLICABLE'",
        'tests.integration.test_s1c_sanity.BiologicalSanityTests.test_circular_no_ends_passes_but_circular_linear_ends_fail'),
    'cds':('src/dna_design_core/biology/analyzers/content.py',
        "if report['internal_stop_count']:codes.append('INTERNAL_STOP')",
        "if False:codes.append('INTERNAL_STOP')",
        'tests.integration.test_s1c_cds.CDSValidityTests.test_complete_cds_and_introduced_internal_stop_have_opposite_verdicts'),
    'annotation':('src/dna_design_core/biology/analyzers/content.py',
        "if part.get('strand') not in (None,-1,0,1):codes.append('INVALID_STRAND')",
        "if False:codes.append('INVALID_STRAND')",
        'tests.integration.test_s1c_content.AnnotationIntegrityTests.test_legal_and_introduced_bad_strand_have_opposite_verdicts'),
}


def run(name,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    relative,before,after,test=MUTATIONS[name]
    baseline=subprocess.run([sys.executable,'-X','utf8','-B','-m','unittest',test,'-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    (output/'baseline.txt').write_text(baseline.stdout+baseline.stderr,encoding='utf-8')
    assert baseline.returncode==0,baseline.stdout+baseline.stderr
    with tempfile.TemporaryDirectory(prefix='s1c_mutation_') as folder:
        copied=Path(folder)/'tree'
        shutil.copytree(ROOT,copied,ignore=shutil.ignore_patterns('.venv','dist','build','__pycache__','runs','*.egg-info','evidence'))
        path=copied/relative;text=path.read_text(encoding='utf-8');assert text.count(before)==1
        path.write_text(text.replace(before,after),encoding='utf-8',newline='\n')
        result=subprocess.run([sys.executable,'-X','utf8','-B','-m','unittest',test,'-v'],cwd=copied,capture_output=True,text=True,encoding='utf-8')
        transcript=(result.stdout+result.stderr).replace(str(copied),'<copied-tree>').replace(str(Path.home()),'<home>')
        (output/'mutant.txt').write_text(transcript,encoding='utf-8')
        summary={'check':name,'test':test,'mutation':[before,after],'baseline_exit':baseline.returncode,
                 'mutant_exit':result.returncode,'detected':result.returncode!=0 and 'AssertionError' in transcript and 'FAILED (failures=' in transcript}
        (output/'RESULTS.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',choices=list(MUTATIONS),required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();result=run(args.case,args.out);print(json.dumps(result,indent=2));raise SystemExit(not result['detected'])
