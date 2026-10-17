"""RFC 8785 probe for an already installed rfc8785 library. Never installs it."""
import importlib.util
import importlib.metadata
import json
import platform
from pathlib import Path


def main():
    report={'environment':{'python':platform.python_version(),'os':platform.platform()},'library':'rfc8785','candidate_version':'0.1.4','version':None,'status':'not_executed','vectors':[],
            'linux':'not_executed: no Linux environment configured','license':'Apache-2.0; official source in FACTS.md'}
    if importlib.util.find_spec('rfc8785') is None:
        report['reason']='Selected implementation is not installed; task forbids downloading/installing it.'
    else:
        import rfc8785
        report['version']=importlib.metadata.version('rfc8785')
        # RFC 8785 section 3.2.3: code-unit sorting, including a surrogate pair.
        keys=['\u20ac','\r','\ufb33','1','\U0001f600','\u0080','\u00f6']
        data={key:index for index,key in enumerate(keys)}
        expected='{"\\r":1,"1":3,"\u0080":5,"\u00f6":6,"\u20ac":0,"\U0001f600":4,"\ufb33":2}'.encode('utf-8')
        number_data={'numbers':[333333333.33333329,1e30,4.50,2e-3,1e-27]}
        number_expected=b'{"numbers":[333333333.3333333,1e+30,4.5,0.002,1e-27]}'
        # Floating-point vector tests RFC conformance only, never product data permission.
        for name,value,answer in [('utf16_sort',data,expected),('rfc_numbers',number_data,number_expected),('controls',{'x':'\b\t\n\f\r"\\'},b'{"x":"\\b\\t\\n\\f\\r\\"\\\\"}')]:
            output=rfc8785.dumps(value)
            report['vectors'].append({'name':name,'passed':output==answer,'actual_hex':output.hex(),'expected_hex':answer.hex()})
        report['status']='passed' if all(v['passed'] for v in report['vectors']) else 'failed'
    output=Path('probes/runs/p3.json');output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))
    return 0 if report['status']=='passed' else 2


if __name__=='__main__': raise SystemExit(main())
