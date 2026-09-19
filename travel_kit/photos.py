"""Opt-in public listing photo discovery. This module never runs a fetch on import."""
import csv
import html
from html.parser import HTMLParser
from http.client import HTTPException
import json
from pathlib import Path
import re
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
from .files import write_file
from .model import ValidationError,safe_url
from .schema import identifier,validate_document

MAX_PAGE=5_000_000


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__();self.photos=[];self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='meta' and (values.get('property') or values.get('name')) in {'og:image','og:image:url','twitter:image'}:
            self.photos.append(values.get('content',''))
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)


def extract_photos(source):
    parser=Metadata();parser.feed(source)
    normalized=html.unescape(source).replace(r'\/', '/').replace(r'\u002F','/').replace(r'\u002f','/').replace(r'\u0026','&')
    urls=re.findall(r'https?://[^\s<>"\x27\\)\]}]+',normalized)
    provider=[]
    for url in urls:
        try:
            parsed=urlsplit(safe_url(url));host=parsed.hostname or ''
            if (host.endswith('.muscache.com') and '/im/pictures/' in parsed.path) or (host.endswith(('.trvl-media.com','.travel-assets.com','.vrbo.com','.homeaway.com')) and '/lodging/' in parsed.path):provider.append(url)
        except ValueError:continue
    # Listing photo feeds take precedence over logos, icons and decorative assets.
    candidates=provider or (parser.photos+re.findall(r'https?://[^\s<>"\x27\\]+?\.(?:jpe?g|png|webp)(?:\?[^\s<>"\x27\\]*)?',normalized,re.I))
    photos=[]
    for candidate in candidates:
        try:url=safe_url(html.unescape(candidate))
        except ValidationError:continue
        if url and url not in photos:photos.append(url)
        if len(photos)==24:break
    return {'title':' '.join(''.join(parser.title).split())[:1000],'photos':photos}


def read_previous(path):
    if path.stat().st_size>5_000_000:raise ValidationError('The existing photo file is too large.')
    try:result=json.loads(path.read_text(encoding='utf-8'))
    except (ValueError,RecursionError) as error:raise ValidationError('The existing photo file could not be read; it was not changed.') from error
    return validate_collection(result)


def validate_collection(result):
    if not isinstance(result,dict) or set(result)!={'formatVersion','listings'} or type(result['formatVersion']) is not int or result['formatVersion']!=1 or not isinstance(result['listings'],dict):
        raise ValidationError('The existing file is not a version 1 photo collection; it was not changed.')
    for key,entry in result['listings'].items():
        identifier(key,'listing ID')
        if not isinstance(entry,dict) or set(entry)!={'url','title','photos'} or not isinstance(entry['title'],str) or not isinstance(entry['photos'],list) or len(entry['photos'])>24:
            raise ValidationError('An existing photo record is invalid; nothing was changed.')
        safe_url(entry['url'])
        for photo in entry['photos']:safe_url(photo)
    return result


def apply_photos(document,collection,replace=False):
    """Explicitly attach fetched URLs by property ID, without fetching their bytes."""
    result=validate_document(document);validate_collection(collection)
    houses={h['id']:h for h in result['rentals']['houses']}
    unknown=set(collection['listings'])-set(houses)
    if unknown:raise ValidationError('Photo records refer to unlisted property IDs: '+', '.join(sorted(unknown)))
    for key,record in collection['listings'].items():
        house=houses[key];photos=[] if replace else house['photos'];known={p['src'] for p in photos}
        for src in record['photos']:
            if src not in known:
                photos.append({'src':src,'alt':house['name']+' listing photo','credit':'From the supplied listing. Check permission before sharing.'});known.add(src)
        if len(photos)>24:raise ValidationError('A property would have more than 24 photos. Trim the collection or explicitly replace its existing photos.')
        house['photos']=photos
    return validate_document(result)


def fetch_csv(csv_path,output,update=False,opener=None):
    csv_path,output=Path(csv_path),Path(output)
    if csv_path.stat().st_size>1_000_000:raise ValidationError('Choose a listings CSV smaller than 1 MB.')
    if output.exists() and not update:raise FileExistsError('Photo output already exists. Use --update to merge successful results.')
    result=read_previous(output) if output.exists() else {'formatVersion':1,'listings':{}}
    with csv_path.open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        if reader.fieldnames!=['id','url']:raise ValidationError('Use exactly these CSV headers: id,url')
        rows=list(reader)
    if not 1<=len(rows)<=100:raise ValidationError('Use 1 to 100 listing rows.')
    seen=set()
    for row in rows:
        if set(row)!={'id','url'}:raise ValidationError('Each CSV row needs exactly an ID and a URL.')
        identifier(row['id'],'listing ID');safe_url(row['url'])
        if not row['url'] or row['id'] in seen:raise ValidationError('Use nonempty URLs and unique listing IDs.')
        seen.add(row['id'])
    opener=opener or urlopen;errors=[];updated=0
    for row in rows:
        try:
            req=Request(row['url'],headers={'User-Agent':'TravelPlanningKit/1.0 (user-requested public listing photo research)','Accept':'text/html'})
            with opener(req,timeout=20) as response:
                safe_url(response.geturl())
                if 'text/html' not in response.headers.get('Content-Type','').lower():raise ValidationError('The response was not an HTML listing page.')
                raw=response.read(MAX_PAGE+1)
                if len(raw)>MAX_PAGE:raise ValidationError('The listing page exceeded the 5 MB limit.')
                encoding=re.search(r'charset=([\w-]+)',response.headers.get('Content-Type',''),re.I)
                try:source=raw.decode(encoding.group(1) if encoding else 'utf-8',errors='replace')
                except LookupError:source=raw.decode('utf-8',errors='replace')
            record=extract_photos(source)
            if not record['photos']:raise ValidationError('No public image URLs were found. The site may require JavaScript or block automated access. Add your chosen images manually.')
            result['listings'][row['id']]={'url':row['url'],**record};updated+=1
        except (OSError,ValueError,HTTPException) as error:
            errors.append({'id':row['id'],'message':str(error)[:500]})
            if hasattr(error,'close'):error.close()
    if updated:write_file(output,json.dumps(result,indent=2,ensure_ascii=False)+'\n',overwrite=update)
    return {'updated':updated,'errors':errors}
