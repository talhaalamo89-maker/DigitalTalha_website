"""Build all pages from retained original text. Python standard library only."""
from pathlib import Path
from html import escape
import json, re, shutil, os
from seo import head as seo_head, breadcrumb as seo_breadcrumb

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
SOURCE=json.loads((ROOT/'content/original-pages.json').read_text())
WEBSITE=json.loads((ROOT/'content/website-service.json').read_text())
DOMAIN='https://digitaltalha.com'
ARTICLE='how-to-build-a-meta-lead-generation-campaign-from-setup-to-optimization'
WA='https://wa.me/919641930688'
EMAIL='talhaalamo89@gmail.com'
SEO=json.loads((ROOT/'content/seo.json').read_text())
STAGING=os.environ.get('SITE_NOINDEX', '').lower() in ['1', 'true', 'yes']

def text(path,n):
    return dict(SOURCE[DOMAIN+path]['lines']).get(n,'').strip()

def line(path,n):
    return re.sub(r'^#{1,6}\s+','',text(path,n))

def esc(s): return escape(str(s),quote=True)
def paras(path,nums): return ''.join(f'<p>{esc(line(path,n))}</p>' for n in nums if line(path,n))
def eyebrow(s): return f'<div class="eyebrow">{esc(s)}</div>'
def button(label,url='/contact/',style='',arrow='↗'):
    return f'<a class="btn {style}" href="{esc(url)}">{esc(label)}<span class="arrow" aria-hidden="true">{arrow}</span></a>'
def link(label,url): return f'<a class="text-link" href="{esc(url)}">{esc(label)} <span aria-hidden="true">↗</span></a>'
def check(items): return '<ul class="check-list">'+''.join(f'<li>{esc(x)}</li>' for x in items)+'</ul>'
def platform(name):
    if name=='Website Creation':return '<span class="platform-icon web" aria-hidden="true">&lt;/&gt;</span>'
    return '<span class="platform-icon '+('google' if name=='Google Ads' else 'meta')+'" aria-hidden="true">'+('G' if name=='Google Ads' else '∞')+'</span>'
def brand(): return '<a class="brand" href="/" aria-label="DigitalTalha home"><img src="/assets/logo-mark.png" width="40" height="38" alt=""><span>DigitalTalha<span class="brand-dot">.</span></span></a>'

STAR='<svg viewBox="0 0 100 100" fill="currentColor" aria-hidden="true"><path d="m50 0 7 30L79 7l-9 31 30-7-24 20 24 17-31-5 9 30-23-22-6 29-8-30-22 23 9-31L0 69l24-19L0 32l31 6-9-30 22 22z"/></svg>'
ICON='<svg class="mini-icon" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M5 25V15m11 10V7m11 18V11M2 28h28"/><path d="m4 10 10-7 9 3 6-4"/></svg>'

def portrait():
    return f'''<div class="portrait-scene"><div class="portrait-star">{STAR}</div><div class="portrait"><img src="/assets/talha-portrait.webp" alt="Talha Alam, independent digital marketer" width="900" height="1125" fetchpriority="high"><div class="portrait-caption"><strong>Talha Alam</strong><span>Independent digital marketer</span></div></div><div class="portrait-label"><strong>Google Ads + Meta Ads</strong><span>Research. Test. Improve.</span></div><div class="portrait-bottom"><span>BASED IN INDIA</span><span>Personal attention. Practical thinking.</span></div></div>'''

def header(current):
    nav=[('Home','/'),('About','/about/'),('Services','/services/'),('Projects','/blog/'),('Contact','/contact/')]
    active='/services/' if current in ['/google-ads/','/meta-ads/','/website-creation/'] else '/blog/' if current=='/'+ARTICLE+'/' else current
    links=''.join(f'<a href="{u}"'+(' aria-current="page"' if active==u else '')+f'>{s}</a>' for s,u in nav)
    return f'''<a class="skip" href="#content">Skip to content</a><header class="site-header"><div class="wrap header-inner">{brand()}<nav class="primary-nav" id="primary-nav" aria-label="Main navigation">{links}</nav><div class="header-cta">{button("Let’s talk",'/contact/')}</div><button class="menu-toggle" data-menu aria-controls="primary-nav" aria-expanded="false" aria-label="Toggle navigation"><span></span><span></span></button></div></header>'''

def footer():
    return f'''<footer class="footer"><div class="wrap"><div class="footer-top"><h2>Have a business you want<br>to grow? <span class="accent">Let’s talk.</span></h2><a href="/contact/" class="circle-link" aria-label="Talk about your business">↗</a></div><div class="footer-grid"><div>{brand()}<p>Performance marketing that drives more leads, sales, and measurable growth.</p><div class="socials"><a href="https://www.instagram.com/_digitaltalha_/" target="_blank" rel="noopener noreferrer">Instagram ↗</a><a href="https://www.linkedin.com/in/talha-alam-798st0/" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a><a href="https://www.facebook.com/profile.php?id=61572897474852" target="_blank" rel="noopener noreferrer">Facebook ↗</a></div></div><div><h3>Explore</h3><ul><li><a href="/">Home</a></li><li><a href="/about/">About</a></li><li><a href="/blog/">Projects &amp; blog</a></li><li><a href="/contact/">Contact</a></li></ul></div><div><h3>Services</h3><ul><li><a href="/services/">All services</a></li><li><a href="/google-ads/">Google Ads</a></li><li><a href="/meta-ads/">Meta Ads</a></li><li><a href="/website-creation/">Website Creation</a></li><li><a href="/contact/">Free consultation</a></li></ul></div><div><h3>Let’s talk growth</h3><a class="footer-email" href="mailto:{EMAIL}">{EMAIL}</a><ul><li><a href="{WA}">Chat on WhatsApp ↗</a></li><li><a href="/privacy-policy/">Privacy Policy</a></li><li><a href="/terms-conditions/">Terms &amp; Conditions</a></li></ul></div></div><div class="footer-bottom"><span>© 2026 DigitalTalha. All rights reserved.</span><span>Independent. Intentional. Always learning.</span><button data-back-top aria-label="Back to top">Back to top ↑</button></div><div class="footer-word" aria-hidden="true">DIGITALTALHA</div></div></footer>'''

