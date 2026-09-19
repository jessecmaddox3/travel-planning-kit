"""Closed, versioned document schema. No user field is silently discarded."""
import copy
import json
import re
from .model import ValidationError, safe_url, iso_date, validate_dates, quote_value, select_items


def text(value, path):
    if not isinstance(value, str) or len(value) > 10000:
        raise ValidationError(f'{path}: use text of at most 10000 characters.')
    return value


def identifier(value, path):
    text(value, path)
    if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', value):
        raise ValidationError(f'{path}: use a short ID starting with a lowercase letter, then letters, digits or hyphens.')
    return value


def integer(value, path):
    if type(value) is not int or not 1 <= value <= 10000:
        raise ValidationError(f'{path}: use a whole number from 1 to 10000.')
    return value


def enumeration(*values):
    def check(value, path):
        if not any(type(value) is type(choice) and value == choice for choice in values):
            raise ValidationError(f'{path}: choose ' + ', '.join(str(x) for x in values) + '.')
        return value
    return check


def day(value, path):
    text(value, path)
    if value:
        try: iso_date(value)
        except ValidationError as error: raise ValidationError(f'{path}: {error}') from error
    return value


def link(value, path):
    try: return safe_url(value)
    except ValidationError as error: raise ValidationError(f'{path}: {error}') from error


def array(check, maximum=500):
    def validate(value, path):
        if not isinstance(value, list) or len(value) > maximum:
            raise ValidationError(f'{path}: use a list with at most {maximum} entries.')
        for i, item in enumerate(value): check(item, f'{path}[{i}]')
        return value
    return validate


def object_of(fields, required=()):
    def validate(value, path):
        if not isinstance(value, dict): raise ValidationError(f'{path}: use an object.')
        unknown = set(value) - set(fields)
        if unknown: raise ValidationError(f'{path}: unsupported fields: ' + ', '.join(sorted(unknown)))
        missing = set(required) - set(value)
        if missing: raise ValidationError(f'{path}: missing fields: ' + ', '.join(sorted(missing)))
        for key, item in value.items(): fields[key](item, f'{path}.{key}')
        return value
    return validate


TEXTS = array(text)
IDS = array(identifier)
TRI = enumeration('yes', 'no', 'unknown')
CATEGORY = object_of({'id':identifier, 'label':text, 'note':text, 'column':enumeration(1, 2)}, ('id','label','column'))
ITEM = object_of({'id':identifier,'category':identifier,'label':text,'tags':array(enumeration('universal','beach','camping','road-trip'),4),'quantity':text,'assignee':text,'note':text}, ('id','category','label','tags'))
QUOTE = object_of({'kind':enumeration('exact','range','unknown'),'currency':text,'amount':text,'min':text,'max':text,'scope':text,'stayStart':day,'stayEnd':day,'checked':day,'note':text}, ('kind','currency'))
PHOTO = object_of({'src':text,'alt':text,'credit':text}, ('src','alt'))
HOUSE = object_of({
    'id':identifier,'name':text,'tier':enumeration('shortlist','alternative','rejected'),'rank':integer,'rationale':text,
    'platform':text,'url':link,'town':text,'drive':text,'sleeps':text,'bedrooms':text,'bathrooms':text,'squareFeet':text,'acreage':text,
    'theater':TRI,'waterfront':text,'pool':text,'hotTub':TRI,'gameRoom':TRI,'sauna':TRI,'amenities':TEXTS,
    'quote':QUOTE,'rating':text,'cancellation':text,'availability':enumeration('available','unavailable','unknown'),'notes':text,
    'beds':text,'childPracticalities':text,'photos':array(PHOTO,24)
}, ('id','name','tier','rank','quote','photos'))
PLAN = object_of({
    'summary':text,'status':array(object_of({'label':text,'value':text,'note':text},('label','value'))),
    'days':array(object_of({'date':day,'theme':text,'morning':text,'afternoon':text,'evening':text,'backup':text},('date','theme'))),
    'decisions':array(object_of({'question':text,'urgency':enumeration('soon','before-trip','optional'),'owner':text,'due':day,'status':text,'options':TEXTS,'note':text},('question','urgency'))),
    'activities':array(object_of({'name':text,'description':text,'constraints':text,'source':link},('name',))),
    'preferences':array(object_of({'question':text,'answer':text,'owner':text},('question','answer'))),
    'sources':array(object_of({'label':text,'url':link,'checked':day,'note':text},('label',))),
    'notes':TEXTS,'review':object_of({'worked':TEXTS,'change':TEXTS,'carryForward':TEXTS})
},('summary','status','days','decisions','activities','preferences','sources','notes'))
DOCUMENT = object_of({
    'formatVersion':enumeration(1),
    'trip':object_of({'title':text,'subtitle':text,'destination':text,'origin':text,'start':day,'end':day,'party':text},('title','start','end')),
    'catalog':object_of({'categories':array(CATEGORY,60),'items':array(ITEM,1000)},('categories','items')),
    'packing':object_of({'tags':array(enumeration('universal','beach','camping','road-trip'),4),'selected':IDS,'excluded':IDS,'morning':IDS,'note':text},('tags','selected','excluded','morning')),
    'plan':PLAN,
    'rentals':object_of({'hero':PHOTO,'summary':text,'criteria':TEXTS,'splitCounts':array(integer,8),'houses':array(HOUSE,100)},('summary','criteria','splitCounts','houses')),
},('formatVersion','trip','catalog','packing','plan','rentals'))


def validate_document(value):
    DOCUMENT(value, 'document')
    if type(value['formatVersion']) is not int: raise ValidationError('formatVersion must be the number 1.')
    validate_dates(value['trip']['start'],value['trip']['end'])
    categories=value['catalog']['categories'];ids=[x['id'] for x in categories]
    if len(ids)!=len(set(ids)): raise ValidationError('Catalog category IDs must be unique.')
    for item in value['catalog']['items']:
        if item['category'] not in ids: raise ValidationError('Every item must refer to a listed category.')
    select_items(value['catalog']['items'],value['packing'])
    houses=value['rentals']['houses'];ids=[x['id'] for x in houses]
    if len(ids)!=len(set(ids)): raise ValidationError('Rental IDs must be unique.')
    for house in houses:
        quote_value(house['quote'])
        quote=house['quote']
        if bool(quote.get('stayStart')) != bool(quote.get('stayEnd')): raise ValidationError('A quote stay needs both arrival and departure, or neither.')
        if quote.get('stayStart'): validate_dates(quote['stayStart'],quote['stayEnd'])
    return copy.deepcopy(value)


def loads_document(source):
    if not isinstance(source,str) or len(source.encode('utf-8'))>2_000_000:
        raise ValidationError('Choose a JSON document smaller than 2 MB.')
    def constant(_): raise ValidationError('JSON cannot contain NaN or Infinity.')
    def unique_pairs(pairs):
        result={}
        for key,value in pairs:
            if key in result: raise ValidationError('JSON contains a duplicate field: '+key)
            result[key]=value
        return result
    try: value=json.loads(source,parse_constant=constant,object_pairs_hook=unique_pairs)
    except (json.JSONDecodeError,RecursionError) as error: raise ValidationError('That JSON document could not be read.') from error
    return validate_document(value)
