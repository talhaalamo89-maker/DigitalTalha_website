"""Visual marketing pages. Original source remains in content/original-pages.json."""
from html import escape
import re


def install(site):
    e=lambda value:escape(str(value),quote=True)
    eyebrow=site['eyebrow'];button=site['button'];link=site['link']
    original_form=site['form'];contact_options=site['contact_options'];breadcrumb=site['breadcrumb']
    project_card=site['project_card'];WEBSITE=site['WEBSITE'];WA=site['WA']

    def form(service='general',compact=False):
        markup=original_form(service,compact)
        markup=re.sub(r'<div class="form-heading">.*?</div>','',markup)
        markup=re.sub(r'<p class="form-note">Still deciding\?.*?</p>','',markup)
        markup=markup.replace('I’ll use these details to review your enquiry and contact you about your requirements.','I’ll use your details to respond to your enquiry.')
        return markup

    services={
      'search':{'name':'Google Ads','url':'/google-ads/','tag':'Meet existing demand','line':'Be there when people search.','description':'Reach people actively looking for your service.','chips':['Search intent','Clear ads','Conversion tracking'],'steps':['A relevant search','A useful offer','A clear enquiry'],'pose':'search'},
      'social':{'name':'Meta Ads','url':'/meta-ads/','tag':'Start the right conversation','line':'Give the right people a reason to care.','description':'Bring your offer to Facebook and Instagram with clear creative.','chips':['Audience research','Creative testing','Lead quality'],'steps':['A relatable message','A moment of interest','A real conversation'],'pose':'social'},
      'website':{'name':'Website Creation','url':'/website-creation/','tag':'Give your business a home','line':'A website that makes the next step easy.','description':'Explain your offer and make contacting you straightforward.','chips':['Mobile layouts','Clear services','Easy contact'],'steps':['A clear first impression','A useful service page','An easy next step'],'pose':'website'}
    }

    def character(pose,eager=False):
        loading='loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<div class="clay-character pose-{pose}" aria-hidden="true"><img src="/assets/service-characters.webp" alt="" width="1881" height="836" {loading} decoding="async"></div>'

    def props(kind):
        if kind=='search':
            return '''<div class="scene-searchbar"><span aria-hidden="true">⌕</span><span>Your customer’s search</span><i></i></div><div class="scene-result"><span class="scene-micro">A RELEVANT ANSWER</span><strong>Your offer, at the right moment.</strong><span class="scene-lines"><i></i><i></i></span><span class="scene-cta">Learn more <b aria-hidden="true">↗</b></span></div><span class="floating-token token-search" aria-hidden="true">⌕</span>'''
        if kind=='social':
            return '''<div class="scene-socialpost"><div class="post-profile"><i></i><span>Your business</span><b>•••</b></div><div class="post-visual"><span>Something<br>worth <em>noticing.</em></span><i aria-hidden="true">✳</i></div><div class="post-actions" aria-hidden="true">♡ &nbsp; ◌ &nbsp; ↗</div></div><span class="floating-token token-heart" aria-hidden="true">♡</span><span class="scene-bubble">A message that clicks.</span><svg class="wave-lines" viewBox="0 0 50 55" aria-hidden="true"><path d="M10 35C6 22 10 11 22 5M21 40c-5-9-4-18 5-25M33 44c-4-7-3-12 2-16" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>'''
        return '''<div class="scene-browser"><div class="scene-browser-top"><i></i><i></i><i></i><span>yourbusiness.com</span></div><div class="scene-site"><span class="scene-micro">YOUR BUSINESS</span><strong>A clearer home<br>for your offer<span>.</span></strong><div class="scene-site-line"></div><span class="scene-cta">Let’s talk <b aria-hidden="true">↗</b></span><div class="scene-site-tiles"><i></i><i></i><i></i></div></div></div><span class="floating-token token-code" aria-hidden="true">&lt;/&gt;</span><div class="typing-dots" aria-hidden="true"><i></i><i></i><i></i></div>'''

    def stage(kind='social',mini=False,eager=False):
        return f'''<div class="motion-stage stage-{kind}{' mini-stage' if mini else ''}"><div class="scene-orbit" aria-hidden="true"></div><span class="scene-spark" aria-hidden="true">✳</span>{props(kind)}{character(kind,eager)}<span class="scene-floor" aria-hidden="true"></span></div>'''

    def story_switcher(initial='social',single=None):
        keys=[single] if single else list(services)
        buttons=''.join(f'<button type="button" data-scene-choice="{k}" aria-pressed="{str(k==initial).lower()}" aria-controls="visual-{k}">{services[k]["name"]}<span aria-hidden="true">↗</span></button>' for k in keys)
        panels=[]
        for k in keys:
            s=services[k]
            flow=''.join(f'<span><b>0{i+1}</b>{e(t)}</span>' for i,t in enumerate(s['steps']))
            panels.append(f'<div class="visual-panel" data-scene-panel="{k}" id="visual-{k}"'+(' hidden' if k!=initial else '')+f'>{stage(k,eager=k==initial)}<div class="scene-flow" aria-label="{e(s["name"])} customer journey">{flow}</div></div>')
        return '<div class="story-switcher" data-scene-switcher><div class="scene-toolbar"><span>Explore the journey</span><span class="scene-toolbar-note">Tap a service ↓</span></div><div class="scene-options" role="group" aria-label="Choose a service illustration">'+buttons+'</div>'+''.join(panels)+'<p class="scene-caption">Illustrative customer journeys</p></div>'

    def service_cards():
        return '<div class="services-grid three-services visual-service-grid">'+''.join(f'''<article class="service-card visual-service-card" data-reveal><a class="service-art-link" href="{s['url']}" aria-label="Explore {e(s['name'])}">{stage(k,True)}</a><div class="visual-service-copy"><span class="label">0{i+1} / {e(s['tag'])}</span><h3>{e(s['name'])}</h3><p>{e(s['description'])}</p><div class="service-chips">{''.join('<span>'+e(c)+'</span>' for c in s['chips'])}</div>{link('Explore '+s['name'],s['url'])}</div></article>''' for i,(k,s) in enumerate(services.items()))+'</div>'

    def goal_picker():
        return f'''<section class="section wrap" id="find-your-service"><div class="goal-picker" data-goal-picker><div>{eyebrow('Find your starting point')}<h2>What does your business need next?</h2><div class="goal-options" role="group" aria-label="Choose your website or advertising goal"><button type="button" data-goal="website" aria-pressed="true">A better website <span aria-hidden="true">↗</span></button><button type="button" data-goal="search" aria-pressed="false">Reach people searching <span aria-hidden="true">↗</span></button><button type="button" data-goal="social" aria-pressed="false">Introduce my offer <span aria-hidden="true">↗</span></button></div></div><div class="goal-answer"><div class="goal-art" data-goal-art="website">{''.join('<div data-goal-picture="'+k+'"'+(' hidden' if k!='website' else '')+'>'+stage(k,True)+'</div>' for k in services)}</div><div class="goal-recommendation" role="status" aria-live="polite" aria-atomic="true"><span class="label">A starting point to explore</span><h3 data-goal-title>Website Creation</h3><p data-goal-description>Build a clear home for your services and an easy route to enquiries.</p><a class="text-link" data-goal-link href="/website-creation/">Explore Website Creation ↗</a></div></div></div></section>'''

    def journey(website=False):
        items=[('Understand','We get clear on your business, audience and goal.','search'),('Build','I put the agreed campaign or website together.','website'),('Refine','We review, test and improve the important details.','social')]
        return '<section class="section dark visual-process"><div class="wrap"><div class="section-heading"><div>'+eyebrow('How it comes together')+'<h2>Clear steps.<br>A little curiosity.</h2></div><p>Explore each step. You work directly with me throughout.</p></div><div class="journey" data-journey><div class="journey-choices" role="group" aria-label="Explore the project process">'+''.join(f'<button type="button" data-journey-choice="{i}" aria-pressed="{str(i==0).lower()}" aria-controls="journey-{i}"><span>0{i+1}</span><strong>{a}</strong><b aria-hidden="true">↗</b></button>' for i,(a,b,k) in enumerate(items))+'</div><div class="journey-panels">'+''.join(f'<div id="journey-{i}" data-journey-panel="{i}"'+(' hidden' if i else '')+f'><div class="journey-art">{stage(k,True)}</div><div class="journey-copy"><span class="label">STEP 0{i+1}</span><h3>{a}</h3><p>{b}</p></div></div>' for i,(a,b,k) in enumerate(items))+'</div></div></div></section>'

    def contact_block(service='general'):
        name=service if service!='general' else 'your next step'
        title='Let’s make it happen.' if service=='general' else 'Let’s talk about '+name+'.'
        return f'''<section class="section contact-section compact-contact" id="contact"><div class="wrap contact-layout"><div class="contact-intro">{eyebrow('A simple first step')}<h2>{e(title)}</h2><p>Tell me about your business and what you need. I’ll review it personally.</p><div class="contact-illustration">{stage('social',True)}</div>{contact_options()}</div>{form(service,compact=service=='general')}</div></section>'''

    def compact_faq(questions,title='A few useful answers.'):
        return '<section class="section wrap compact-faq"><div class="faq-layout"><div>'+eyebrow('Good questions')+'<h2>'+e(title)+'</h2><p class="lead-mini">Open the details you need.</p></div><div class="faq">'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in questions)+'</div></div></section>'

    def home():
        hero=f'''<div class="wrap"><section class="hero visual-hero"><div>{eyebrow('Freelance digital marketer · India')}<h1>Your business.<br>Seen. Understood.<br><span class="accent">Easy to choose.</span></h1><p class="hero-copy">I’m Talha. I help small businesses in India with Google Ads, Meta Ads and websites that make getting in touch easy.</p><div class="button-row">{button('Let’s talk','#contact','btn-primary')}{link('Find my service','#find-your-service')}</div><p class="hero-foot"><i></i>One person. Direct communication. Based in India.</p></div>{story_switcher()}</section><div class="visual-marquee" aria-label="My focus"><span>Real business goals</span><i aria-hidden="true">✳</i><span>Thoughtful creative</span><i aria-hidden="true">✳</i><span>Clear next steps</span><i aria-hidden="true">✳</i><span>Always improving</span></div></div>'''
        cards='<section class="section wrap visual-services" id="services"><div class="section-heading"><div>'+eyebrow('Three connected services')+'<h2>Digital marketing &amp; website services.</h2></div><p>From discovery to a clear place to enquire.</p></div>'+service_cards()+'</section>'
        about=f'''<section class="section wrap compact-about"><div class="compact-portrait"><img src="/assets/talha-portrait.webp" width="900" height="1125" alt="Talha Alam" loading="lazy"><span class="portrait-sticker">Hello, I’m Talha <span aria-hidden="true">↗</span></span></div><div>{eyebrow('The person behind the work')}<h2>A curious mind.<br><span class="accent">A practical approach.</span></h2><p>You work directly with me on your ads, website and the thinking behind them.</p><div class="value-pills"><span>Research first</span><span>Clear communication</span><span>Thoughtful testing</span></div>{link('Get to know me','/about/')}</div></section>'''
        project='<section class="section soft"><div class="wrap"><div class="section-heading"><div>'+eyebrow('Behind the scenes')+'<h2>A closer look at the work.</h2></div>'+link('All projects','/blog/')+'</div>'+project_card()+'</div></section>'
        return hero+cards+goal_picker()+journey()+about+project+contact_block()

    def services_page():
        return '<section class="page-hero compact-page-hero"><div class="wrap">'+breadcrumb('Services')+eyebrow('Your next step')+'<h1>Digital marketing.<br><span class="accent">Website creation.</span></h1><p>Choose a service. Explore the journey. Let’s see what fits.</p></div></section><section class="section wrap">'+service_cards()+'</section>'+goal_picker()+journey()+contact_block()

    def service_page(path,name):
        k='search' if name=='Google Ads' else 'social';s=services[k]
        head='Google Ads management.<br><span class="accent">Reach people searching.</span>' if k=='search' else 'Meta Ads management.<br><span class="accent">Facebook &amp; Instagram.</span>'
        intro='Google search campaigns for small businesses in India, built around what your customers are looking for.' if k=='search' else 'Facebook and Instagram campaigns for small businesses in India, built around your audience, offer and creative.'
        hero=f'<section class="page-hero"><div class="wrap">{breadcrumb(name)}<div class="service-hero visual-detail-hero"><div>{eyebrow(name)}<h1>{head}</h1><p>{intro}</p><div class="button-row">{button("Discuss my campaign", "#contact", "btn-primary")}{link("Ask on WhatsApp",WA)}</div><div class="service-chips">'+''.join('<span>'+e(c)+'</span>' for c in s['chips'])+f'</div></div>{story_switcher(k,k)}</div></div></section>'
        points=[('Understand intent','Research the searches and needs behind demand.','⌕'),('Build the campaign','Connect keywords, ad copy and the offer.','↗'),('Track & improve','Measure meaningful actions and test changes.','◉')] if k=='search' else [('Understand people','Research the audience and what matters to them.','♡'),('Test the creative','Explore useful messages, visuals and angles.','✳'),('Follow the funnel','Review enquiries, lead quality and next steps.','↗')]
        essentials='<section class="section wrap"><div class="section-heading"><div>'+eyebrow('What I work on')+'<h2>The pieces that matter.</h2></div><p>A clear plan before spend.</p></div><div class="visual-deliverables">'+''.join('<div><span class="delivery-icon" aria-hidden="true">'+icon+'</span><h3>'+a+'</h3><p>'+b+'</p></div>' for a,b,icon in points)+'</div></section>'
        raw=site['SOURCE'][site['DOMAIN']+path]['lines'];faq_lines=[t for n,t in raw if 224<n<260 and t and not t.startswith('#')];questions=[]
        for i,t in enumerate(faq_lines[:-1]):
            if t.endswith('?') and any(word in t.lower() for word in ['budget','guarantee','own','started']):questions.append((t,faq_lines[i+1]))
        scope=[site['line']('/',n) for n in ([55,57,59,61,63] if k=='search' else [68,70,72,74,76])]
        detail='<section class="section-sm soft"><div class="wrap scope-row"><div>'+eyebrow('The practical details')+'<h2>Is this a good fit?</h2><p>Useful when you have a clear offer, a test budget and a way to follow up on enquiries.</p></div><details class="scope-detail"><summary>See what campaign management includes <span aria-hidden="true">+</span></summary>'+site['check'](scope)+'<p>Your ad spend and management fee are separate. Scope is agreed before work begins.</p></details></div></section>'
        return hero+essentials+detail+journey()+compact_faq(questions)+contact_block(name)

    def website_creation():
        s=services['website'];hero=f'<section class="page-hero"><div class="wrap">{breadcrumb("Website Creation")}<div class="service-hero visual-detail-hero"><div>{eyebrow("Website Creation")}<h1>Website design.<br><span class="accent">Built for your business.</span></h1><p>Business websites, landing pages and portfolios for small businesses in India. Clear services. Easy enquiries.</p><div class="button-row">{button("Discuss my website","#contact","btn-primary")}{link("Ask on WhatsApp",WA)}</div><p class="form-note">AI-assisted development. Personally reviewed.</p></div>{story_switcher("website","website")}</div></div></section>'
        points=[('Made for mobile','Readable pages and easy-to-use contact options.','↗'),('Clear services','A useful structure around your offer and audience.','☷'),('Ready to hand over','Agreed source files, hosting help and next steps.','&lt;/&gt;')]
        deliverables='<section class="section wrap"><div class="section-heading"><div>'+eyebrow('Thoughtfully put together')+'<h2>Useful from the first visit.</h2></div><p>We agree the pages, features and scope before the build.</p></div><div class="visual-deliverables">'+''.join('<div><span class="delivery-icon" aria-hidden="true">'+i+'</span><h3>'+a+'</h3><p>'+b+'</p></div>' for a,b,i in points)+'</div></section>'
        scope='<section class="section-sm soft"><div class="wrap scope-row"><div>'+eyebrow('The right scope')+'<h2>Only the details you need.</h2><p>Your website is planned around your business and budget.</p></div><details class="scope-detail"><summary>Explore the full website scope <span aria-hidden="true">+</span></summary>'+''.join('<h3>'+e(a)+'</h3><p>'+e(b)+'</p>' for a,b in WEBSITE['deliverables'])+'</details></div></section>'
        selected=[WEBSITE['faqs'][i] for i in [1,2,3,6,7,8]]
        return hero+deliverables+scope+journey(True)+compact_faq(selected)+contact_block('Website Creation')

    def about():
        hero=f'<section class="page-hero"><div class="wrap">{breadcrumb("About")}<div class="page-hero-grid"><div>{eyebrow("Talha Alam · Independent digital marketer")}<h1>Talha Alam.<br><span class="accent">Your digital marketer.</span></h1><p>I’m Talha. I work on Google Ads, Meta Ads and websites for small businesses. You work directly with me.</p><div class="button-row">{button("Let’s talk","/contact/","btn-primary")}</div></div>{site["portrait"]()}</div></div></section>'
        intro='<section class="section wrap"><div class="about-visual-values"><div>'+eyebrow('One person. Three connected skills.')+'<h2>A little more<br>about the approach.</h2><p class="about-short">Research the problem. Build thoughtfully. Keep learning from the work.</p></div><div class="about-character-line">'+stage('search',True)+'</div></div><div class="visual-deliverables"><div><span class="delivery-icon" aria-hidden="true">⌕</span><h3>Research first</h3><p>Understand the audience before choosing a message.</p></div><div><span class="delivery-icon" aria-hidden="true">✳</span><h3>Clear communication</h3><p>Explain what’s happening and why.</p></div><div><span class="delivery-icon" aria-hidden="true">↗</span><h3>Keep improving</h3><p>Test ideas, review the details, and learn.</p></div></div></section>'
        facts='<section class="section-sm soft"><div class="wrap about-facts-compact"><div><span class="label">Learning</span><h3>BBA · Amity University</h3><p>Currently studying business administration.</p></div><div><span class="label">Training</span><h3>UT Digital Media</h3><p>Structured digital marketing learning and practical work.</p></div><div><span class="label">Working style</span><h3>Direct & personal</h3><p>One conversation, from planning to handover.</p></div></div></section>'
        return hero+intro+facts+journey()+'<section class="section wrap"><div class="button-row">'+link('Explore my practical work','/blog/')+'</div></section>'+contact_block()

    def contact():
        hero='<section class="page-hero compact-page-hero"><div class="wrap">'+breadcrumb('Contact')+eyebrow('Let’s talk')+'<h1>Contact Talha.<br><span class="accent">Plan your next step.</span></h1><p>A website, an ad campaign, or a question about where to start.</p></div></section>'
        return hero+contact_block()

    def projects():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Projects')+'<div class="page-hero-grid"><div>'+eyebrow('Projects & practical work')+'<h1>Marketing projects.<br><span class="accent">The thinking behind them.</span></h1><p>Explore the research and decisions behind a complete practice campaign.</p></div><div class="project-sidekick">'+stage('search',True,eager=True)+'</div></div></div></section>'
        listing='<section class="section wrap"><div class="project-tools"><label class="search-box"><span aria-hidden="true">⌕</span><input type="search" placeholder="Search projects or topics…" aria-label="Search projects" data-project-search></label><span class="label">Campaigns · Research · Experiments</span></div><p class="search-result" data-search-result role="status">1 project found</p>'+project_card()+'</section>'
        return hero+listing

    site.update(home=home,services=services_page,service=service_page,website_creation=website_creation,about=about,contact=contact,projects=projects,service_cards=service_cards,contact_block=contact_block)

