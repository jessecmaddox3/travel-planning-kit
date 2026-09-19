"""One escaped rendering engine for the CLI, browser editor and shareable HTML."""
from pathlib import Path
import base64
from decimal import Decimal
from html import escape
from .theme import COLORS, BODY_FONT, HEADING_FONT
from .model import ValidationError, safe_url, quote_value, split_quote, currency_digits, select_items, validate_dates
from .schema import validate_document

E=lambda value:escape(str(value),quote=True)
ASSETS=Path(__file__).parent
COMPARISON_COLUMNS=[('name','Name'),('platform','Platform'),('url','Listing URL'),('town','Town / area'),('drive','Drive time'),('sleeps','Sleeps'),('bedrooms','Bedrooms'),('bathrooms','Bathrooms'),('squareFeet','Square feet'),('acreage','Acreage'),('theater','Movie theater'),('waterfront','Water frontage'),('pool','Pool'),('hotTub','Hot tub'),('gameRoom','Game room'),('amenities','Other amenities'),('quote','Stay-total quote'),('split','Per-household split'),('rating','Rating / reviews'),('cancellation','Cancellation policy'),('availability','Availability for trip dates'),('notes','Notes')]


def doc_css():
    tokens=':root{'+''.join('--'+key+':'+value+';' for key,value in COLORS.items())+'--font-body:'+BODY_FONT+';--font-heading:'+HEADING_FONT+';}'
    return tokens+(ASSETS/'document.css').read_text()


def wrap(title,body,css=None,extra_class=''):
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>{E(title)}</title><style>{css or doc_css()}</style></head><body class="{E(extra_class)}">{body}</body></html>'


def heading(doc,kind):
    t=doc['trip'];meta=' · '.join(x for x in [t.get('destination',''),t['start']+' to '+t['end'],t.get('party','')] if x)
    return f'<h1>{E(t["title"])}: {E(kind)}</h1><p class="subtitle">{E(meta)}</p>'


def tldr(text):return f'<div class="tldr"><strong>At a glance</strong><p>{E(text)}</p></div>'
def para(text,cls=''):return f'<p class="{E(cls)}">{E(text)}</p>'
def bullets(items):return '<ul>'+''.join('<li>'+E(x)+'</li>' for x in items)+'</ul>'
def section(title,body):return '<section><h2>'+E(title)+'</h2>'+body+'</section>'
def footer():return '<footer>Made with Travel Planning Kit. Keep personal plans and exported files private until you choose to share them.</footer>'
def external(url,label):return f'<a href="{E(safe_url(url))}" target="_blank" rel="noopener noreferrer">{E(label)}</a>' if url else E(label)


