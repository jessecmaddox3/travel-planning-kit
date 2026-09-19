"""The offline demonstration has no network calls and uses only invented inputs."""
from pathlib import Path
import os
import shutil
import tempfile
from .files import read_document,write_file
from .cli import SAMPLE,render
from .render import wrap


def make_demo(destination):
    destination=Path(destination)
    if destination.exists():raise FileExistsError('The demo folder already exists. Choose a new empty destination name.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.'+destination.name+'-',dir=destination.parent))
    try:
        doc=read_document(SAMPLE)
        labels={'packing':'Printable packing list','plan':'Trip planning dossier','compare':'Rental photo gallery','table':'Full 22-column rental comparison'}
        for name in labels:write_file(temp/(name+'.html'),render(name,doc,SAMPLE.parent))
        body='<main><h1>Travel Planning Kit</h1><div class="tldr"><strong>Start here</strong><p>Four complete examples from one invented trip. Open a page, explore it, or print it. These files work offline.</p></div><ul>'+''.join('<li><a href="'+name+'.html">'+label+'</a></li>' for name,label in labels.items())+'</ul><h2>Make a trip of your own</h2><p>The source download includes a local browser editor, reusable JSON and research templates. Follow the README to start it. No cloud account or AI subscription is required.</p><p>All people, destinations, prices and properties here are fictional. Sample images are AI illustrations.</p><p>I built this for me and my personal use. Make it your own, and feel free to improve mine. Hopefully it gives you a useful starting point, or at the very least some ideas. Cheers!</p></main>'
        write_file(temp/'Start.html',wrap('Travel Planning Kit: start here',body))
        write_file(temp/'LICENSE.txt',(Path(__file__).parent/'demo-license.txt').read_text())
        write_file(temp/'ASSETS.txt','Travel Planning Kit fictional examples\n\nThe trip, locations, prices and properties are invented. The cottage and cabin images were generated with ChatGPT for this kit, without real-trip reference images. They are illustrations, not real rental listings. The author makes the generated outputs available under the kit\'s permissive terms to the extent the author can grant them, with no claim of exclusive rights. See LICENSE.txt. Source and retained prompts: https://github.com/jessecmaddox3/travel-planning-kit\n')
        os.rename(temp,destination)
    finally:
        if temp.exists():shutil.rmtree(temp)