PAGES={}
def page(path,title,body,description=None,noindex=False):
    # Metadata is maintained separately so rebuilding cannot reintroduce duplicates.
    markup=f'''<!doctype html><html lang="en-IN"><head>{seo_head(path, SEO, noindex, STAGING)}</head><body>{header(path)}<div class="motion-control-wrap"><div class="wrap motion-controls"><span>Explore at your pace</span><button class="motion-toggle" type="button" data-motion-toggle aria-pressed="false">Pause motion</button></div></div><main id="content">{body}</main>{footer()}</body></html>'''
    PAGES[path]=markup
    destination=OUT/('index.html' if path=='/' else path.strip('/')+'/index.html')
    destination.parent.mkdir(parents=True,exist_ok=True); destination.write_text(markup)

def section_heading(label,title,description=''):
    return f'''<div class="section-heading"><div>{eyebrow(label)}<h2>{esc(title)}</h2></div>{'<p>'+esc(description)+'</p>' if description else ''}</div>'''

def service_cards():
    cards=[]
    for name,a,b,points,url,i in [('Google Ads',51,53,[55,57,59,61,63],'/google-ads/','01'),('Meta Ads',64,66,[68,70,72,74,76],'/meta-ads/','02')]:
        cards.append(f'''<article class="service-card" data-reveal><div class="topline">{platform(name)}<span class="index">{i} / SERVICE</span></div><h3>{esc(line('/',a))}</h3>{paras('/',[b])}{check([line('/',n) for n in points])}{link('Explore '+name,url)}</article>''')
    cards.append(f'''<article class="service-card" data-reveal><div class="topline">{platform('Website Creation')}<span class="index">03 / SERVICE</span></div><h3>Website Creation</h3><p>{esc(WEBSITE['card_description'])}</p>{check(WEBSITE['card_points'])}{link('Explore Website Creation',WEBSITE['route'])}</article>''')
    return '<div class="services-grid three-services">'+''.join(cards)+'</div>'

def process(path,starts,six=False):
    items=[]
    for i,n in enumerate(starts):
        items.append(f'<div class="process-step"><span class="num">0{i+1} /</span><h3>{esc(line(path,n))}</h3><p>{esc(line(path,n+2))}</p></div>')
    return '<div class="process-grid'+(' six' if six else '')+'">'+''.join(items)+'</div>'

def home_values():
    return '<div class="value-list">'+''.join(f'<div class="value-row"><span class="num">0{i+1}</span><h3>{esc(line("/",n))}</h3><p>{esc(line("/",n+2))}</p></div>' for i,n in enumerate([116,120,124,128,131]))+'</div>'

def project_card():
    return f'''<article class="project-feature" data-project><a class="project-art" href="/{ARTICLE}/" aria-label="Read Meta Lead Campaign — From Start to Finish"><div class="project-window"><div class="window-bar"><i></i><i></i><i></i></div><img src="/assets/meta-campaign.webp" width="1200" height="677" alt="UrbanFit Meta lead campaign setup in Ads Manager, showing a campaign in draft" loading="lazy"></div></a><div class="project-info"><span class="tag">PRACTICE PROJECT · META ADS</span><h3><a href="/{ARTICLE}/">Meta Lead Campaign — From Start to Finish</a></h3><p>A practical beginner-friendly project. A hypothetical brand, a complete lead-generation campaign, and the thinking behind every step.</p>{link('Explore the project','/'+ARTICLE+'/')}</div></article>'''

