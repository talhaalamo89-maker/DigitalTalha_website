"""Check requested service information, static routes and the single contact form."""
from pathlib import Path
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
SERVICES=json.loads((ROOT/'content/services.json').read_text())
class Text(HTMLParser):
 def __init__(self,html):
  super().__init__(convert_charrefs=True);self.words=[];self.skip=0;self.images=[];self.links=[];self.feed(html)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag in ['script','style']:self.skip+=1
  if tag=='img':self.images.append(a)
  if tag=='a':self.links.append(a.get('href',''))
 def handle_endtag(self,tag):
  if tag in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,value):
  if not self.skip:self.words.extend(value.split())
for key,s in SERVICES.items():
 route=s['route'];source=(DIST/route.strip('/')/'index.html').read_text();parsed=Text(source)
 words=' '.join(parsed.words)
 assert '?' not in route and (DIST/route.strip('/')/'index.html').exists(),route
 assert len(parsed.words)>450,(route,'insufficient useful service detail')
 for title,description in s['includes']:
  assert title in words and description in words,(route,'scope missing',title)
 for q,a in s['faqs']:assert q in words and a in words,(route,'FAQ missing',q)
 assert s['prepare'] in words and s['note'] in words,(route,'missing project expectations')
 assert any(i.get('src')=='/assets/'+s['image'] and i.get('alt')==s['alt'] for i in parsed.images),(route,'image missing')
 assert (DIST/'assets'/s['image']).stat().st_size<100000,(route,'image too large')
 assert '<form' not in source and 'href="#contact"' not in source,(route,'repeated form or broken old contact anchor')
 for other in SERVICES.values():assert other['route'] in parsed.links,(route,'related service link missing')
for file in DIST.rglob('*.html'):
 source=file.read_text()
 if file==DIST/'contact/index.html':
  assert source.count('<form')==1
  for s in SERVICES.values():assert '<option>'+s['name']+'</option>' in source
 elif 'http-equiv="refresh"' not in source:assert '<form' not in source,(file,'only Contact should contain a form')
 for url in Text(source).links:
  if url.startswith('/'):
   assert not urlsplit(url).query,(file,'internal URL should be static',url)
 assert 'data-scroll-story' not in source
home=(DIST/'index.html').read_text()
for s in SERVICES.values():assert '/assets/'+s['image'] in home
about=(DIST/'about/index.html').read_text()
for fact in ['Class 12','UT Digital Media','Umar Tazkeer','Amity University','Philip Kotler','Google Tag Manager','Seth Godin']:
 assert fact in about,('about story missing',fact)
for page in ['index.html','about/index.html','contact/index.html']:
 assert 'class="brand-mark"' in (DIST/page).read_text()
css=(ROOT/'assets/site.css').read_text()
assert '.brand-mark{' in css and 'background:var(--ink)' in css
assert (DIST/'assets/site.js').stat().st_size<10000
print('PASS: four illustrated services, useful scope and FAQs, recovered About story, logo backing, static URLs and one Contact form.')
