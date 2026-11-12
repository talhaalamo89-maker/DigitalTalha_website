"""Hospital portfolio: real screenshots, a defined role and ongoing SEO status."""
from html import escape
from pathlib import Path
import json

PROJECT = json.loads((Path(__file__).resolve().parents[1] / 'content/hospital-project.json').read_text())


def install(site):
    e = lambda value: escape(str(value), quote=True)
    p = PROJECT
    eyebrow, button, link = (site[k] for k in ['eyebrow', 'button', 'link'])

    def screenshot(kind, eager=False):
        shot = p[kind]
        priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
        return f'<img src="/assets/{e(shot["file"])}" width="{shot["width"]}" height="{shot["height"]}" alt="{e(shot["alt"])}" {priority} decoding="async">'

    def live_link(label='Visit live website', url=None):
        return f'<a class="text-link" href="{e(url or p["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{e(label)} (opens in a new tab)">{e(label)} <span aria-hidden="true">↗</span></a>'

    def status():
        return '<div class="project-status"><span class="live-status">Live website</span><span>SEO ongoing</span></div>'

    def stage():
        return '<div class="hospital-stage"><div class="hospital-browser"><div class="hospital-browser-bar"><span aria-hidden="true">● ● ●</span><span>glisanhospitalpurnia.in</span><span aria-hidden="true">↗</span></div>'+screenshot('desktop')+'</div><div class="hospital-phone">'+screenshot('mobile')+'</div><span class="stage-label">DESKTOP + MOBILE</span></div>'

    def hospital_card(level=3):
        return '<article class="hospital-feature" data-project><div class="hospital-feature-art"><a href="'+p['route']+'" aria-label="View the Glisan Akbari hospital website project">'+stage()+'</a></div><div class="hospital-feature-copy"><p class="label">Healthcare · Website project</p>'+status()+f'<h{level}><a href="{p["route"]}">Glisan Akbari<br>Super Speciality Hospital.</a></h{level}><p>'+e(p['summary'])+'</p><div class="project-tags"><span>Website planning</span><span>AI-assisted build</span><span>SEO direction</span></div><div class="button-row">'+button('View project',p['route'],'btn-primary')+live_link()+'</div><p class="hospital-credit">Planning and review by Talha Alam.<br>Built with ChatGPT and Codex.</p></div></article>'

    def hospital_feature():
        return '<section class="section wrap work-proof" id="website-project"><div class="section-heading"><div>'+eyebrow('Selected website project')+'<h2>A real website.<br>A closer look.</h2></div><p>Explore the live work and the thinking behind it.</p></div>'+hospital_card()+'</section>'

    def hospital_project():
        hero='<section class="page-hero case-hero"><div class="wrap">'+site['seo_breadcrumb'](p['route'],site['SEO'])+'<div class="case-hero-grid"><div>'+eyebrow('Healthcare website · Purnea, Bihar')+'<h1>Glisan Akbari.<br><span class="accent">A clearer path to care.</span></h1><p class="case-hospital-name">'+e(p['name'])+'</p><p class="case-intro">'+e(p['summary'])+'</p><div class="button-row">'+live_link()+link('Explore the work','#project-overview')+'</div></div><aside class="case-role">'+status()+'<span class="label">My contribution</span><h2>Plan. Direct.<br>Review. Refine.</h2><p>'+e(p['role'])+'</p><p class="case-build-note">Built with ChatGPT and Codex.<br>'+e(p['context'])+'</p></aside></div></div></section>'
        showcase='<section class="case-showcase wrap" aria-label="Desktop and mobile website screenshots">'+stage()+'<p class="screenshot-caption">Actual live-site screenshots · '+e(p['captured_label'])+'. The live website may change.</p></section>'
        overview='<section class="section wrap" id="project-overview"><div class="case-overview"><div>'+eyebrow('The website goal')+'<h2>Help visitors find<br>their next step.</h2><p>'+e(p['goal'])+'</p></div><div>'+eyebrow('My role in the work')+'<h2>Marketing thinking.<br>AI-assisted execution.</h2><p>'+e(p['role_description'])+'</p><p>I guided what to build, how the information should connect and what needed another review. The work includes planning, SEO direction and quality review.</p></div></div></section>'
        decisions='<section class="section soft"><div class="wrap"><div class="section-heading"><div>'+eyebrow('Inside the approach')+'<h2>The decisions behind the pages.</h2></div></div><div class="case-decisions">'+''.join(f'<article><span class="num">0{i+1}</span><h3>{e(title)}</h3><p>{e(description)}</p></article>' for i,(title,description) in enumerate(p['decisions']))+'</div></div></section>'
        detail='<section class="section wrap"><div class="case-detail"><div>'+eyebrow('One journey, connected')+'<h2>From a department<br>to a specific concern.</h2><p>The urology page links to dedicated care topics. The kidney stone page brings together focused information, doctor details and consultation options.</p><p>This is the structure in practice: help visitors explore, understand and find a way to contact the hospital.</p>'+live_link('Explore the service page',p['service_url'])+'</div><figure class="case-detail-shot">'+screenshot('detail')+'<figcaption>A dedicated service page on the live hospital website.</figcaption></figure></div></section>'
        seo='<section class="section soft"><div class="wrap case-seo"><div>'+eyebrow('Current project status')+'<h2>Website live.<br><span class="accent">SEO in progress.</span></h2><p class="case-status-date">Status recorded '+e(p['captured_label'])+'</p></div><div><p>'+e(p['seo_description'])+'</p><div class="case-seo-foundations"><span>Page titles & descriptions</span><span>Headings & service content</span><span>Connected care pages</span></div><p class="case-evidence-note">'+e(p['seo_note'])+'</p></div></div></section>'
        cta='<section class="section wrap"><div class="case-cta"><div>'+eyebrow('Your website, next')+'<h2>Make your services<br>easier to understand.</h2><p>Let’s plan a website around your business, your visitors and the next step you want them to take.</p></div><div class="case-cta-actions">'+button('Discuss your website','/contact/','btn-primary')+link('Website design and development','/website-creation/')+link('SEO services','/seo/')+link('All projects','/blog/')+'</div></div></section>'
        return hero+showcase+overview+decisions+detail+seo+cta

    site.update(HOSPITAL_PROJECT=p,hospital_card=hospital_card,hospital_feature=hospital_feature,hospital_project=hospital_project)
