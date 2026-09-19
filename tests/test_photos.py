import io,json,tempfile,unittest
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError
from travel_kit.photos import extract_photos,fetch_csv,apply_photos
from travel_kit.files import read_document
from travel_kit.cli import SAMPLE
from travel_kit.model import ValidationError

class Response(io.BytesIO):
    headers={'Content-Type':'text/html; charset=utf-8'}
    def geturl(self):return 'https://example.invalid/listing'

class PhotoTests(unittest.TestCase):
    def test_apply_fetched_results_to_trip_preserves_other_fields_and_checks_ids(self):
        doc=read_document(SAMPLE);house=doc['rentals']['houses'][0];data={'formatVersion':1,'listings':{house['id']:{'url':'https://example.invalid/one','title':'Listing','photos':['https://images.example.invalid/one.jpg']}}}
        merged=apply_photos(doc,data)
        self.assertEqual(merged['plan'],doc['plan']);self.assertEqual(len(merged['rentals']['houses'][0]['photos']),len(house['photos'])+1)
        self.assertEqual(len(apply_photos(merged,data)['rentals']['houses'][0]['photos']),len(house['photos'])+1)
        self.assertEqual(len(apply_photos(doc,data,replace=True)['rentals']['houses'][0]['photos']),1)
        data['listings']['unknown']=data['listings'].pop(house['id'])
        with self.assertRaises(ValidationError):apply_photos(doc,data)
    def test_provider_photos_take_priority_over_icons_and_need_no_extension(self):
        icons=''.join(f'<img src="https://assets.example.invalid/icon-{i}.png">' for i in range(24))
        result=extract_photos(icons+'<script>"https://a0.muscache.com/im/pictures/synthetic-photo?width=1000"</script>')
        self.assertEqual(result['photos'],['https://a0.muscache.com/im/pictures/synthetic-photo?width=1000'])
    def test_css_url_delimiters_are_not_part_of_provider_photo(self):
        result=extract_photos('<style>.hero{background-image:url(https://a0.muscache.com/im/pictures/fictional-house.jpg)}</style>')
        self.assertEqual(result['photos'],['https://a0.muscache.com/im/pictures/fictional-house.jpg'])
    def test_metadata_and_embedded_photo_urls_are_deduplicated(self):
        result=extract_photos('<title>Blue &amp; green</title><meta property="og:image" content="https://images.example.invalid/a.jpg"><script>{"image":"https:\\/\\/images.example.invalid\\/a.jpg","extra":"https://images.example.invalid/b.webp"}</script>')
        self.assertEqual(result['title'],'Blue & green');self.assertEqual(len(result['photos']),2)
    def test_partial_failure_preserves_existing_records_and_all_failure_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);csv=root/'listings.csv';out=root/'photos.json'
            old={'formatVersion':1,'listings':{'failed':{'url':'https://example.invalid/old','title':'Keep me','photos':['https://images.example.invalid/old.jpg']}}}
            out.write_text(json.dumps(old));csv.write_text('id,url\nfailed,https://example.invalid/fail\nsuccess,https://example.invalid/ok\n')
            def opener(req,timeout):
                if req.full_url.endswith('/fail'):raise HTTPError(req.full_url,403,'Denied',{},None)
                return Response(b'<meta property="og:image" content="https://images.example.invalid/new.jpg">')
            report=fetch_csv(csv,out,update=True,opener=opener);saved=json.loads(out.read_text())
            self.assertEqual(report['updated'],1);self.assertEqual(len(report['errors']),1);self.assertEqual(saved['listings']['failed'],old['listings']['failed'])
            before=out.read_bytes();csv.write_text('id,url\nfailed,https://example.invalid/fail\n')
            report=fetch_csv(csv,out,update=True,opener=opener);self.assertEqual(report['updated'],0);self.assertEqual(out.read_bytes(),before)
    def test_invalid_csv_and_existing_output_never_start_network(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);csv=root/'listings.csv';out=root/'photos.json';calls=[]
            csv.write_text('id,url\nbad,file:///tmp/local.png\n')
            with self.assertRaises(ValidationError):fetch_csv(csv,out,opener=lambda *a,**k:calls.append(a))
            csv.write_text('id,url\ngood,https://example.invalid/a\n');out.write_text('{}')
            with self.assertRaises(FileExistsError):fetch_csv(csv,out,opener=lambda *a,**k:calls.append(a))
            self.assertEqual(calls,[])
    def test_incomplete_http_response_is_reported_without_losing_successes(self):
        class Broken(Response):
            def read(self,*args):raise IncompleteRead(b'partial',100)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);csv=root/'listings.csv';out=root/'photos.json';csv.write_text('id,url\none,https://example.invalid/one\ntwo,https://example.invalid/two\n')
            result=fetch_csv(csv,out,opener=lambda req,timeout:Broken(b'') if req.full_url.endswith('two') else Response(b'<meta property="og:image" content="https://images.example.invalid/one.jpg">'))
            self.assertEqual(result['updated'],1);self.assertEqual(len(result['errors']),1);self.assertIn('one',json.loads(out.read_text())['listings'])

if __name__=='__main__':unittest.main()