def form(service='general',compact=False):
    service_options=['Google Ads','Meta Ads','Website Creation','Not sure yet']
    opts='<option value=""'+(' selected' if service=='general' else '')+' disabled>Choose one</option>'+''.join(f'<option'+(' selected' if service==v else '')+f'>{v}</option>' for v in service_options)
    name_label='Name' if compact else 'Full Name'
    extra='' if compact else '<div class="field full"><label for="website">Business Website <span>(optional)</span></label><input id="website" name="website" type="url" maxlength="250" placeholder="https://yourwebsite.com" autocomplete="url"></div>'
    budget='' if service=='general' else '<div class="field full"><label for="budget">Monthly Ad Budget</label><select id="budget" name="budget"><option>Not decided yet</option><option>Under ₹10,000</option><option>₹10,000 – ₹30,000</option><option>₹30,000 – ₹50,000</option><option>₹50,000+</option></select></div>'
    if service=='Website Creation':budget='<div class="field full"><label for="budget">Project Budget <span>(optional)</span></label><input id="budget" name="budget" maxlength="150" placeholder="Your planned budget, if you have one"></div>'
    label='Tell Me About Your Business' if compact else 'Send My Enquiry' if service=='general' else 'Discuss My Website' if service=='Website Creation' else 'Get My Free Consultation'
    service_header='' if service=='general' else '<div class="form-heading"><span class="label">Get started</span><h3>Tell Me About Your Business</h3><p>Fill in a few details and I’ll get back to you personally to schedule your free consultation.</p><p>No spam, no sales pressure — just an honest conversation about your goals.</p></div>'
    if service=='Website Creation':service_header='<div class="form-heading"><span class="label">Start a website project</span><h3>What does your website need to do?</h3><p>Share the kind of business, pages and features you have in mind. I’ll review your brief and discuss the scope and next steps with you.</p></div>'
    service_end='' if service=='general' else f'<p class="form-note">Still deciding? There’s no pressure — reach out and let’s talk about whether {service} makes sense for your business right now.</p>'
    return f'''<form class="enquiry-form" id="enquiry" data-enquiry data-service="{esc(service)}" method="post" action="/api/enquiry.php">{service_header}<div class="form-grid"><div class="field"><label for="name">{name_label} *</label><input id="name" name="name" required maxlength="100" placeholder="Your full name" autocomplete="name"></div><div class="field"><label for="business">Business Name *</label><input id="business" name="business" required maxlength="150" placeholder="Your business name" autocomplete="organization"></div><div class="field"><label for="email">Email Address *</label><input id="email" name="email" type="email" required maxlength="200" placeholder="you@business.com" autocomplete="email"></div><div class="field"><label for="phone">Phone / WhatsApp <span>(optional)</span></label><input id="phone" name="phone" type="tel" maxlength="25" pattern="[+0-9() .-]{{7,25}}" placeholder="Your number" autocomplete="tel"></div>{extra}<div class="field full"><label for="service">What do you need help with? *</label><select id="service" name="service" required>{opts}</select></div>{budget}<div class="field full"><label for="message">{'Message' if compact else 'What are you trying to achieve?'} *</label><textarea id="message" name="message" required minlength="10" maxlength="5000" rows="4" placeholder="Tell me a bit about your business and what you’re trying to achieve."></textarea></div></div><label class="form-consent"><input type="checkbox" name="consent" value="yes" required><span>I agree to the <a href="/privacy-policy/">Privacy Policy</a> and consent to being contacted.</span></label><div class="honeypot" aria-hidden="true"><label for="company-url">Leave this field blank</label><input id="company-url" name="company_url" tabindex="-1" autocomplete="off"></div><button class="btn btn-primary" type="submit" data-label="{label}">{label} <span aria-hidden="true">↗</span></button><p class="form-note">I’ll use these details to review your enquiry and contact you about your requirements.</p>{service_end}<p class="form-status" role="status" aria-live="polite" aria-atomic="true"></p><noscript><p class="form-note">Submit this form on the hosted website, or contact me directly by email or WhatsApp.</p></noscript></form>'''

def contact_options():
    return f'<div class="contact-options"><div class="contact-option"><span>EMAIL ME</span><a href="mailto:{EMAIL}">{EMAIL} ↗</a></div><div class="contact-option"><span>PREFER A QUICK CHAT?</span><a href="{WA}">Chat on WhatsApp ↗</a></div></div>'

def contact_block(service='general'):
    is_home=service=='general'
    title=line('/',187) if is_home else 'Let’s see if '+service+' is right for you.'
    description=line('/',189) if is_home else 'Let’s discuss your business goals and figure out, honestly, whether '+service+' is the right next step.'
    if service=='Website Creation':
        title='Let’s plan a website around your business.'
        description='Starting from scratch or replacing an existing site? Tell me what you need. We’ll discuss the pages, features and scope before a quote is agreed.'
    return f'''<section class="section contact-section" id="contact"><div class="wrap contact-layout"><div class="contact-intro">{eyebrow("Let’s get started")}<h2>{esc(title)}</h2><p>{esc(description)}</p>{contact_options()}<p class="form-note">{'I’ll get back to you personally — usually within a day or two.' if is_home else 'I’ll reply personally, usually within one business day.'}</p></div>{form(service,compact=is_home)}</div></section>'''

def home():
    h1=esc(line('/',34)).replace('real customers','<span class="accent">real customers</span>')
    hero=f'''<div class="wrap"><section class="hero"><div>{eyebrow('Google Ads · Meta Ads · Websites')}<h1>{h1}</h1><p class="hero-copy">{esc(line('/',36))}</p><div class="button-row">{button(line('/',38).split(' Chat')[0],'#contact','btn-primary')}{link('Chat on WhatsApp',WA)}</div><p class="hero-foot"><i></i>Independent digital marketer · Small &amp; local businesses in India</p></div>{portrait()}</section><div class="hero-strip"><div>{ICON}<span>{esc(line('/',40))}</span></div><div>{ICON}<span>{esc(line('/',42))}</span></div><div>{ICON}<span>{esc(line('/',44))}</span></div></div></div>'''
    services='<section class="section wrap" id="services">'+section_heading(line('/',46),'Digital marketing & websites, built around your business.','Reach the right people, explain your offer clearly, and make it easy to get in touch.')+service_cards()+'</section>'
    proc='<section class="section dark"><div class="wrap">'+section_heading(line('/',78),line('/',80),line('/',82))+process('/',[85,91,97,103,109])+'</div></section>'
    values='<section class="section wrap"><div class="statement"><div>'+eyebrow(line('/',113))+'<h2>'+esc(line('/',114))+'</h2></div>'+home_values()+'</div></section>'
    skill='<section class="section-sm wrap line-top">'+section_heading(line('/',135),line('/',137),line('/',139))+'<div class="skills-grid">'+''.join(f'<div class="skill"><h3>{esc(line("/",n))}</h3><p>{esc(line("/",n+2))}</p></div>' for n in [141,144,148,152,156,159])+'</div></section>'
    about=f'''<section class="section wrap about-preview"><div class="about-photo"><img src="/assets/talha-portrait.webp" width="900" height="1125" alt="Talha, independent digital marketer" loading="lazy"></div><div>{eyebrow(line('/',165))}<h2>{esc(line('/',166))}</h2>{paras('/',[168,170])}{check([line('/',n) for n in [171,173,175]])}<div class="signature">Talha<span>Digital Marketer, Google Ads &amp; Meta Ads</span></div><div class="button-row">{link('More about me','/about/')}</div></div></section>'''
    project='<section class="section soft"><div class="wrap">'+section_heading(line('/',179),line('/',180),'A closer look at the research, setup, and thinking behind the work.')+project_card()+'<div class="button-row">'+link('View All Articles','/blog/')+'</div></div></section>'
    return hero+services+proc+values+skill+about+project+contact_block()