def table(headers,rows,cls=''):
    return '<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable comparison"><table class="'+E(cls)+'"><thead><tr>'+''.join('<th scope="col">'+E(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join(('<th scope="row">'+c+'</th>') if i==0 else '<td>'+c+'</td>' for i,c in enumerate(row))+'</tr>' for row in rows)+'</tbody></table></div>'


def render_packing(doc):
    d=validate_document(doc);items=select_items(d['catalog']['items'],d['packing']);morning=set(d['packing']['morning'])
    def rows(chosen):
        result=[]
        for x in chosen:
            details=' · '.join(v for v in [x.get('quantity',''),x.get('assignee',''),x.get('note','')] if v)
            result.append(f'<label class="packing-item"><input type="checkbox">{E(x["label"])}'+(f'<span class="item-detail">{E(details)}</span>' if details else '')+'</label>')
        return ''.join(result)
    urgent=[x for x in items if x['id'] in morning]
    top='<div class="morning"><h2>Morning of departure</h2>'+para('These are selected items to check again before leaving. They also appear in their categories.')+(rows(urgent) or para('No morning-of items selected.'))+'</div>'
    columns=[]
    for col in (1,2):
        content=''
        for category in d['catalog']['categories']:
            chosen=[x for x in items if x['category']==category['id']]
            if category['column']==col and chosen:
                content+='<section class="packing-category"><h2>'+E(category['label'])+'</h2>'+rows(chosen)+para(category.get('note',''),'note')+'</section>'
        columns.append('<div>'+content+'</div>')
    body='<main>'+heading(d,'packing list')+tldr(d['packing'].get('note','Review your chosen items, then print the checklist.'))+top+'<div class="packing-columns">'+''.join(columns)+'</div>'+footer()+'</main>'
    return wrap(d['trip']['title']+' packing list',body)


def render_plan(doc):
    d=validate_document(doc);p=d['plan'];body=heading(d,'trip plan')+tldr(p['summary'])
    body+=section('Current status',para('A quick view of what is decided and what still needs attention.')+table(['Area','Current position','Notes'],[[E(x['label']),E(x['value']),E(x.get('note',''))] for x in p['status']]))
    body+=section('Day plan',para('Use these as anchors, leaving room to adjust for the group and the weather.')+table(['Day','Plan','Alternative'],[[E(x['date'])+'<br><strong>'+E(x['theme'])+'</strong>',''.join('<p><strong>'+label+':</strong> '+E(x.get(key,''))+'</p>' for key,label in [('morning','Morning'),('afternoon','Afternoon'),('evening','Evening')]),E(x.get('backup',''))] for x in p['days']]))
    urgency={'soon':'Soon','before-trip':'Before the trip','optional':'Optional'}
    body+=section('Open decisions',para('A named owner and a date make the next steps easier to act on.')+table(['Decision','Priority','Owner / due','Status and options'],[[E(x['question']),'<span class="badge '+E(x['urgency'])+'">'+urgency[x['urgency']]+'</span>',E(x.get('owner',''))+'<br>'+E(x.get('due','')),para(x.get('status',''))+bullets(x.get('options',[]))+para(x.get('note',''),'note')] for x in p['decisions']]))
    body+=section('Activity options',''.join(para(x['name'],'subhead')+para(x.get('description',''))+para(x.get('constraints',''),'note')+('<p>'+external(x['source'],'Source')+'</p>' if x.get('source') else '') for x in p['activities']))
    body+=section('Preferences and questionnaire',para('Keep the reasons behind the plan alongside the choices themselves.')+table(['Question','Answer','Whose preference'],[[E(x['question']),E(x['answer']),E(x.get('owner',''))] for x in p['preferences']]))
    body+=section('Sources and notes',bullets(p['notes']))
    for x in p['sources']:
        body+=para(x['label'],'subhead')+('<p>'+external(x['url'],'Open source')+'</p>' if x.get('url') else '')+(para('Checked: '+x['checked'],'note') if x.get('checked') else '')+para(x.get('note',''))
    review=p.get('review',{})
    body+=section('After the trip',para('Save the useful lessons for the next trip. Empty sections are ready to fill in.')+''.join(para(label,'subhead')+bullets(review.get(key,[])) for key,label in [('worked','What worked'),('change','What to change'),('carryForward','What to carry forward')]))
    return wrap(d['trip']['title']+' trip plan','<main>'+body+footer()+'</main>')


def quote_text(quote):
    value=quote_value(quote);currency=quote.get('currency','USD');digits=currency_digits(currency)
    if value is not None:return f'{currency} {value:,.{digits}f}'
    if quote['kind']=='range':return f'{currency} {Decimal(quote["min"]):,.{digits}f} to {Decimal(quote["max"]):,.{digits}f} (range)'
    return 'Price not supplied'


def quote_details(quote,trip):
    details=[]
    start,end=quote.get('stayStart'),quote.get('stayEnd')
    if start and end:
        nights=validate_dates(start,end)
        details.append(f'Quoted stay: {start} to {end} ({nights} '+('night' if nights==1 else 'nights')+').')
        if (start,end)!=(trip['start'],trip['end']):details.append('These quoted dates differ from this trip. Confirm a matching quote before comparing totals.')
    else:details.append('Quoted dates not supplied. Confirm the stay covered by this total.')
    details.append('Quote checked: '+quote['checked']+'.' if quote.get('checked') else 'Quote check date not supplied.')
    return details


def split_text(quote,count):
    split=split_quote(quote,count)
    if split is None:return 'No exact split until a total is supplied.'
    result=f'{count} households: {split["currency"]} {split["amount"]} each'
    if split['extra_count']:result+=f'; {split["extra_count"]} pay {split["currency"]} {split["extra_amount"]} instead'
    return result+'.'


def image_source(src,asset_root,remote_images=False):
    if src.startswith(('https://','http://')):
        safe_url(src)
        return src if remote_images else None
    if ':' in src or '\\' in src or not src or any(ord(c)<32 for c in src):raise ValidationError('Photo references must be relative image paths or explicit HTTP(S) URLs.')
    rel=Path(src)
    if rel.is_absolute() or '..' in rel.parts:raise ValidationError('Photo paths must stay inside the chosen configuration folder.')
    root=Path(asset_root).resolve();path=(root/rel).resolve()
    if not path.is_relative_to(root):raise ValidationError('A photo symlink points outside the chosen configuration folder.')
    if not path.exists():return None
    if not path.is_file() or path.stat().st_size>8_000_000:raise ValidationError('Each local image must be a file smaller than 8 MB.')
    data=path.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):mime='image/png'
    elif data.startswith(b'\xff\xd8\xff'):mime='image/jpeg'
    elif data.startswith(b'RIFF') and data[8:12]==b'WEBP':mime='image/webp'
    else:raise ValidationError('Local photos must be PNG, JPEG or WebP images.')
    return 'data:'+mime+';base64,'+base64.b64encode(data).decode('ascii')


