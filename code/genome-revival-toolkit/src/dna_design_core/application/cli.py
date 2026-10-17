"""The single grt CLI; invoke this file directly in an uninstalled development tree."""
import argparse
import json
from pathlib import Path
import sys

if __package__ in {None,''}:
    # A direct execution of this same entry needs no installation or PYTHONPATH.
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from dna_design_core.application.api import call
from dna_design_core.kernel import canonical
from dna_design_core.kernel.errors import ToolkitError


class Parser(argparse.ArgumentParser):
    def error(self,message):
        raise ToolkitError('PLAN_PARAM_INVALID','Invalid command or arguments. Use describe or --help.')


def parser():
    common=Parser(add_help=False)
    common.add_argument('--run',type=Path);common.add_argument('--kit-dir',action='append',default=[],type=Path)
    common.add_argument('--config',type=Path);common.add_argument('--format',choices=['json','text'],default='json')
    common.add_argument('--lang')
    root=Parser(prog='grt');commands=root.add_subparsers(dest='group',required=True)
    def group(name,commands_for_group):
        group_parser=commands.add_parser(name)
        children=group_parser.add_subparsers(dest='action',required=True)
        for command,configure in commands_for_group:
            selected=children.add_parser(command,parents=[common]);selected.set_defaults(verb=name+' '+command);configure(selected)
    def request(p):p.add_argument('--request',required=True,type=Path)
    group('run',[('create',lambda p:p.add_argument('directory',type=Path)),('execute',lambda p:p.add_argument('--until')),('abandon',lambda p:p.add_argument('--reason'))])
    group('goal',[('declare',request),('amend',request)])
    group('pipeline',[('submit',request),('revise',request)])
    group('template',[('instantiate',lambda p:(p.add_argument('name'),request(p)))])
    group('record',[('render',lambda p:p.add_argument('--level',choices=['brief','standard','full'],default='standard'))])
    group('review',[('sign',request)])
    p=commands.add_parser('describe',parents=[common]);p.set_defaults(verb='describe')
    p.add_argument('kind',nargs='?',default='capabilities',choices=['capabilities','capability','templates','template','checks','goal-kinds','kits','vocab']);p.add_argument('name',nargs='?')
    for name in ['declare','status','judge','seal','verify','doctor']:
        p=commands.add_parser(name,parents=[common]);p.set_defaults(verb=name)
        if name=='declare':request(p)
        if name in {'judge','seal'}:p.add_argument('--also',action='append',default=[])
        if name=='verify':p.add_argument('directory',type=Path)
    return root


def main(argv=None):
    output_format='json'
    try:
        args=vars(parser().parse_args(argv));output_format=args.pop('format')
        verb=args.pop('verb');args.pop('group');args.pop('action',None)
        request_path=args.pop('request',None);request=canonical.loads(request_path.read_bytes()) if request_path else None
        receipt=call(verb,root=args.pop('run'),request=request,kit_dirs=args.pop('kit_dir'),config_path=args.pop('config'),**args)
        code=1 if receipt['problems'] else 10 if verb=='seal' and not receipt['result'].get('sealed') else 1 if verb=='verify' and not receipt['result'].get('verified') else 0
    except Exception as error:
        if isinstance(error,ToolkitError):problem=error.problem
        elif isinstance(error,(OSError,ValueError)):problem=ToolkitError('PLAN_INPUT_UNBOUND','Request could not be read.',{'type':type(error).__name__}).problem
        else:problem=ToolkitError('CAPABILITY_INTERNAL','Unexpected command failure.',{'type':type(error).__name__}).problem
        value=problem.as_dict()
        receipt={'run_id':None,'state':None,'event_range':None,'result':{'failure':value},
                 'problems':[{key:value[key] for key in ['code','category','message','recovery']}|{'location':''}],'next':['describe'],'labels':[]}
        code=1
    if output_format=='json':print(json.dumps(receipt,ensure_ascii=False,separators=(',',':')))
    else:
        print('Run: '+str(receipt['run_id'])+'; state: '+str(receipt['state']))
        print(json.dumps(receipt['result'],ensure_ascii=False,indent=2))
        for problem in receipt['problems']:print(problem['code']+': '+problem['message'])
    return code


if __name__=='__main__':raise SystemExit(main())
