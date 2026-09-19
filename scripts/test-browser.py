"""Real offline and editor workflows with only the invented bundled trip."""
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[1]
if not os.environ.get('TRAVEL_INSTALLED'):sys.path.insert(0,str(ROOT))
from travel_kit.cli import SAMPLE
from travel_kit.demo import make_demo
from travel_kit.server import make_server


def main():
    with tempfile.TemporaryDirectory(prefix='travel-browser-') as temporary:
        output=Path(temporary);demo=output/'demo';make_demo(demo)
        server=make_server(SAMPLE);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        origin='http://127.0.0.1:'+str(server.server_address[1])
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch();context=browser.new_context(accept_downloads=True);page=context.new_page();external=[];errors=[]
                def route(request):
                    url=request.request.url
                    if url.startswith(('http:','https:')) and not url.startswith(origin+'/'):
                        external.append(url);request.abort()
                    else:request.continue_()
                context.route('**/*',route);page.on('pageerror',lambda error:errors.append(str(error)));page.on('dialog',lambda dialog:dialog.accept())
                page.goto(origin);expect(page.get_by_label('Trip name',exact=True)).to_have_value('Cedar Bay Weekender')
                page.get_by_label('Trip name',exact=True).fill('Synthetic browser trip')
                page.get_by_role('button',name='Update preview',exact=True).click()
                expect(page.frame_locator('#frame').locator('h1')).to_contain_text('Synthetic browser trip')
                page.get_by_role('button',name='Places to stay',exact=True).click()
                property_card=page.locator('details').filter(has=page.locator('summary',has_text='Blue Shutter Cottage')).first
                property_card.locator('summary').first.click()
                property_card.get_by_label('Property notes',exact=True).fill('Synthetic field changed in browser')
                property_card.get_by_label('Exact stay total (exact quotes only)',exact=True).fill('1843.27')
                page.get_by_role('button',name='The plan',exact=True).click()
                page.get_by_label('At a glance',exact=True).fill('A fully fictional browser check.')
                with page.expect_download() as item:page.get_by_role('button',name='Save my trip',exact=True).click()
                saved=output/'saved.json';item.value.save_as(saved);doc=json.loads(saved.read_text())
                assert doc['rentals']['houses'][0]['quote']['amount']=='1843.27'
                assert doc['rentals']['houses'][0]['notes']=='Synthetic field changed in browser'
                original=json.loads(SAMPLE.read_text());assert doc['catalog']==original['catalog'];assert doc['plan']['preferences']==original['plan']['preferences']
                bad=output/'bad.json';bad.write_text('{"formatVersion":99}')
                page.locator('#import').set_input_files(bad);expect(page.locator('#message')).to_contain_text('current draft is unchanged')
                page.get_by_role('button',name='The trip',exact=True).click();expect(page.get_by_label('Trip name',exact=True)).to_have_value('Synthetic browser trip')
                page.get_by_label('Departure',exact=True).fill('2034-09-01');page.get_by_role('button',name='Update preview',exact=True).click();expect(page.locator('#message')).to_contain_text('Departure must follow')
                expect(page.frame_locator('#frame').locator('h1')).to_contain_text('Synthetic browser trip')
                page.get_by_label('Departure',exact=True).fill(original['trip']['end'])
                for kind in ['packing','plan','compare','table']:
                    page.locator('#kind').select_option(kind)
                    with page.expect_download() as item:page.get_by_role('button',name='Download HTML',exact=True).click()
                    destination=output/(kind+'.html');item.value.save_as(destination)
                    assert 'Synthetic browser trip' in destination.read_text()
                page.locator('#import').set_input_files(saved);expect(page.locator('#message')).to_contain_text('Trip opened')
                for width in [320,390,768,1440]:
                    page.set_viewport_size({'width':width,'height':900})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'Editor overflow at {width}'
                    if os.environ.get('TRAVEL_SCREENSHOTS'):
                        shots=Path(os.environ['TRAVEL_SCREENSHOTS']);shots.mkdir(parents=True,exist_ok=True);page.screenshot(path=str(shots/f'editor-{width}.png'),full_page=True)
                page.get_by_role('button',name='Start a new trip',exact=True).click();expect(page.get_by_label('Trip name',exact=True)).to_have_value('My trip');expect(page.get_by_label('Arrival',exact=True)).to_have_value('')
                for kind in ['packing','plan','compare','table']:
                    page.goto((demo/(kind+'.html')).as_uri());page.wait_for_load_state('load')
                    for width in [390,1440]:
                        page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'{kind} overflow at {width}'
                    assert page.locator('h1').count()==1
                    if os.environ.get('TRAVEL_SCREENSHOTS'):
                        page.screenshot(path=str(shots/f'{kind}-1440.png'),full_page=True)
                        page.pdf(path=str(shots/f'{kind}.pdf'),format='Letter',print_background=True,prefer_css_page_size=True,landscape=kind=='table')
                assert not external,f'Unexpected external requests: {external}'
                assert not errors,f'Browser errors: {errors}'
                browser.close()
                print('PASS: editor changes/save/import/error recovery, four HTML downloads, responsive and offline workflows; zero external requests or script errors.')
        finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':main()
