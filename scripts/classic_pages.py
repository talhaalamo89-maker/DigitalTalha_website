"""Minimal, content-led marketing pages; all information is rendered as HTML."""
from html import escape
from cms_content import asset_info, attribute, copy_text, copy_value, load_services
import posts

from seo import PORTRAIT_SIZES, PORTRAIT_SRC, PORTRAIT_SRCSET


def install(site):
    from portfolio import install as install_portfolio
    install_portfolio(site)
    e = lambda value: escape(str(value), quote=True)
    eyebrow, button, link = (site[k] for k in ['eyebrow', 'button', 'link'])
    breadcrumb, original_form = (site[k] for k in ['breadcrumb', 'form'])
    services = load_services()

    def portrait(path):
        _, width, height, _ = asset_info(PORTRAIT_SRC)
        responsive = f' srcset="{PORTRAIT_SRCSET}" sizes="{PORTRAIT_SIZES[path]}"' if PORTRAIT_SRCSET else ''
        return (f'<figure class="profile"><img src="{PORTRAIT_SRC}"{responsive} '
                f'width="{width}" height="{height}" alt="{attribute("profile", "alt")}" fetchpriority="high">'
                f'<figcaption><strong>{copy_text("profile", "name")}</strong>'
                f'<span>{copy_text("profile", "caption")}</span></figcaption></figure>')

    def image(key, eager=False):
        s = services[key]
        path, width, height, _ = asset_info(s["image"])
        return f'<img src="{path}" width="{width}" height="{height}" alt="{e(s["alt"])}" '+('fetchpriority="high"' if eager else 'loading="lazy"')+' decoding="async">'

    def service_cards(level=3, prioritize_first=False):
        return '<div class="services-grid">'+''.join(f'<article class="service-card"><a class="service-art" href="{s["route"]}" aria-label="Explore {e(s["name"])}">{image(key, eager=prioritize_first and i == 0)}</a><div class="service-card-copy"><p class="label">0{i+1} / {e(s["tag"])}</p><h{level}><a href="{s["route"]}">{e(s["name"])}</a></h{level}><p>{e(s["description"])}</p><ul class="service-points">'+''.join('<li>'+e(c)+'</li>' for c in s['chips'])+'</ul>'+link('Explore '+s['name'],s['route'])+'</div></article>' for i,(key,s) in enumerate(services.items()))+'</div>'

    def section(label,title,body,style=''):
        return f'<section class="section {style}"><div class="wrap"><div class="section-heading"><div>{eyebrow(label)}<h2>{title}</h2></div></div>{body}</div></section>'

    def faq(questions, title=None):
        title = title or copy_value('service-layout', 'faq_heading')
        return '<section class="section wrap"><div class="faq-layout"><div>'+eyebrow(copy_value('service-layout', 'faq_eyebrow'))+'<h2>'+e(title)+'</h2></div><div class="faq">'+''.join('<details><summary>'+e(q)+'</summary><p>'+e(a)+'</p></details>' for q,a in questions)+'</div></div></section>'

    def journey():
        items=[(row['heading'], row['description']) for row in copy_value('process', 'items')]
        return section(copy_value('process', 'how_it_comes_together'),copy_text('process', 'clear_steps') + '<br>' + copy_text('process', 'a_little_curiosity'),'<div class="process-grid">'+''.join(f'<article><span class="num">0{i+1}</span><h3>{e(a)}</h3><p>{e(b)}</p></article>' for i,(a,b) in enumerate(items))+'</div>','soft')

    def project_card(level=3):
        route='/'+site['ARTICLE']+'/'
        image, width, height, _ = asset_info(copy_value('campaign-card', 'image'))
        return f'<article class="project-feature" data-project><a class="project-art" href="{route}" aria-label="Read the Meta lead-generation practice project"><img src="{image}" width="{width}" height="{height}" loading="lazy" alt="{attribute('campaign-card', 'urbanfit_practice_campaign_structure_in')}"></a><div class="project-info"><span class="label">{copy_text('campaign-card', 'practice_project_meta_ads')}</span><h{level}><a href="{route}">{copy_text('campaign-card', 'meta_lead_generation_campaign_guide')}</a></h{level}><p>{copy_text('campaign-card', 'explore_the_research_landing_page')}</p><div class="project-tags"><span>{copy_text('campaign-card', 'research')}</span><span>{copy_text('campaign-card', 'landing_page')}</span><span>{copy_text('campaign-card', 'tracking')}</span></div>'+link(copy_value('campaign-card', 'read_the_project'),route)+('<p class="project-note">' + copy_text('campaign-card', 'a_hypothetical_fitness_studio_a') + '</p></div></article>')

    def home():
        hero='<section class="wrap hero"><div>'+eyebrow(copy_value('home', 'talha_alam_india'))+('<h1>' + copy_text('home', 'freelance_digital_marketer') + '<br> <span class="accent">' + copy_text('home', 'for_small_businesses') + '</span></h1><p class="hero-tagline">' + copy_text('home', 'help_more_customers_find_you') + '</p><p class="hero-copy">' + copy_text('home', 'i_m_talha_alam_i') + '</p><div class="button-row">')+button(copy_value('home', 'let_s_talk'),'/contact/','btn-primary')+link(copy_value('home', 'explore_my_services'),'#services')+('</div><p class="hero-foot">' + copy_text('home', 'work_directly_with_me_from') + '</p></div>')+portrait('/')+('</section><div class="wrap focus-strip"><span>' + copy_text('home', 'google_ads') + '</span><span>' + copy_text('home', 'meta_ads') + '</span><span>' + copy_text('home', 'website_creation') + '</span><span>' + copy_text('home', 'seo') + '</span></div>')
        cards='<section class="section wrap" id="services"><div class="section-heading"><div>'+eyebrow(copy_value('home', 'four_connected_services'))+('<h2>' + copy_text('home', 'digital_marketing') + '<br>' + copy_text('home', 'website_services') + '</h2></div><p>' + copy_text('home', 'reach_the_right_people_explain') + '</p></div>')+service_cards()+'</section>'
        about='<section class="section wrap about-intro"><div>'+eyebrow(copy_value('home', 'the_person_behind_the_work'))+('<h2>' + copy_text('home', 'a_curious_mind') + '<br> <span class="accent">' + copy_text('home', 'a_practical_approach') + '</span></h2></div><div><p class="large-copy">' + copy_text('home', 'you_work_directly_with_me') + '</p><p>' + copy_text('home', 'i_m_a_bba_student') + '</p><div class="value-pills"><span>' + copy_text('home', 'research_first') + '</span><span>' + copy_text('home', 'clear_communication') + '</span><span>' + copy_text('home', 'thoughtful_testing') + '</span></div>')+link(copy_value('home', 'get_to_know_me'),'/about/')+'</div></section>'
        work=section(copy_value('home', 'selected_work'),copy_text('home', 'digital_marketing_and_website_projects'),'<div class="project-list">'+site['hospital_card']()+project_card()+'</div>','soft')
        questions=[(row['question'], row['answer']) for row in copy_value('home', 'questions')]
        return hero+cards+about+work+journey()+faq(questions,copy_value('home', 'faq_heading'))

    def services_page():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Services')+('<h1>' + copy_text('services-overview', 'digital_marketing') + '<br> <span class="accent">' + copy_text('services-overview', 'website_design_services') + '</span></h1><p>' + copy_text('services-overview', 'compare_google_ads_meta_ads') + '</p></div></section>')
        guide='<div class="scope-grid">'+''.join('<article><h3>'+e(s['name'])+'</h3><p>'+e(s['fit'])+'</p></article>' for s in services.values())+'</div>'
        return hero+'<section class="section wrap">'+service_cards(2, prioritize_first=True)+'</section>'+section(copy_value('services-overview', 'start_with_the_business_need'),copy_text('services-overview', 'which_service_fits_your_next'),guide,'soft')+journey()

    def service_page(key):
        s=services[key]
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb(s['name'])+'<div class="service-hero"><div>'+eyebrow(s['name'])+'<h1>'+e(s['headline'])+'<br> <span class="accent">'+e(s['accent'])+'</span></h1><p>'+e(s['intro'])+'</p><div class="button-row">'+button('Discuss my '+('website' if key=='website' else 'SEO' if key=='seo' else 'campaign'),'/contact/','btn-primary')+'</div><div class="value-pills">'+''.join('<span>'+e(c)+'</span>' for c in s['chips'])+'</div></div><figure class="service-visual">'+image(key,True)+'<figcaption>Illustration of '+e(s['name'])+' services</figcaption></figure></div></div></section>'
        intro='<section class="section wrap"><div class="narrative"><div>'+eyebrow(copy_value('service-layout', 'the_starting_point'))+'<h2>'+copy_text('service-layout', 'seo_intro_heading' if key=='seo' else 'intro_heading')+'</h2></div><div class="prose"><p>'+e(s['overview'])+('</p><h3>' + copy_text('service-layout', 'who_is_this_for') + '</h3><p>')+e(s['fit'])+'</p></div></div></section>'
        scope=section(copy_value('service-layout', 'what_the_work_covers'),copy_text('service-layout', 'what_s_included'),'<div class="scope-grid">'+''.join('<article><h3>'+e(a)+'</h3><p>'+e(b)+'</p></article>' for a,b in ((row["heading"], row["description"]) for row in s["includes"]))+'</div>','soft')
        receive='<section class="section wrap"><div class="scope-layout"><div>'+eyebrow(copy_value('service-layout', 'clear_expectations'))+('<h2>' + copy_text('service-layout', 'what_you_receive') + '</h2><ul class="check-list">')+''.join('<li>'+e(t)+'</li>' for t in s['receive'])+('</ul></div><div><h3>' + copy_text('service-layout', 'before_we_begin') + '</h3><p>')+e(s['prepare'])+'</p><p class="scope-note">'+e(s['note'])+'</p></div></div></section>'
        related=('<section class="section-sm wrap related-services"><h2>' + copy_text('service-layout', 'explore_another_service') + '</h2><div>')+''.join(link(t['name'],t['route']) for t in services.values() if t['route']!=s['route'])+'</div></section>'
        proof = ''
        if key == 'website':
            proof = site['hospital_feature']()
        elif key == 'search':
            example = [(row['heading'], row['description']) for row in copy_value('service-layout', 'example')]
            proof = section(copy_value('service-layout', 'worked_example'), copy_text('service-layout', 'what_a_search_campaign_plan'),
                            ('<p class="section-intro">' + copy_text('service-layout', 'an_illustrative_setup_for_a') + '</p><div class="scope-grid">')+
                            ''.join(f'<article><h3>{e(title)}</h3><p>{e(body)}</p></article>' for title, body in example)+'</div>')
        elif key == 'social':
            proof = section(copy_value('service-layout', 'practice_campaign'), copy_text('service-layout', 'see_how_a_meta_lead'), project_card())
        elif key == 'seo':
            proof = section(copy_value('service-layout', 'from_the_portfolio'), copy_text('service-layout', 'how_a_hospital_organised_its'),
                            ('<p class="section-intro">' + copy_text('service-layout', 'the_glisan_akbari_project_shows') + '</p>')
                            +link(copy_value('service-layout', 'see_the_hospital_website_and'),site['HOSPITAL_PROJECT']['route']))
        return hero+intro+proof+scope+receive+journey()+faq([(row['question'], row['answer']) for row in s['faqs']])+related

    def about():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('About')+'<div class="page-hero-grid"><div>'+eyebrow(copy_value('about', 'talha_alam_digitaltalha'))+('<h1>' + copy_text('about', 'about_talha_alam') + '<br> <span class="accent">' + copy_text('about', 'your_digital_marketer') + '</span></h1><p>' + copy_text('about', 'i_m_talha_a_freelance') + '</p><p>' + copy_text('about', 'paid_advertising_is_my_main') + '</p><div class="button-row">')+button(copy_value('about', 'explore_my_work'),'/blog/','btn-primary')+'</div></div>'+portrait('/about/')+'</div></div></section>'
        story=[(row['heading'], row['description']) for row in copy_value('about', 'story')]
        background=section(copy_value('about', 'my_journey'),copy_text('about', 'from_curiosity_to_practical_work'),'<div class="timeline">'+''.join(f'<article><span class="num">0{i+1}</span><div><h3>{e(a)}</h3><p>{e(b)}</p></div></article>' for i,(a,b) in enumerate(story))+'</div>')
        thinking=section(copy_value('about', 'how_i_think_about_the'),copy_text('about', 'understand_the_problem') + '<br>' + copy_text('about', 'then_choose_the_approach'),('<div class="narrative"><p class="large-copy">' + copy_text('about', 'advertising_should_make_a_useful') + '</p><div class="prose"><p>' + copy_text('about', 'before_writing_an_ad_or') + '</p><p>' + copy_text('about', 'a_campaign_a_website_and') + '</p></div></div>'),'soft')
        skills=copy_value('about', 'skills')
        practice=section(copy_value('about', 'skills_focus'),copy_text('about', 'the_practical_work_behind_the'),('<p class="section-intro">' + copy_text('about', 'my_foundation_is_in_paid') + '</p><ul class="skill-tags">')+''.join('<li>'+e(t)+'</li>' for t in skills)+'</ul><div class="button-row">'+link(copy_value('about', 'explore_google_ads'),'/google-ads/')+link(copy_value('about', 'explore_meta_ads'),'/meta-ads/')+link(copy_value('about', 'explore_seo'),'/seo/')+link(copy_value('about', 'explore_website_creation'),'/website-creation/')+'</div>')
        principles=[(row['heading'], row['description']) for row in copy_value('about', 'principles')]
        expectations=section(copy_value('about', 'what_you_can_expect'),copy_text('about', 'a_direct_thoughtful_working_relationship'),'<div class="scope-grid">'+''.join('<article><h3>'+a+'</h3><p>'+b+'</p></article>' for a,b in principles)+'</div>','soft')
        return hero+background+thinking+practice+expectations

    def contact():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Contact')+('<h1>' + copy_text('contact', 'contact_talha_alam') + '<br> <span class="accent">' + copy_text('contact', 'about_your_project') + '</span></h1><p>' + copy_text('contact', 'a_website_an_ad_campaign') + '</p></div></section>')
        form=original_form('general',compact=True)
        return hero+('<section class="section contact-section" id="contact"><div class="wrap contact-layout"><div class="contact-intro"><h2>' + copy_text('contact', 'a_simple_first_step') + '</h2><p>' + copy_text('contact', 'tell_me_what_your_business') + '</p>')+('<p class="form-note">' + copy_text('contact', 'i_ll_reply_using_the') + '</p></div>')+form+'</div></section>'

    def projects():
        hero='<section class="page-hero"><div class="wrap">'+breadcrumb('Projects')+('<h1>' + copy_text('projects', 'digital_marketing') + '<br> <span class="accent">' + copy_text('projects', 'website_projects') + '</span></h1><p>' + copy_text('projects', 'see_how_the_purnea_hospital') + '</p></div></section>')
        listing=('<section class="section wrap"><div class="project-tools"><label class="search-box"><span aria-hidden="true">⌕</span><input type="search" placeholder="' + attribute('projects', 'search_projects_or_topics') + '" aria-label="Search projects" data-project-search></label><span class="label">' + copy_text('projects', 'websites_campaigns_research') + '</span></div><p class="search-result" data-search-result role="status">' + f'{2 + len(site["POSTS"])} projects found' + '</p><div class="project-list">')+site['hospital_card'](2)+project_card(2)+posts.cards(site['POSTS'])+'</div></section>'
        return hero+listing

    site.update(home=home,services=services_page,service=lambda path,name:service_page('search' if name=='Google Ads' else 'social'),website_creation=lambda:service_page('website'),seo_service=lambda:service_page('seo'),about=about,contact=contact,projects=projects,service_cards=service_cards,project_card=project_card)
