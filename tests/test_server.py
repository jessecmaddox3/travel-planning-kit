import http.client,json,threading,unittest
from travel_kit.server import make_server
from travel_kit.cli import SAMPLE

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=make_server(SAMPLE);cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.port=cls.server.server_address[1];cls.origin=f'http://127.0.0.1:{cls.port}'
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join()
    def request(self,path='/',method='GET',body=None,headers=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5);conn.request(method,path,body,headers or {});r=conn.getresponse();data=r.read();status=r.status;conn.close();return status,data
    def bootstrap(self):return json.loads(self.request('/bootstrap')[1])
    def post(self,path,payload,**overrides):
        headers={'Content-Type':'application/json','Origin':self.origin,'X-Travel-Token':self.bootstrap()['token']};headers.update(overrides)
        return self.request(path,'POST',json.dumps(payload),headers)
    def test_normal_render_and_import_preserve_document(self):
        doc=self.bootstrap()['document'];doc['trip']['title']='Synthetic editor test'
        status,data=self.post('/render',{'kind':'plan','document':doc});self.assertEqual(status,200);self.assertIn('Synthetic editor test',json.loads(data)['html'])
        status,data=self.post('/validate',{'source':json.dumps(doc)});self.assertEqual(status,200);self.assertEqual(json.loads(data)['document'],doc)
    def test_foreign_origin_host_missing_token_and_file_paths_are_rejected(self):
        self.assertEqual(self.request(headers={'Host':'attacker.example'})[0],403)
        self.assertEqual(self.post('/validate',{'source':'{}'},Origin='https://attacker.example')[0],403)
        self.assertEqual(self.post('/validate',{'source':'{}'},**{'X-Travel-Token':''})[0],403)
        for path in ['/../README.md','/example/cedar-bay.json','/etc/passwd']:
            self.assertEqual(self.request(path)[0],404)
    def test_invalid_import_and_render_do_not_change_starting_state(self):
        original=self.bootstrap()['document']
        self.assertEqual(self.post('/validate',{'source':'{"formatVersion":1,"formatVersion":2}'})[0],400)
        self.assertEqual(self.post('/render',{'kind':'other','document':original})[0],400)
        self.assertEqual(self.bootstrap()['document'],original)

if __name__=='__main__':unittest.main()