def photo_strip(house,asset_root,remote_images):
    images=[]
    for photo in house['photos']:
        source=image_source(photo['src'],asset_root,remote_images)
        if source:
            images.append('<figure><img src="'+E(source)+'" loading="lazy" alt="'+E(photo['alt'])+'"><figcaption>'+E(photo.get('credit',''))+'</figcaption></figure>')
        elif photo['src'].startswith(('https://','http://')):
            images.append('<p class="photo-placeholder">'+external(photo['src'],'Open supplied photo')+'<br>External images are off in this offline document.</p>')
    return '<div class="strip" tabindex="0" aria-label="Scrollable photos">'+''.join(images)+'</div>' if images else '<div class="photo-placeholder">Photos not supplied</div>'


def facts(house):
    fields=[('platform','Platform'),('town','Town / area'),('drive','Drive time'),('sleeps','Sleeps'),('bedrooms','Bedrooms'),('bathrooms','Bathrooms'),('squareFeet','Square feet'),('acreage','Acreage'),('theater','Movie theater'),('waterfront','Waterfront'),('pool','Pool'),('hotTub','Hot tub'),('gameRoom','Game room'),('sauna','Sauna'),('rating','Rating')]
    return '<div class="facts">'+''.join('<div class="fact"><span>'+E(label)+'</span>'+E(house.get(key) or 'Not supplied')+'</div>' for key,label in fields)+'</div>'+para('Beds: '+(house.get('beds') or 'Not supplied'),'beds')+para('Children: '+(house.get('childPracticalities') or 'Not supplied'),'beds')+para('Other amenities: '+(', '.join(house.get('amenities',[])) or 'Not supplied'),'beds')


def property_details(house,trip,split_counts):
    q=house['quote']
    return facts(house)+para('Quote: '+quote_text(q))+''.join(para(line,'note') for line in quote_details(q,trip))+''.join(para(split_text(q,n),'note') for n in split_counts)+para('Fee and tax scope: '+(q.get('scope') or 'Not supplied'),'note')+para(q.get('note',''),'note')+para('Availability: '+house.get('availability','unknown'),'note')+para('Cancellation: '+(house.get('cancellation') or 'Not supplied'),'note')+para(house.get('notes',''),'note')+('<p>'+external(house['url'],'Open listing')+'</p>' if house.get('url') else '')


