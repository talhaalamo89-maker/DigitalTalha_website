"""Check page structure, routes, assets, form wiring and preserved article text."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import Counter
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
class Document(HTMLParser):
    def __init__(self,source):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.links=[];self.assets=[];self.h1=0;self.title=False
        self.empty_headings=[];self.heading=None;self.heading_text='';self.text=[];self.script=0;self.heading_levels=[]
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.append(a['id'])
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag in ['img','script'] and a.get('src'):self.assets.append(a['src'])
        if tag=='link' and a.get('href'):self.assets.append(a['href'])
        if tag=='h1':self.h1+=1
        if tag=='title':self.title=True
        if re.fullmatch(r'h[1-6]',tag):self.heading=tag;self.heading_text='';self.heading_levels.append(int(tag[1]))
        if tag in ['script','style']:self.script+=1
    def handle_data(self,data):
        if not self.script:self.text.append(data)
        if self.heading:self.heading_text+=data
    def handle_endtag(self,tag):
        if self.heading==tag:
            if not self.heading_text.strip():self.empty_headings.append(tag)
            self.heading=None
        if tag in ['script','style']:self.script=max(0,self.script-1)

errors=[];docs={}
files=list(DIST.rglob('*.html'))
for f in files:
    doc=Document(f.read_text());docs[f]=doc
    alias='http-equiv="refresh"' in f.read_text()
    if not alias:
        if doc.h1!=1:errors.append(f'{f.relative_to(DIST)}: expected one H1, got {doc.h1}')
        if not doc.title:errors.append(f'{f}: missing title')
        if doc.empty_headings:errors.append(f'{f}: empty headings')
        if any(b>a+1 for a,b in zip(doc.heading_levels,doc.heading_levels[1:])):errors.append(f'{f}: skipped heading level')
    repeats=[k for k,v in Counter(doc.ids).items() if v>1]
    if repeats:errors.append(f'{f}: duplicate IDs {repeats}')

for f,doc in docs.items():
    for url in doc.links+doc.assets:
        u=urlsplit(url)
        if u.scheme or u.netloc:continue
        p=(DIST/u.path.lstrip('/')) if u.path.startswith('/') else (f.parent/u.path if u.path else f)
        p=Path(unquote(str(p)))
        if p.is_dir():p=p/'index.html'
        if not p.exists():errors.append(f'{f.relative_to(DIST)}: broken local target {url}');continue
        if u.fragment and p.suffix=='.html':
            target=docs.get(p) or Document(p.read_text())
            if unquote(u.fragment) not in target.ids:errors.append(f'{f.relative_to(DIST)}: missing fragment {url}')

def norm(s): return re.sub(r'[^a-z0-9]','',s.lower())
source=json.loads((ROOT/'content/original-pages.json').read_text())
article='/how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization/'
article_text=norm(' '.join(docs[DIST/article.strip('/')/'index.html'].text))
missing=[]
for n,t in source['https://digitaltalha.com'+article]['lines']:
    if 36<=n<=869:
        cleaned=re.sub(r'^[#*>\s]+','',t).strip().replace('`','')
        cleaned=re.sub(r'^\d+\.\s+','',cleaned)
        if len(cleaned)>8 and norm(cleaned) not in article_text:missing.append((n,cleaned))
if missing:errors.append(f'Article content missing: {missing}')

for route in ['/contact/']:
    f=DIST/route.strip('/')/'index.html'
    html=f.read_text()
    if 'action="/api/enquiry.php"' not in html:errors.append(f'{route}: missing enquiry handler')
    if 'name="consent"' not in html:errors.append(f'{route}: missing consent')
    if 'role="status"' not in html:errors.append(f'{route}: missing feedback region')

for route in ['/','/services/','/contact/']:
    if 'Website Creation' not in (DIST/route.strip('/')/'index.html').read_text():errors.append(f'{route}: Website Creation is missing.')
if "'Website Creation'" not in (ROOT/'server/enquiry.php').read_text():errors.append('Enquiry handler must accept Website Creation enquiries.')
preview=(ROOT/'DigitalTalha-preview.html').read_text()
if not re.search(r'<link rel="icon"[^>]+href="data:image/png;base64,',preview):errors.append('Standalone preview must include its own embedded browser-tab icon.')

# Public artefacts use the enquiry form instead of publishing direct contact links.
direct_contact = re.compile(r'mailto:|https?://(?:wa\.me/|api\.whatsapp\.com/send)', re.I)
for f in [*files, DIST / 'assets/site.js', ROOT / 'DigitalTalha-preview.html']:
    if direct_contact.search(f.read_text()):
        errors.append(f'{f.name}: direct contact details in public output')

if errors:
    print('\n'.join(errors));sys.exit(1)
print(f'PASS: {len(files)} HTML files; internal links, fragments, assets, unique IDs, page headings, form wiring and complete original article verified.')

