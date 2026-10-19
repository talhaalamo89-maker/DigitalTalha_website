"""Self-contained clickable preview, with each artwork stored only once."""
from pathlib import Path
import base64,json,mimetypes,re

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
CSS='\n'.join((ROOT/'assets'/f).read_text() for f in ['site.css','motion.css'])
JS='\n'.join((ROOT/'assets'/f).read_text() for f in ['site.js','motion.js'])
FAVICON='data:image/png;base64,'+base64.b64encode((ROOT/'assets/favicon-32.png').read_bytes()).decode()
PAGES={};ASSETS={};TOKENS={}

def embed_asset(match):
    path=match[2]
    if path not in TOKENS:
        token='__DIGITALTALHA_ASSET_'+str(len(TOKENS))+'__'
        TOKENS[path]=token
        file=DIST/path.lstrip('/')
        mime=mimetypes.guess_type(str(file))[0] or 'application/octet-stream'
        ASSETS[token]='data:'+mime+';base64,'+base64.b64encode(file.read_bytes()).decode()
    return match[1]+TOKENS[path]+match[3]

for path in DIST.rglob('index.html'):
    raw=path.read_text()
    if 'http-equiv="refresh"' in raw:continue
    route='/' if path.parent==DIST else '/'+str(path.parent.relative_to(DIST))+'/'
    raw=raw.replace('<link rel="stylesheet" href="/assets/site.css">','<style>'+CSS+'</style>')
    raw=raw.replace('<link rel="stylesheet" href="/assets/motion.css">','')
    raw=re.sub(r'<script defer src="/assets/(?:site|motion).js"></script>','',raw)
    raw=re.sub(r'(src=")(/assets/[^\"]+)(")',embed_asset,raw)
    raw=re.sub(r'<link rel="(?:icon|apple-touch-icon)"[^>]+>','',raw)
    bridge="""document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;let href=a.getAttribute('href');if(!href)return;if(href.startsWith('/')){e.preventDefault();parent.postMessage({digitalTalhaPreview:true,path:href},'*');}else if(!href.startsWith('#')){a.target='_blank';a.rel='noopener noreferrer';}});"""
    raw=raw.replace('</body>','<script>window.fetch=async()=>({ok:false,headers:{get:()=>"application/json"},json:async()=>({ok:false,message:"This preview cannot send enquiries. Please use WhatsApp or email."})});'+JS+bridge+'</script></body>')
    PAGES[route]=raw

safe_json=lambda value:json.dumps(value,ensure_ascii=False).replace('</script','<\\/script')
shell="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DigitalTalha — Full website preview</title><link rel="icon" type="image/png" sizes="32x32" href="FAVICON_DATA"><style>html,body{margin:0;width:100%;height:100%;background:#f8f7f3}iframe{border:0;width:100%;height:100%;display:block}</style></head><body><iframe id="site" title="DigitalTalha website preview"></iframe><script>const pages=PAGES_JSON;const assets=ASSETS_JSON;const frame=document.getElementById('site');function render(){const route=decodeURIComponent(location.hash.slice(1)||'/');let html=pages[route]||pages['/404/'];for(const [key,value]of Object.entries(assets))html=html.split(key).join(value);frame.srcdoc=html;document.title=(route==='/'?'Home':route.split('/').filter(Boolean).join(' / '))+' | DigitalTalha preview';}window.addEventListener('message',event=>{if(event.source!==frame.contentWindow||!event.data?.digitalTalhaPreview)return;const route=event.data.path;if(!route.startsWith('/'))return;if(location.hash.slice(1)===route)render();else location.hash=route;});window.addEventListener('hashchange',render);render();</script></body></html>"""
shell=shell.replace('PAGES_JSON',safe_json(PAGES)).replace('ASSETS_JSON',safe_json(ASSETS)).replace('FAVICON_DATA',FAVICON)
(ROOT/'DigitalTalha-preview.html').write_text(shell)
print(f'Created self-contained preview: {len(PAGES)} pages, {len(ASSETS)} shared assets, {len(shell):,} characters.')