def render_comparison(doc,asset_root,remote_images=False):
    d=validate_document(doc);r=d['rentals'];houses=sorted(r['houses'],key=lambda x:x['rank']);nights=validate_dates(d['trip']['start'],d['trip']['end'])
    css=(ASSETS/'comparison.css').read_text()+'''\n.hero:not(.has-image){min-height:0}.hero-image{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.hero-credit{position:relative;z-index:1;font-size:.75rem;color:var(--dim)}.hero-inner{padding-top:3rem}.hero::after{pointer-events:none}.strip figure{margin:0;flex:none;max-width:520px;scroll-snap-align:start}.strip img{width:100%;max-width:520px;object-fit:cover}.strip figcaption{font-size:.75rem;max-width:480px;color:var(--dim);margin:8px 0}.photo-placeholder{min-height:120px;display:grid;place-content:center;text-align:center;background:var(--card2);border:1px dashed var(--dim);border-radius:10px;padding:24px}.tldr{border-left:3px solid var(--ember);padding:16px 20px;background:var(--card2)}.house{scroll-margin-top:70px}.house-head>div{min-width:0}.pricebox{max-width:100%}.pricebox span{overflow-wrap:anywhere}.note{color:var(--dim);font-size:.85rem}figure{margin:0}.strip:focus-visible{outline-offset:4px}@media print{.nav{position:static}.strip{flex-wrap:wrap;overflow:visible}.strip img{height:130px;max-width:200px}.house,.also{break-inside:avoid}body{print-color-adjust:exact}details::details-content{content-visibility:visible!important}details:not([open])>*:not(summary){display:block!important}.hero-inner{padding-top:1rem}}'''
    title=d['trip']['title'];nav=''.join('<a href="#'+E(h['id'])+'"><b>'+str(i)+'</b>'+E(h['name'])+'</a>' for i,h in enumerate([h for h in houses if h['tier']=='shortlist'],1))
    hero=r.get('hero',{});hero_src=image_source(hero['src'],asset_root,remote_images) if hero.get('src') else None
    hero_image='<img class="hero-image" src="'+E(hero_src)+'" alt="'+E(hero['alt'])+'">' if hero_src else ''
    header='<header class="hero'+(' has-image' if hero_src else '')+'">'+hero_image+'<div class="hero-inner"><p class="eyebrow">'+E(d['trip']['start']+' to '+d['trip']['end'])+'</p><h1>'+E(title)+': places to stay</h1><p class="dek">'+E(r['summary'])+'</p>'+para(hero.get('credit',''),'hero-credit')+'</div></header><nav class="nav" aria-label="Shortlist"><div class="nav-inner">'+nav+'</div></nav>'
    body=tldr('Keep the practical tradeoffs, complete quotes and source notes together. Availability and prices need checking before a real booking.')+bullets(r['criteria'])
    shortlist=[h for h in houses if h['tier']=='shortlist']
    if not shortlist:body+='<h2>No shortlist yet</h2>'+para('Move a property to the shortlist when you are ready to compare it here.')
    for i,h in enumerate(shortlist,1):
        q=h['quote'];chips=[('drive',h.get('drive','Unknown')),('sleeps',h.get('sleeps','Unknown')),('beds/baths',h.get('bedrooms','?')+' BR / '+h.get('bathrooms','?')+' BA')]
        body+='<article class="house" id="'+E(h['id'])+'"><header class="house-head"><span class="index">'+str(i)+'</span><div><h2>'+E(h['name'])+'</h2><p class="where">'+E(h.get('town',''))+'</p></div><div class="pricebox"><strong>'+E(quote_text(q))+'</strong><span>'+str(nights)+' trip nights</span>'+''.join('<span>'+E(line)+'</span>' for line in quote_details(q,d['trip']))+''.join('<span>'+E(split_text(q,n))+'</span>' for n in r['splitCounts'])+'</div></header><div class="chips">'+''.join('<span class="chip"><em>'+E(k)+'</em>'+E(v)+'</span>' for k,v in chips)+'</div>'+para(h.get('rationale',''),'take')+photo_strip(h,asset_root,remote_images)+property_details(h,d['trip'],[])+'</article>'
    body+='<h2 class="section-head">Also worth considering</h2>'+para('Expand an alternative to keep its tradeoffs and available photos in view.','section-note')
    for h in houses:
        if h['tier']=='alternative':body+='<details class="also"><summary><span class="also-name">'+E(h['name'])+'</span><span class="also-meta">'+E(h.get('town','')+' · '+quote_text(h['quote']))+'</span><span class="also-why">'+E(h.get('rationale',''))+'</span></summary>'+photo_strip(h,asset_root,remote_images)+property_details(h,d['trip'],r['splitCounts'])+'</details>'
    body+='<h2 class="section-head">Checked and ruled out</h2><ul class="outs">'+''.join('<li><strong>'+E(h['name'])+':</strong> '+E(h.get('rationale',''))+'</li>' for h in houses if h['tier']=='rejected')+'</ul><p class="foot">'+E('Prices retain their stated fee and tax scope. Ranges and unknown quotes have no precise split. '+('Remote images were explicitly enabled for this output.' if remote_images else 'Local images are embedded; external photos remain optional links.'))+'</p>'
    return wrap(title+' rental comparison',header+'<main>'+body+'</main>',css)