def breadcrumb(label):
    route = next((path for path, config in SEO.items() if config['label'] == label), None)
    route = route or {'About': '/about/', 'Website Creation': '/website-creation/',
                      'Terms and Conditions': '/terms-conditions/',
                      'Projects / Meta lead campaign': '/'+ARTICLE+'/'}.get(label)
    if route is None:
        raise ValueError(f'Unknown breadcrumb: {label}')
    return seo_breadcrumb(route, SEO)

def services():
    return f'''<section class="page-hero"><div class="wrap">{breadcrumb('Services')}{eyebrow('What I do')}<h1>Ads that reach people.<br><span class="accent">Websites that explain your offer.</span></h1><p>Google Ads, Meta Ads and website creation for small and local businesses. Explore the service that fits your next step.</p></div></section><section class="section wrap">{service_cards()}</section><section class="section dark"><div class="wrap">{section_heading('How I work',line('/',80),line('/',82))}{process('/',[85,91,97,103,109])}</div></section>{contact_block()}'''

def website_creation():
    w=WEBSITE
    demo='''<div class="service-demo-wrap"><div class="service-demo website-demo"><div class="demo-browser"><span></span>Your business · Your website</div><div class="website-demo-nav"><strong>YOUR BUSINESS<span>.</span></strong><span>About &nbsp; Services &nbsp; Contact</span></div><div class="website-demo-hero"><span class="label">Clear offer. Simple next step.</span><p>A place for your<br>business to <em>stand out.</em></p><div class="website-demo-button">Let’s talk <span>↗</span></div><div class="website-demo-shape" aria-hidden="true">✳</div></div><div class="website-demo-grid"><span>YOUR SERVICES</span><span>YOUR WORK</span><span>GET IN TOUCH</span></div></div><p class="demo-caption">Illustrative website layout. Your design is shaped around your business.</p></div>'''
    hero=f'''<section class="page-hero"><div class="wrap">{breadcrumb('Website Creation')}<div class="service-hero"><div>{eyebrow(w['eyebrow'])}<h1>{esc(w['headline'])}<br><span class="accent">{esc(w['headline_accent'])}</span></h1><p>{esc(w['intro'])}</p><div class="button-row">{button('Discuss my website','#contact','btn-primary')}{link('Talk on WhatsApp',WA)}</div><p class="form-note">{esc(w['workflow_note'])}</p></div>{demo}</div></div></section>'''
    intro='<section class="section wrap">'+section_heading('The right starting point','A website with a job to do.','Your customers should be able to understand your services, find the details they need, and take the next step without getting lost.')+'<div class="fit-grid">'+''.join('<div class="fit-card"><h3>'+esc(a)+'</h3><p>'+esc(b)+'</p></div>' for a,b in w['website_types'])+'</div></section>'
    deliverables='<section class="section soft"><div class="wrap">'+section_heading('What can be included','The essentials, thoughtfully put together.','We agree the exact pages, features and deliverables before the project starts. Your quote will make the scope clear.')+'<div class="benefit-grid">'+''.join('<div><h3>'+esc(a)+'</h3><p>'+esc(b)+'</p></div>' for a,b in w['deliverables'])+'</div></div></section>'
    proc='<section class="section dark" id="process"><div class="wrap">'+section_heading('How we’ll work together','From a clear brief to a useful website.','You see the plan, review the design, and know what happens before launch.')+'<div class="process-grid six">'+''.join(f'<div class="process-step"><span class="num">0{i+1} /</span><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i,(a,b) in enumerate(w['process']))+'</div></div></section>'
    prepare='<section class="section wrap"><div class="narrative"><div>'+eyebrow('Before we begin')+'<h2>A little preparation makes a better website.</h2></div><div class="prose"><p>Bring your business details, logo, service information, contact details and any photos or copy you can use. We’ll identify what is missing and agree who prepares it.</p>'+check(['The main action you want visitors to take','The pages and features you need','Your current website, if you have one','Your brand assets and content','Your budget and preferred timeline'])+'<p>Domain, hosting, paid integrations and ongoing updates are discussed separately unless included in the quote.</p></div></div></section>'
    faq='<section class="section wrap line-top" id="faqs"><div class="faq-layout"><div>'+eyebrow('FAQs')+'<h2>A few things you might be wondering.</h2></div><div class="faq">'+''.join('<details><summary>'+esc(a)+'</summary><p>'+esc(b)+'</p></details>' for a,b in w['faqs'])+'</div></div></section>'
    return hero+intro+deliverables+proc+prepare+faq+contact_block(w['name'])

def service_demo(name):
    if name=='Google Ads':
        return f'''<div class="service-demo-wrap"><div class="service-demo"><div class="demo-browser"><span></span>google.com/search?q=google+ads+expert+near+me</div><div class="demo-inner"><div class="demo-url">D &nbsp; digitaltalha.com &nbsp; · &nbsp; Sponsored example</div><h3>Google Ads Management — DigitalTalha</h3><p>Freelance Google Ads specialist for small businesses. Personal strategy, transparent reporting, honest advice. Free first consultation.</p><div class="demo-links"><a href="#contact"><strong>Free Consultation</strong><span>Discuss your goals, no cost</span></a><a href="#process"><strong>My Process</strong><span>See how campaigns are built</span></a><a href="#industries"><strong>Industries I Help</strong><span>Local &amp; small businesses</span></a><a href="#faqs"><strong>FAQs</strong><span>Common questions answered</span></a></div></div></div><p class="demo-caption">This is the spot your business could be in. Illustrative search ad.</p></div>'''
    return '''<div class="service-demo-wrap"><div class="service-demo"><div class="demo-browser"><span></span>facebook.com/adsmanager/manage/campaigns</div><div class="demo-inner"><div class="demo-url">D &nbsp; digitaltalha.com &nbsp; · &nbsp; Campaign structure example</div><h3 style="color:#1b1b19">Meta Ads Management — DigitalTalha</h3><p>A clear view of the actions that matter.</p><div class="demo-metrics"><div><strong>Leads</strong><span>Tracked enquiries from your campaigns</span></div><div><strong>Reach</strong><span>People seeing your message</span></div><div><strong>Cost per lead</strong><span>Spend measured against results</span></div><div><strong>Creative tests</strong><span>Improving what people respond to</span></div></div></div></div><p class="demo-caption">This is how your offer can reach the right people. Illustrative layout.</p></div>'''

def service(path,name):
    # Original Google and Meta layouts differ by a line after their process sections.
    meta=name=='Meta Ads'
    hero=f'''<section class="page-hero"><div class="wrap">{breadcrumb(name)}<div class="service-hero"><div>{eyebrow(line(path,33))}<h1>{esc(line(path,34))}</h1>{paras(path,[36])}<div class="button-row">{button('Get Free Consultation','#contact','btn-primary')}{link('Talk on WhatsApp',WA)}</div><p class="form-note">{esc(line(path,40))}</p></div>{service_demo(name)}</div></div></section>'''
    proof='<div class="wrap proof-strip">'+''.join(f'<div><h3>{esc(line(path,n))}</h3><p>{esc(line(path,n+2))}</p></div>' for n in [66,70,74,78,82])+'</div>'
    fit='<section class="section wrap">'+section_heading(line(path,86),line(path,87),line(path,89))+'<div class="fit-grid">'+''.join(f'<div class="fit-card"><span class="label">{esc(line(path,n))}</span><h3>{esc(line(path,h))}</h3><p>{esc(line(path,d))}</p></div>' for n,h,d in [(91,93,95),(97,98,100),(102,104,106)])+'</div></section>'
    benefits='<section class="section soft"><div class="wrap">'+section_heading(line(path,108),line(path,110))+'<div class="benefit-grid">'+''.join(f'<div><h3>{esc(line(path,n))}</h3><p>{esc(line(path,n+2))}</p></div>' for n in [112,115,119,123,127,(130 if meta else 131),134,138])+'</div></div></section>'
    starts=[149,155,161,167,172,178] if not meta else [149,155,161,167,173,179]
    # Use verified headings rather than assume identical source spacing.
    raw=SOURCE[DOMAIN+path]['lines']
    process_items=[]
    for n,t in raw:
        if 148<=n<=181 and t.startswith('### '):
            desc=next((v for k,v in raw if k>n and k<=n+4 and v and not v.startswith('#') and not v.isdigit()),'')
            process_items.append((t[4:],desc))
    proc='<section class="section dark" id="process"><div class="wrap">'+section_heading('My process',"How we’ll work together.",line(path,146))+'<div class="process-grid six">'+''.join(f'<div class="process-step"><span class="num">0{i+1} /</span><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i,(a,b) in enumerate(process_items))+'</div></div></section>'
    why_start=182 if meta else 183
    why_items=[t for n,t in raw if why_start+4<=n<=why_start+19 and t]
    why='<section class="section wrap"><div class="narrative"><div>'+eyebrow('Why work with me')+'<h2>Why work with a freelancer instead of an agency.</h2></div><div>'+check(why_items)+'</div></div></section>'
    industries=[re.sub(r'^#### ','',t) for n,t in raw if 204<=n<=222 and t.startswith('####')]
    industries_section='<section class="section-sm soft" id="industries"><div class="wrap">'+section_heading('Who I work with','Industries I work with.')+'<div class="industry-list">'+''.join('<span>'+esc(t)+'</span>' for t in industries)+'</div></div></section>'
    faq_start=223 if meta else 224
    faq_end=260 if meta else 261
    faq_lines=[t for n,t in raw if faq_start<n<faq_end and t and not t.startswith('#')]
    faq_items=[];i=0
    while i<len(faq_lines):
        if faq_lines[i].endswith('?') and i+1<len(faq_lines): faq_items.append((faq_lines[i],faq_lines[i+1]));i+=2
        else:i+=1
    faq='<section class="section wrap" id="faqs"><div class="faq-layout"><div>'+eyebrow('FAQs')+'<h2>Common questions<br>about '+name+'.</h2></div><div class="faq">'+''.join('<details><summary>'+esc(a)+'</summary><p>'+esc(b)+'</p></details>' for a,b in faq_items)+'</div></div></section>'
    return hero+proof+fit+benefits+proc+why+industries_section+faq+contact_block(name)

def about():
    path='/about/'
    hero=f'''<section class="page-hero"><div class="wrap">{breadcrumb('About')}<div class="page-hero-grid"><div>{eyebrow(line(path,33))}<h1>{esc(line(path,34))}</h1>{paras(path,[36])}<div class="button-row">{button('Let’s talk about your advertising','/contact/','btn-primary')}</div></div>{portrait()}</div></div></section>'''
    facts=[]
    for n,label in [(50,'Name'),(51,'Focus'),(52,'Currently'),(53,'Approach'),(54,'Working style')]:
        content=line(path,n).removeprefix('* ').removeprefix(label).strip()
        facts.append(f'<div><dt>{label}</dt><dd>{esc(content)}</dd></div>')
    intro='<section class="section wrap"><div class="narrative"><div>'+eyebrow(line(path,44))+'<h2>'+esc(line(path,45))+'</h2></div><div class="prose">'+paras(path,[47,49])+'<dl class="about-facts">'+''.join(facts)+'</dl></div></div></section>'
    journey='<section class="section soft"><div class="wrap narrative"><div>'+eyebrow(line(path,56))+'<h2>'+esc(line(path,57))+'</h2></div><div class="timeline">'+''.join(f'<div class="timeline-item"><span class="label">{esc(line(path,n))}</span><div><h3>{esc(line(path,n+2))}</h3><p>{esc(line(path,n+4))}</p></div></div>' for n in [59,65,70,75,80])+'</div></div></section>'
    # Journey source has varying blank-line spacing; select by actual headings.
    journey_cards=[]
    raw=dict(SOURCE[DOMAIN+path]['lines'])
    for n in [61,66,71,76,81]:
        label=next((raw[k] for k in range(n-1,56,-1) if raw.get(k)), '')
        desc=next((raw[k] for k in range(n+1,n+5) if raw.get(k)), '')
        journey_cards.append(f'<div class="timeline-item"><span class="label">{esc(label)}</span><div><h3>{esc(line(path,n))}</h3><p>{esc(desc)}</p></div></div>')
    journey='<section class="section soft"><div class="wrap narrative"><div>'+eyebrow(line(path,56))+'<h2>'+esc(line(path,57))+'</h2></div><div class="timeline">'+''.join(journey_cards)+'</div></div></section>'
    focus='<section class="section wrap">'+section_heading(line(path,85),line(path,87),line(path,89))+'<div class="fit-grid">'+''.join(f'<div class="fit-card"><span class="label">{esc(line(path,n))}</span><h3>{esc(line(path,h))}</h3><p>{esc(line(path,d))}</p></div>' for n,h,d in [(91,92,94),(96,98,100),(102,103,105)])+'</div></section>'
    philosophy='<section class="section wrap line-top"><div class="narrative"><div>'+eyebrow(line(path,107))+'<h2>'+esc(line(path,108))+'</h2></div><div class="prose">'+paras(path,[110,112,113,115])+'</div></div></section>'
    proc='<section class="section dark"><div class="wrap">'+section_heading(line(path,117),line(path,118),line(path,120))+process(path,[124,130,136,141,147,153],True)+'</div></section>'
    skills=[t.removeprefix('  * ').removeprefix('* ') for n,t in SOURCE[DOMAIN+path]['lines'] if 162<=n<=177 and t]
    skill='<section class="section wrap">'+section_heading(line(path,157),line(path,158),line(path,160))+'<div class="skill-tags">'+''.join('<span>'+esc(t)+'</span>' for t in skills)+'</div><p class="lead-mini">'+esc(line(path,178))+'</p></section>'
    purpose='<section class="section soft"><div class="wrap narrative"><div>'+eyebrow(line(path,180))+'<h2>'+esc(line(path,181))+'</h2></div><div class="prose">'+paras(path,[183,185])+check([line(path,n).removeprefix('→ ') for n in [187,188,190,192]])+'</div></div></section>'
    val='<section class="section wrap"><div class="statement"><div>'+eyebrow(line(path,194))+'<h2>'+esc(line(path,195))+'</h2></div><div class="value-list">'+''.join(f'<div class="value-row"><span class="num">0{i+1}</span><h3>{esc(line(path,n))}</h3><p>{esc(line(path,n+2))}</p></div>' for i,n in enumerate([197,201,205,208,212,216]))+'</div></div></section>'
    end='<section class="section-sm soft"><div class="wrap">'+section_heading(line(path,220),line(path,221),line(path,223))+'<div class="button-row">'+button('Start the conversation','/contact/','btn-primary')+'</div></div></section>'
    return hero+intro+journey+focus+philosophy+proc+skill+purpose+val+end

def contact():
    path='/contact/'
    hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Contact')+eyebrow(line(path,33))+'<h1>Let’s talk about your<br><span class="accent">marketing goals.</span></h1>'+paras(path,[36])+'</div></section>'
    content='<section class="section wrap contact-page"><div class="contact-layout"><div class="contact-intro">'+paras(path,[38])+'<div class="contact-steps">'+''.join(f'<div class="contact-step"><span>0{i+1}</span><div><h3>{esc(line(path,n))}</h3><p>{esc(line(path,n+2))}</p></div></div>' for i,n in enumerate([42,47,53]))+'</div><aside class="aside-note"><h3>'+esc(line(path,56))+'</h3>'+paras(path,[58])+'</aside>'+contact_options()+'</div>'+form()+'</div></section>'
    return hero+content

def projects():
    hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Projects')+eyebrow('Projects & practical works')+'<h1>The thinking.<br>The setup. <span class="accent">The work.</span></h1><p>A collection of campaigns, marketing systems, research and experiments I’ve built and documented.</p></div></section>'
    return hero+f'''<section class="section wrap"><div class="project-tools"><label class="search-box"><span aria-hidden="true">⌕</span><span class="label" hidden>Search projects</span><input type="search" placeholder="Search projects, campaigns, or topics…" aria-label="Search projects" data-project-search></label><span class="label">Campaigns · Research · Experiments</span></div><p class="search-result" data-search-result role="status">1 project found</p>{project_card()}</section><section class="section-sm soft"><div class="wrap">{section_heading('Let’s put the thinking to work','Have a business you want to grow?',line('/',189))}<div class="button-row">{button('Tell Me About Your Business','/contact/','btn-primary')}</div></div></section>'''

def slugify(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

def article_content(path,start,end):
    """Convert readable source content without changing its wording."""
    output=[];in_list=None;seen_ids={}
    for n,raw in SOURCE[DOMAIN+path]['lines']:
        if not start<=n<=end: continue
        t=raw.strip()
        if not t: continue
        is_bullet=t.startswith('* ');is_number=bool(re.match(r'^\d+\. ',t))
        kind='ul' if is_bullet else 'ol' if is_number else None
        if kind!=in_list:
            if in_list: output.append('</'+in_list+'>')
            if kind:output.append('<'+kind+'>')
            in_list=kind
        if kind:
            val=re.sub(r'^(?:\* |\d+\. )','',t)
            output.append('<li>'+esc(val)+'</li>');continue
        match=re.match(r'^(#{1,6})\s+(.*)',t)
        if match:
            level=2 if len(match[1])==1 else 3 if len(match[1])==2 else 4
            if path in ['/privacy-policy/','/terms-conditions/']:level=2
            base_id=slugify(match[2]);seen_ids[base_id]=seen_ids.get(base_id,0)+1
            heading_id=base_id if seen_ids[base_id]==1 else base_id+'-'+str(seen_ids[base_id])
            output.append(f'<h{level} id="{heading_id}">{esc(match[2])}</h{level}>')
        elif t.startswith('> '):output.append('<blockquote>'+esc(t[2:])+'</blockquote>')
        elif t=='↓':output.append('<p aria-hidden="true" class="orange">↓</p>')
        elif '→' in t and len(t)>55:output.append('<p class="flow-line">'+esc(t)+'</p>')
        elif t.startswith('`') or t=='`':output.append('<p><code>'+esc(t.replace('`',''))+'</code></p>')
        elif t.startswith('Email: '):output.append(f'<p>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>')
        else:output.append('<p>'+esc(t)+'</p>')
    if in_list:output.append('</'+in_list+'>')
    return ''.join(output)

def toc(path,start,end,article=False):
    heads=[]
    for n,t in SOURCE[DOMAIN+path]['lines']:
        if start<=n<=end and (t.startswith('# ') if article else t.startswith('## ')):
            h=t.lstrip('# ').strip();heads.append((slugify(h),h))
    return '<aside class="article-toc" aria-label="Table of contents"><h2>On this page</h2><ol>'+''.join(f'<li><a href="#{u}">{esc(t)}</a></li>' for u,t in heads)+'</ol></aside>'

def article():
    path='/'+ARTICLE+'/'
    hero='<section class="page-hero"><div class="wrap article-hero">'+breadcrumb('Projects / Meta lead campaign')+eyebrow('Practice project · Meta Ads')+'<h1>Meta Lead Campaign —<br><span class="accent">From Start to Finish</span></h1><div class="article-meta"><span>By Talha Alam</span><span>A practical beginner-friendly project</span><span>Campaign setup → Optimization</span></div></div></section>'
    article_intro='<p class="article-intro">A Practical Beginner-Friendly Project</p><p>By <a href="/about/">Talha Alam</a> · Explore <a href="/meta-ads/">Meta Ads management</a> or <a href="/website-creation/">landing page creation</a> for your business.</p><div class="article-note">'+esc(line(path,36))+'</div>'
    return hero+'<section class="section wrap article-layout">'+toc(path,42,869,True)+'<article class="prose article-body">'+article_intro+article_content(path,38,869)+'<div class="button-row">'+link('Back to all projects','/blog/')+'</div></article></section>'

def legal(path,title,end):
    hero='<section class="page-hero"><div class="wrap">'+breadcrumb(title)+eyebrow('The details')+'<h1>'+esc(title)+'</h1><p>Last Updated: September 2026</p></div></section>'
    return hero+'<section class="section wrap legal-layout">'+toc(path,37,end)+'<article class="prose">'+article_content(path,37,end)+'</article></section>'

def build():
    PAGES.clear()
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    shutil.copy(ROOT/'assets/favicon.ico',OUT/'favicon.ico')
    if (ROOT/'server').exists():shutil.copytree(ROOT/'server',OUT/'api',dirs_exist_ok=True)
    page('/','Practical digital marketing help for small businesses',home())
    page('/about/','About Talha Alam',about())
    page('/services/','Google Ads, Meta Ads & Website Creation Services',services())
    page(WEBSITE['route'],WEBSITE['title'],website_creation(),description=WEBSITE['description'])
    page('/google-ads/','Google Ads Management for Small Businesses',service('/google-ads/','Google Ads'))
    page('/meta-ads/','Meta Ads Services',service('/meta-ads/','Meta Ads'))
    page('/blog/','Projects and Practical Works',projects())
    page('/contact/','Let’s talk about your marketing goals',contact())
    page('/privacy-policy/','Privacy Policy',legal('/privacy-policy/','Privacy Policy',63))
    page('/terms-conditions/','Terms and Conditions',legal('/terms-conditions/','Terms and Conditions',74))
    page('/'+ARTICLE+'/','Meta Lead Campaign — From Start to Finish',article(),description='A complete practical Meta lead-generation project: goal, landing page, tracking, campaign setup, audiences, creative, remarketing, and optimization.')
    for alias,target in {'/about-us/':'/about/','/contact-us/':'/contact/','/service/':'/services/','/projects/':'/blog/'}.items():
        folder=OUT/alias.strip('/');folder.mkdir(exist_ok=True)
        (folder/'index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}"><meta name="robots" content="noindex"><link rel="canonical" href="{DOMAIN+target}"><title>Continue to DigitalTalha</title></head><body><p>This page has moved. <a href="{target}">Continue to DigitalTalha</a>.</p></body></html>')
    body='<div class="wrap not-found"><p class="big404" aria-hidden="true">404</p><h1>This page took a wrong turn.</h1><p>The page you’re looking for isn’t here. Let’s get you back to the work, the services, or a conversation.</p><div class="button-row">'+button('Back to home','/','btn-primary')+button('Get in touch','/contact/','btn-outline')+'</div></div>'
    page('/404/','Page not found',body,noindex=True)
    (OUT/'404.html').write_text(PAGES['/404/'])
    (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /api/\n' + ('' if STAGING else 'Sitemap: https://digitaltalha.com/sitemap.xml\n'))
    indexable=[] if STAGING else [p for p in PAGES if not SEO[p].get('noindex')]
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+DOMAIN+p+'</loc></url>\n' for p in indexable)+'</urlset>\n')
    (OUT/'.htaccess').write_text(r'''Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html
<IfModule mod_rewrite.c>
RewriteEngine On
# Keep WordPress-era routes working, including direct index.html requests.
RewriteRule ^about-us(?:/index\.html)?/?$ /about/ [R=301,L]
RewriteRule ^contact-us(?:/index\.html)?/?$ /contact/ [R=301,L]
RewriteRule ^service(?:/index\.html)?/?$ /services/ [R=301,L]
RewriteRule ^projects(?:/index\.html)?/?$ /blog/ [R=301,L]
# Redirect explicit index.html URLs, never internal DirectoryIndex lookups.
RewriteCond %{THE_REQUEST} \s/+(.*/)?index\.html(?:[?\s]) [NC]
RewriteRule ^(.*)index\.html$ /$1 [R=301,L]
# The production canonical is HTTPS without www. Local/staging hosts are exempt.
RewriteCond %{HTTP_HOST} ^www\.digitaltalha\.com$ [NC]
RewriteRule ^ https://digitaltalha.com%{REQUEST_URI} [R=301,L]
RewriteCond %{HTTP_HOST} ^digitaltalha\.com$ [NC]
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !^https$ [NC]
RewriteRule ^ https://digitaltalha.com%{REQUEST_URI} [R=301,L]
# Existing directories have a single trailing-slash URL; files and 404s are exempt.
RewriteCond %{REQUEST_FILENAME} -d
RewriteRule ^(.+[^/])$ /$1/ [R=301,L]
</IfModule>
<IfModule mod_headers.c>
Header always set X-Content-Type-Options "nosniff"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
Header always set X-Frame-Options "SAMEORIGIN"
Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
<Files "DigitalTalha-preview.html">
Header always set X-Robots-Tag "noindex, follow"
</Files>
</IfModule>
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/plain text/css application/javascript application/json application/xml text/xml image/svg+xml
</IfModule>
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 1 month"
ExpiresByType image/png "access plus 1 month"
ExpiresByType image/svg+xml "access plus 1 month"
ExpiresByType image/x-icon "access plus 1 month"
ExpiresByType image/vnd.microsoft.icon "access plus 1 month"
ExpiresByType text/css "access plus 1 day"
ExpiresByType application/javascript "access plus 1 day"
</IfModule>
''')
    if STAGING:
        with (OUT/'.htaccess').open('a') as settings:
            settings.write('\n<IfModule mod_headers.c>\nHeader always set X-Robots-Tag "noindex, follow"\n</IfModule>\n')
    print(f'Built {len(PAGES)} complete pages, 4 legacy routes, assets, sitemap and Hostinger settings → {OUT}')

from motion_pages import install
install(globals())

if __name__=='__main__':build()

