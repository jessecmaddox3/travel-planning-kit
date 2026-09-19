from pathlib import Path
import copy,json,tempfile,unittest
from travel_kit.schema import loads_document,validate_document
from travel_kit.model import ValidationError
from travel_kit.render import render_packing,render_plan,render_comparison,render_table,COMPARISON_COLUMNS

ROOT=Path(__file__).resolve().parents[1]

def example():return loads_document((ROOT/'travel_kit/example/cedar-bay.json').read_text())

class SchemaTests(unittest.TestCase):
    def test_roundtrip_preserves_every_supported_field(self):
        doc=example();out=validate_document(doc);self.assertEqual(doc,out);out['plan']['preferences'][0]['answer']='Changed';self.assertNotEqual(out,doc)
    def test_incompatible_or_ambiguous_import_is_rejected(self):
        for mutate in [lambda d:d.update(formatVersion=2),lambda d:d.update(formatVersion=True),lambda d:d['trip'].update(secretExtra='unused'),lambda d:d['catalog']['categories'][0].update(column=True),lambda d:d['catalog']['items'][0].update(category='missing')]:
            d=example();mutate(d)
            with self.assertRaises(ValidationError):validate_document(d)
        with self.assertRaises(ValidationError):loads_document('{"formatVersion":1,"formatVersion":2}')
        with self.assertRaises(ValidationError):loads_document('{"formatVersion":NaN}')

class RenderTests(unittest.TestCase):
    def test_all_four_documents_preserve_full_workflows(self):
        d=example();packing=render_packing(d);plan=render_plan(d);gallery=render_comparison(d,ROOT/'travel_kit/example');table=render_table(d)
        self.assertIn('Morning of departure',packing);self.assertIn('packing-columns',packing);self.assertIn('@page',packing)
        self.assertIn('Preferences and questionnaire',plan);self.assertIn('Open decisions',plan);self.assertIn('After the trip',plan)
        self.assertIn('Also worth considering',gallery);self.assertIn('Checked and ruled out',gallery);self.assertIn('Photos not supplied',gallery);self.assertIn('data:image/png;base64,',gallery)
        self.assertEqual(len(COMPARISON_COLUMNS),22)
        for _,label in COMPARISON_COLUMNS:self.assertIn(label,table)
        self.assertTrue('921.62' in gallery and '921.63' in gallery, 'Exact split must allocate the final cent.')
        for html in [packing,plan,gallery,table]:
            self.assertNotIn('<script src="http',html);self.assertNotIn('<img src="http',html);self.assertNotIn('fonts.googleapis.com',html)
    def test_user_text_is_never_markup(self):
        d=example();payload='<script>alert("fictional")</script>';d['trip']['title']=payload;d['catalog']['items'][0]['label']=payload;d['plan']['summary']=payload;d['rentals']['houses'][0]['name']=payload
        for html in [render_packing(d),render_plan(d),render_comparison(d,ROOT/'travel_kit/example'),render_table(d)]:
            self.assertNotIn(payload,html);self.assertIn('&lt;script&gt;',html)
    def test_photo_paths_cannot_escape_the_explicit_example_root(self):
        d=example()
        for path in ['../outside.png','/tmp/outside.png','file:///tmp/outside.png','javascript:alert(1)']:
            d['rentals']['houses'][0]['photos'][0]['src']=path
            with self.subTest(path=path),self.assertRaises(ValidationError):render_comparison(d,ROOT/'travel_kit/example')
    def test_external_photo_is_a_link_until_explicitly_enabled(self):
        d=example();d['rentals']['houses'][0]['photos']=[{'src':'https://images.example.invalid/sample.jpg','alt':'Supplied image'}]
        html=render_comparison(d,ROOT/'travel_kit/example');self.assertNotIn('<img src="https://',html);self.assertIn('https://images.example.invalid/sample.jpg',html)
        html=render_comparison(d,ROOT/'travel_kit/example',remote_images=True);self.assertIn('<img src="https://images.example.invalid/sample.jpg',html)
    def test_quoted_dates_and_check_date_remain_visible_when_different(self):
        d=example();q=d['rentals']['houses'][0]['quote'];q.update(stayStart='2034-09-08',stayEnd='2034-09-09',checked='2034-07-13')
        for html in [render_comparison(d,ROOT/'travel_kit/example'),render_table(d)]:
            self.assertTrue('2034-09-08 to 2034-09-09 (1 night)' in html)
            self.assertTrue('quoted dates differ from this trip' in html)
            self.assertTrue('Quote checked: 2034-07-13' in html)
    def test_unknown_price_and_empty_shortlist_do_not_crash(self):
        d=example()
        for h in d['rentals']['houses']:h['tier']='alternative';h['photos']=[];h['quote']={'kind':'unknown','currency':'USD'}
        html=render_comparison(d,ROOT/'travel_kit/example');self.assertIn('No shortlist yet',html);self.assertIn('Price not supplied',html)
    def test_alternative_preserves_listing_caveats_and_property_details(self):
        d=example();h=d['rentals']['houses'][2]
        h.update(url='https://listings.example.invalid/orchard',amenities=['Covered bike storage'],cancellation='Refund rules pending',notes='Ask about stairs')
        h['quote'].update(scope='Cleaning fee excluded',note='Confirm taxes')
        html=render_comparison(d,ROOT/'travel_kit/example')
        for text in ['https://listings.example.invalid/orchard','Covered bike storage','Refund rules pending','Ask about stairs','Cleaning fee excluded','Confirm taxes']:
            self.assertTrue(text in html,text)
    def test_optional_hero_uses_safe_local_embedding(self):
        d=example();d['rentals']['hero']={'src':'images/fictional-cottage.png','alt':'Invented coastal cottage','credit':'Generated illustration'}
        html=render_comparison(d,ROOT/'travel_kit/example')
        self.assertTrue('class="hero-image"' in html and 'Invented coastal cottage' in html)
        d['rentals']['hero']['src']='../outside.png'
        with self.assertRaises(ValidationError):render_comparison(d,ROOT/'travel_kit/example')

if __name__=='__main__':unittest.main()