def render_table(doc):
    d=validate_document(doc);r=d['rentals'];rows=[]
    for h in sorted(r['houses'],key=lambda x:x['rank']):
        row=[]
        for key,_ in COMPARISON_COLUMNS:
            if key=='url':value=external(h.get('url',''),'Open listing') if h.get('url') else 'Not supplied'
            elif key=='quote':value=E(quote_text(h['quote']))+'<br>'+E(h['quote'].get('scope',''))+'<br>'+E(h['quote'].get('note',''))+'<br>'+'<br>'.join(E(x) for x in quote_details(h['quote'],d['trip']))
            elif key=='split':value='<br>'.join(E(split_text(h['quote'],n)) for n in r['splitCounts'])
            elif key=='amenities':value=E(', '.join(h.get('amenities',[])))
            elif key=='notes':value=E(h['tier']+': '+h.get('rationale','')+' '+h.get('notes',''))
            else:value=E(h.get(key,'Not supplied'))
            row.append(value)
        rows.append(row)
    intro=tldr(r['summary'])+para('All 22 comparison fields stay available here. Scroll sideways for the full table. Drive times use '+d['trip'].get('origin','your chosen origin')+'. The print layout groups the same 22 fields into four readable landscape tables. Check the print preview before printing.')
    bands=[('Location and size',[0,1,2,3,4,5,6,7]),('Space and amenities',[0,8,9,10,11,12,13,14]),('Costs and conditions',[0,16,17,18,19,20]),('Other amenities and notes',[0,15,21])]
    paper=''.join(section(title,para('The same comparison, arranged in readable groups for paper.')+table([COMPARISON_COLUMNS[i][1] for i in indices],[[row[i] for i in indices] for row in rows],'print-comparison')) for title,indices in bands)
    css=doc_css()+'.print-only{display:none}@page{size:letter landscape}@media print{.screen-only{display:none}.print-only{display:block}.print-comparison{table-layout:fixed;font-size:9pt}.print-comparison th,.print-comparison td{padding:5px;overflow-wrap:break-word}.print-only section{break-before:page}.print-only section:first-child{break-before:auto}}'
    return wrap(d['trip']['title']+' full comparison','<main>'+heading(d,'full rental comparison')+intro+'<div class="screen-only">'+table([label for _,label in COMPARISON_COLUMNS],rows,'full-comparison')+'</div><div class="print-only">'+paper+'</div>'+footer()+'</main>',css)

