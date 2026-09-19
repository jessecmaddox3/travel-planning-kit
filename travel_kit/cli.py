"""Command line entry point. No network or files are touched on import."""
import argparse
import json
from pathlib import Path
import sys
from .files import read_document,write_file
from .model import ValidationError
from .render import render_packing,render_plan,render_comparison,render_table

SAMPLE=Path(__file__).parent/'example'/'cedar-bay.json'
RENDERERS={'packing':render_packing,'plan':render_plan,'compare':render_comparison,'table':render_table}


def render(kind,document,asset_root,remote_images=False):
    if kind not in RENDERERS:raise ValidationError('Choose packing, plan, compare or table.')
    return RENDERERS[kind](document,asset_root,remote_images=remote_images) if kind=='compare' else RENDERERS[kind](document)


def main(argv=None):
    parser=argparse.ArgumentParser(description='Pack, plan and compare places to stay. Your data stays local.')
    commands=parser.add_subparsers(dest='command',required=True)
    for command in RENDERERS:
        p=commands.add_parser(command);p.add_argument('--config',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--overwrite',action='store_true')
        if command=='compare':p.add_argument('--remote-images',action='store_true',help='Explicitly allow supplied HTTP(S) photos to load when someone opens this output.')
    p=commands.add_parser('demo',help='Create four ready-to-open fictional sample documents.');p.add_argument('--output',type=Path,required=True)
    p=commands.add_parser('start',help='Open the local browser editor.');p.add_argument('--config',type=Path,default=SAMPLE);p.add_argument('--port',type=int,default=0);p.add_argument('--no-browser',action='store_true')
    p=commands.add_parser('fetch-photos',help='Explicit network action: collect public photo URLs from your CSV.');p.add_argument('--csv',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--update',action='store_true')
    p=commands.add_parser('apply-photos',help='Merge a fetched photo collection into a new editable trip file.');p.add_argument('--config',type=Path,required=True);p.add_argument('--photos',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--replace',action='store_true',help='Replace photos for matching properties instead of appending.');p.add_argument('--overwrite',action='store_true')
    args=parser.parse_args(argv)
    try:
        if args.command in RENDERERS:
            document=read_document(args.config);html=render(args.command,document,args.config.resolve().parent,getattr(args,'remote_images',False));write_file(args.output,html,args.overwrite);print('Created '+str(args.output));return 0
        if args.command=='demo':
            from .demo import make_demo
            make_demo(args.output);print('Created '+str(args.output/'Start.html')+'. Open this file in your browser.');return 0
        if args.command=='start':
            from .server import serve
            serve(args.config,args.port,open_browser=not args.no_browser);return 0
        if args.command=='apply-photos':
            from .photos import read_previous,apply_photos
            result=apply_photos(read_document(args.config),read_previous(args.photos),args.replace)
            write_file(args.output,json.dumps(result,indent=2,ensure_ascii=False)+'\n',args.overwrite)
            print('Created '+str(args.output)+'. Keep it beside the original configuration so relative local photos still resolve.');return 0
        if args.command=='fetch-photos':
            from .photos import fetch_csv
            result=fetch_csv(args.csv,args.output,update=args.update)
            print(f'{result["updated"]} listings updated; {len(result["errors"])} failures. Previous photo records for failed listings were preserved.')
            for error in result['errors']:print(error['id']+': '+error['message'],file=sys.stderr)
            return 1 if result['errors'] else 0
    except (ValidationError,OSError,UnicodeError) as error:
        print('Could not finish: '+str(error),file=sys.stderr);return 2
    return 0
