"""Public development probe command; never imports runtime or old source."""
import argparse
import json
from pathlib import Path
from sequence_sample import reverse_complement, scan_linear_pam
from tm_sample import tm_nn


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('spikes/runs/samples.json'))
    args=parser.parse_args()
    result={'kind':'SYNTHETIC_MIGRATION_SAMPLE','reverse_complement':reverse_complement('AGTCAGAA'),
            'pam_hits':scan_linear_pam('A'*20+'AGG'+'T'*5,'NGG',20),
            'tm':{'method':'Biopython DNA_NN3, saltcorr 5, non-self-complementary','Na_mM':50,'dnac1_nM':250,'dnac2_nM':0,'Mg_mM':0,'dNTP_mM':0,
                  'A10_C':str(tm_nn('A'*10,sodium_mm=50,primer_nm=250)),'C10_C':str(tm_nn('C'*10,sodium_mm=50,primer_nm=250))},
            'not_done':['Circular candidates','Material annotation transfer','Primer quality','Wet experiments','Old-code acceptance','Runtime integration']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
