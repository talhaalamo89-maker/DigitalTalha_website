"""Minimal, content-led marketing pages; all information is rendered as HTML."""
from html import escape
from pathlib import Path
import json
import re


def install(site):
    from portfolio import install as install_portfolio
    install_portfolio(site)
    e = lambda value: escape(str(value), quote=True)
    eyebrow, button, link = (site[k] for k in ['eyebrow', 'button', 'link'])
    breadcrumb, original_form = (site[k] for k in ['breadcrumb', 'form'])
    services = json.loads((Path(__file__).resolve().parents[1] / 'content/services.json').read_text())

    def portrait():
        return '<figure class="profile"><img src="/assets/talha-portrait.webp" width="900" height="1125" alt="Talha Alam, freelance digital marketer behind DigitalTalha" fetchpriority="high"><figcaption><strong>Talha Alam</strong><span>Independent digital marketer</span></figcaption></figure>'

    def image(key, eager=False):
        s = services[key]
        return f'<img src="/assets/{s["image"]}" width="960" height="640" alt="{e(s["alt"])}" '+('fetchpriority="high"' if eager else 'loading="lazy"')+' decoding="async">'

    def service_cards(level=3):
        return '<div class="services-grid">'+''.join(f'<article class="service-card"><a class="service-art" href="{s["route"]}" aria-label="Explore {e(s["name"])}">{image(key)}</a><div class="service-card-copy"><p class="label">0{i+1} / {e(s["tag"])}</p><h{level}><a href="{s["route"]}">{e(s["name"])}</a></h{level}><p>{e(s["description"])}</p><ul class="service-points">'+''.join('<li>'+e(c)+'</li>' for c in s['chips'])+'</ul>'+link('Explore '+s['name'],s['route'])+'</div></article>' for i,(key,s) in enumerate(services.items()))+'</div>'

    def section(label,title,body,style=''):
        return f'<section class="section {style}"><div class="wrap"><div class="section-heading"><div>{eyebrow(label)}<h2>{title}</h2></div></div>{body}</div></section>'

    def faq(questions, title='A few useful answers.'):
        return '<section class="section wrap"><div class="faq-layout"><div>'+eyebrow('Good questions')+'<h2>'+e(title)+'</h2></div><div class="faq">'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in questions)+'</div></div></section>'

    def journey():
        items=[('Understand','We get clear on your business, audience and goal.'),('Build','I put the agreed campaign, SEO plan or website together.'),('Refine','We review, test and improve the important details.')]
        return section('How it comes together','Clear steps.<br>A little curiosity.','<div class="process-grid">'+''.join(f'<article><span class="num">0{i+1}</span><h3>{a}</h3><p>{b}</p></article>' for i,(a,b) in enumerate(items))+'</div>','soft')

    def project_card(level=3):
        route='/'+site['ARTICLE']+'/'
        return f'<article class="project-feature" data-project><a class="project-art" href="{route}" aria-label="Read the Meta lead-generation practice project"><img src="/assets/meta-campaign.webp" width="1200" height="677" loading="lazy" alt="UrbanFit practice campaign structure in Meta Ads Manager"></a><div class="project-info"><span class="label">Practice project · Meta Ads</span><h{level}><a href="{route}">Meta Lead Campaign — From Start to Finish</a></h{level}><p>Explore the research, landing page, tracking and campaign decisions behind a complete practice campaign.</p><div class="project-tags"><span>Research</span><span>Landing page</span><span>Tracking</span></div>'+link('Read the project',route)+'<p class="project-note">A hypothetical fitness studio. A practical beginner-friendly project, not a client results claim.</p></div></article>'

    def home():
        hero='<section class="wrap hero"><div>'+eyebrow('Freelance digital marketer · India')+'<h1>Freelance digital marketer<br><span class="accent">for your business.</span></h1><p class="hero-tagline">Your business. Seen. Understood. Easy to choose.</p><p class="hero-copy">I’m Talha. I help small businesses in India with Google Ads, Meta Ads, SEO and websites that make getting in touch easy.</p><div class="button-row">'+button('Let’s talk','/contact/','btn-primary')+link('Explore my services','#services')+'</div><p class="hero-foot">One person. Direct communication. Based in India.</p></div>'+portrait()+'</section><div class="wrap focus-strip"><span>Google Ads</span><span>Meta Ads</span><span>Website Creation</span><span>SEO</span></div>'
        cards='<section class="section wrap" id="services"><div class="section-heading"><div>'+eyebrow('Four connected services')+'<h2>Digital marketing &amp;<br>website services.</h2></div><p>Reach the right people. Explain your offer. Make the next step clear.</p></div>'+service_cards()+'</section>'
        about='<section class="section wrap about-intro"><div>'+eyebrow('The person behind the work')+'<h2>A curious mind.<br><span class="accent">A practical approach.</span></h2></div><div><p class="large-copy">You work directly with me on your ads, website and the thinking behind them.</p><p>I’m a BBA student at Amity University with structured digital marketing training and hands-on practice in research, campaigns and conversion tracking. I start by understanding your business before choosing a channel or building a page.</p><div class="value-pills"><span>Research first</span><span>Clear communication</span><span>Thoughtful testing</span></div>'+link('Get to know me','/about/')+'</div></section>'
        work=section('Selected work','A closer look at the work.','<div class="project-list">'+site['hospital_card']()+project_card()+'</div>','soft')
        questions=[('Which service should I start with?','Start with the problem. Google Ads can reach people already searching, Meta Ads can introduce an offer, SEO improves the website’s organic search foundations, and website creation gives your services a clear home. We review your business before choosing a starting point.'),('What information will you need from me?','Your website, main services, real service areas, customer type, available assets and business goal are useful starting points. For advertising, we also discuss a test budget and how you respond to enquiries.'),('What is it like to work with you?','DigitalTalha is my personal brand. You work directly with me, with agreed scope, clear communication and reviews of what the available evidence shows.')]
        return hero+cards+about+work+journey()+faq(questions,'Choosing a useful next step.')

    def services_page():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Services')+eyebrow('Four connected services')+'<h1>Digital marketing.<br><span class="accent">Website creation.</span></h1><p>Google Ads, Meta Ads, SEO and websites for small businesses in India. Explore what each service includes and choose a useful starting point for your business.</p></div></section>'
        guide='<div class="scope-grid">'+''.join('<article><h3>'+e(s['name'])+'</h3><p>'+e(s['fit'])+'</p></article>' for s in services.values())+'</div>'
        return hero+'<section class="section wrap">'+service_cards(2)+'</section>'+section('Start with the business need','Which service fits your next step?',guide,'soft')+journey()

    def service_page(key):
        s=services[key]
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb(s['name'])+'<div class="service-hero"><div>'+eyebrow(s['name'])+'<h1>'+e(s['headline'])+'<br><span class="accent">'+e(s['accent'])+'</span></h1><p>'+e(s['intro'])+'</p><div class="button-row">'+button('Discuss my '+('website' if key=='website' else 'SEO' if key=='seo' else 'campaign'),'/contact/','btn-primary')+'</div><div class="value-pills">'+''.join('<span>'+e(c)+'</span>' for c in s['chips'])+'</div></div><figure class="service-visual">'+image(key,True)+'<figcaption>Illustration of '+e(s['name'])+' services</figcaption></figure></div></div></section>'
        intro='<section class="section wrap"><div class="narrative"><div>'+eyebrow('The starting point')+'<h2>'+('Search visibility starts with useful pages.' if key=='seo' else 'Your business goal comes first.')+'</h2></div><div class="prose"><p>'+e(s['overview'])+'</p><h3>Who is this for?</h3><p>'+e(s['fit'])+'</p></div></div></section>'
        scope=section('What the work covers','What’s included.','<div class="scope-grid">'+''.join('<article><h3>'+e(a)+'</h3><p>'+e(b)+'</p></article>' for a,b in s['includes'])+'</div>','soft')
        receive='<section class="section wrap"><div class="scope-layout"><div>'+eyebrow('Clear expectations')+'<h2>What you receive.</h2><ul class="check-list">'+''.join('<li>'+e(t)+'</li>' for t in s['receive'])+'</ul></div><div><h3>Before we begin</h3><p>'+e(s['prepare'])+'</p><p class="scope-note">'+e(s['note'])+'</p></div></div></section>'
        related='<section class="section-sm wrap related-services"><h2>Explore another service.</h2><div>'+''.join(link(t['name'],t['route']) for t in services.values() if t['name']!=s['name'])+'</div></section>'
        proof = ''
        if key == 'website':
            proof = site['hospital_feature']()
        elif key == 'search':
            example = [
                ('Group by service', 'For a sample plumbing campaign, keep emergency repairs and planned installations in separate ad groups. Each group can use its own ad and relevant service page.'),
                ('Review search terms', 'Check whether searches match work the business can take. Exclude clearly unrelated terms such as jobs or training when the report shows them.'),
                ('Check the enquiry', 'Test the mobile call button and form. Track a completed enquiry separately from a button click so the campaign can be reviewed against meaningful actions.')
            ]
            proof = section('Worked example', 'What a search campaign plan looks like.',
                            '<p class="section-intro">An illustrative setup for a plumbing business.</p><div class="scope-grid">'+
                            ''.join(f'<article><h3>{e(title)}</h3><p>{e(body)}</p></article>' for title, body in example)+'</div>')
        elif key == 'social':
            proof = section('Practice campaign', 'See how a Meta lead campaign is planned.', project_card())
        elif key == 'seo':
            proof = section('From the portfolio', 'How a hospital organised its service pages.',
                            '<p class="section-intro">The Glisan Akbari project shows how a urology department page connects to a focused kidney stone page. Each page answers a different question and links to the next step for patients.</p>'
                            +link('See the hospital website and SEO work',site['HOSPITAL_PROJECT']['route']))
        return hero+intro+proof+scope+receive+journey()+faq(s['faqs'])+related

    def about():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('About')+'<div class="page-hero-grid"><div>'+eyebrow('Talha Alam · DigitalTalha')+'<h1>About Talha Alam.<br><span class="accent">Your digital marketer.</span></h1><p>I’m Talha, a freelance digital marketer and BBA student at Amity University. DigitalTalha is my personal brand, built around research, testing and honest communication.</p><p>Paid advertising is my main focus. Website creation and SEO connect that work with a clearer home for your services and a useful path from search to enquiry.</p><div class="button-row">'+button('Explore my work','/blog/','btn-primary')+'</div></div>'+portrait()+'</div></div></section>'
        story=[('A spark in Class 12','My interest in marketing began with something I came across online during Class 12. Curiosity led me to blogs, videos and books, including Philip Kotler’s Marketing Management and Seth Godin’s work.'),('A structured foundation','I wanted a connected understanding of marketing, so I researched courses and chose the three-month UT Digital Media programme by Umar Tazkeer. Alongside my BBA studies, it gave me a foundation to keep building on.'),('Turning learning into practice','I practised keyword and audience research, campaign structure, ad copy, budget planning, landing-page analysis and conversion tracking with GA4 and Google Tag Manager. The work taught me to connect the customer, the message and the action being measured.'),('Building DigitalTalha','I created DigitalTalha to give that work a name and a home. It is a solo personal brand: when you work with me, you work directly with me. My aim is to keep improving through useful work and evidence, without inflated claims.')]
        background=section('My journey','From curiosity to practical work.','<div class="timeline">'+''.join(f'<article><span class="num">0{i+1}</span><div><h3>{a}</h3><p>{b}</p></div></article>' for i,(a,b) in enumerate(story))+'</div>')
        thinking=section('How I think about the work','Understand the problem.<br>Then choose the approach.','<div class="narrative"><p class="large-copy">Advertising should make a useful solution easy to understand.</p><div class="prose"><p>Before writing an ad or planning a page, I want to understand the audience, the problem they have, what they care about and why they would choose one solution over another.</p><p>A campaign, a website and an SEO plan all need that foundation. I review the available evidence, explain what it means and use it to decide what needs changing. The first version is a starting point to learn from.</p></div></div>','soft')
        skills=['Keyword research','Audience research','Competitor research','Google Ads','Meta Ads','Ad copywriting','Landing-page analysis','Conversion tracking','Google Analytics 4','Google Tag Manager','Meta Pixel','Budget planning','A/B testing','Campaign optimisation','Website structure','On-page SEO']
        practice=section('Skills & focus','The practical work behind the services.','<p class="section-intro">My foundation is in paid search and paid social, supported by website and search work. These are areas I study and put into practice; this list is not a claim of certification or client results.</p><ul class="skill-tags">'+''.join('<li>'+e(t)+'</li>' for t in skills)+'</ul><div class="button-row">'+link('Explore Google Ads','/google-ads/')+link('Explore Meta Ads','/meta-ads/')+link('Explore SEO','/seo/')+link('Explore Website Creation','/website-creation/')+'</div>')
        principles=[('Research before execution','Understand the business, audience and offer before making a recommendation.'),('Clear communication','Explain what is happening and why, in plain language.'),('Testing over guessing','Use structured tests and available data instead of treating assumptions as facts.'),('Honest reporting','Discuss what is working, what is not, and what still needs evidence.'),('Direct involvement','Work with me throughout the agreed project, from the first brief to review.'),('Continuous improvement','Keep learning from the work and use that learning to improve the next version.')]
        expectations=section('What you can expect','A direct, thoughtful working relationship.','<div class="scope-grid">'+''.join('<article><h3>'+a+'</h3><p>'+b+'</p></article>' for a,b in principles)+'</div>','soft')
        return hero+background+thinking+practice+expectations

    def contact():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Contact')+eyebrow('Let’s talk')+'<h1>Contact Talha.<br><span class="accent">Plan your next step.</span></h1><p>A website, an ad campaign, SEO, or a question about where to start. Share your business, the service you need and what you want to improve.</p></div></section>'
        form=original_form('general',compact=True)
        return hero+'<section class="section contact-section" id="contact"><div class="wrap contact-layout"><div class="contact-intro"><h2>A simple first step.</h2><p>Tell me about your business and what you need. I’ll review it personally.</p>'+'<p class="form-note">I’ll reply using the email address you provide.</p></div>'+form+'</div></section>'

    def projects():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Projects')+eyebrow('Projects & practical work')+'<h1>Marketing projects.<br><span class="accent">The thinking behind them.</span></h1><p>A live hospital website and a documented practice campaign. Explore the planning, decisions and work behind each.</p></div></section>'
        listing='<section class="section wrap"><div class="project-tools"><label class="search-box"><span aria-hidden="true">⌕</span><input type="search" placeholder="Search projects or topics…" aria-label="Search projects" data-project-search></label><span class="label">Websites · Campaigns · Research</span></div><p class="search-result" data-search-result role="status">2 projects found</p><div class="project-list">'+site['hospital_card'](2)+project_card(2)+'</div></section>'
        return hero+listing

    site.update(home=home,services=services_page,service=lambda path,name:service_page('search' if name=='Google Ads' else 'social'),website_creation=lambda:service_page('website'),seo_service=lambda:service_page('seo'),about=about,contact=contact,projects=projects,service_cards=service_cards,project_card=project_card)
