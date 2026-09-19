"""Loopback-only editor. It reads one explicit configuration and never writes it."""
from functools import partial
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import webbrowser
from .cli import render
from .files import read_document
from .model import ValidationError
from .schema import loads_document

ASSETS=Path(__file__).parent
STATIC={'/':('editor.html','text/html'),'/editor.js':('editor.js','text/javascript'),'/editor.css':('editor.css','text/css')}


class EditorHandler(BaseHTTPRequestHandler):
    server_version='TravelPlanningKit'
    def log_message(self,*args):pass
    def reply(self,status,body,kind='application/json'):
        data=body.encode('utf-8') if isinstance(body,str) else body
        self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-src 'self' about:; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.send_header('X-Frame-Options','DENY');self.end_headers();self.wfile.write(data)
    def error(self,status,message):self.reply(status,json.dumps({'error':message}))
    def allowed(self,post=False):
        host='127.0.0.1:'+str(self.server.server_address[1])
        if self.headers.get('Host')!=host or self.headers.get('Sec-Fetch-Site')=='cross-site':return False
        if post:
            return self.headers.get('Origin')=='http://'+host and secrets.compare_digest(self.headers.get('X-Travel-Token',''),self.server.editor_token)
        return True
    def do_GET(self):
        if not self.allowed():return self.error(403,'Open the editor using its printed local address.')
        if self.path=='/bootstrap':return self.reply(200,json.dumps({'document':self.server.document,'token':self.server.editor_token}))
        if self.path not in STATIC:return self.error(404,'Page not found.')
        name,kind=STATIC[self.path];self.reply(200,(ASSETS/name).read_bytes(),kind)
    def do_POST(self):
        if not self.allowed(post=True):return self.error(403,'This request did not come from this editor session.')
        if self.path not in {'/validate','/render'}:return self.error(404,'Action not found.')
        if self.headers.get('Content-Type')!='application/json' or self.headers.get('Transfer-Encoding'):return self.error(415,'Use an ordinary JSON request.')
        try:length=int(self.headers.get('Content-Length',''))
        except ValueError:return self.error(400,'A request length is required.')
        if not 0<length<=2_100_000:return self.error(413,'Choose a document smaller than 2 MB.')
        self.connection.settimeout(10)
        try:
            raw=self.rfile.read(length)
            if len(raw)!=length:raise ValidationError('The request ended before the document was received.')
            payload=json.loads(raw)
            if not isinstance(payload,dict):raise ValidationError('Use a document object.')
            if self.path=='/validate':
                if set(payload)!={'source'}:raise ValidationError('Choose one JSON source document.')
                result={'document':loads_document(payload['source'])}
            else:
                if set(payload)!={'kind','document'}:raise ValidationError('Choose a document and one output type.')
                document=loads_document(json.dumps(payload['document'],allow_nan=False))
                if not isinstance(payload['kind'],str):raise ValidationError('Choose an output type.')
                result={'html':render(payload['kind'],document,self.server.asset_root)}
            self.reply(200,json.dumps(result))
        except (ValidationError,ValueError,TypeError,RecursionError,OSError,UnicodeError) as error:self.error(400,str(error))


def make_server(config,port=0):
    if type(port) is not int or not 0<=port<=65535:raise ValidationError('Use a port from 0 to 65535.')
    document=read_document(config)
    server=ThreadingHTTPServer(('127.0.0.1',port),EditorHandler)
    server.document=document;server.asset_root=Path(config).resolve().parent;server.editor_token=secrets.token_urlsafe(32)
    return server


def serve(config,port=0,open_browser=True):
    server=make_server(config,port);address='http://127.0.0.1:'+str(server.server_address[1])+'/'
    print('Travel Planning Kit: '+address,flush=True)
    print('Keep this window open. Save your JSON before closing the browser. Press Ctrl+C here to stop.',flush=True)
    if open_browser:webbrowser.open(address)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
