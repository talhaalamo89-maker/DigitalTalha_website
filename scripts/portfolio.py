"""Hospital portfolio: real screenshots, a defined role and ongoing SEO status."""
from html import escape
from cms_content import asset_info, attribute, copy_text, copy_value
from urllib.parse import urlsplit
from cms_content import read_json

PROJECT = read_json('hospital-project.json')


def install(site):
    e = lambda value: escape(str(value), quote=True)
    p = PROJECT
    for field in ('url', 'service_url'):
        address = urlsplit(p[field])
        if address.scheme != 'https' or not address.hostname or any(ch.isspace() for ch in p[field]):
            raise ValueError(f'Hospital project {field} must be an HTTPS URL')
    eyebrow, button, link = (site[k] for k in ['eyebrow', 'button', 'link'])

    def screenshot(kind, eager=False):
        shot = p[kind]
        priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
        path, width, height, _ = asset_info(shot["file"])
        return f'<img src="{path}" width="{width}" height="{height}" alt="{e(shot["alt"])}" {priority} decoding="async">'

    def live_link(label='Visit live website', url=None):
        return f'<a class="text-link" href="{e(url or p["url"])}" target="_blank" rel="noopener noreferrer" aria-label="{e(label)} (opens in a new tab)">{e(label)} <span aria-hidden="true">↗</span></a>'

    def status():
        return ('<div class="project-status"><span class="live-status">' + copy_text('hospital-copy', 'live_website') + '</span><span>' + copy_text('hospital-copy', 'seo_ongoing') + '</span></div>')

    def stage():
        return ('<div class="hospital-stage"><div class="hospital-browser"><div class="hospital-browser-bar"><span aria-hidden="true">● ● ●</span><span>' + copy_text('hospital-copy', 'glisanhospitalpurnia_in') + '</span><span aria-hidden="true">↗</span></div>')+screenshot('desktop')+'</div><div class="hospital-phone">'+screenshot('mobile')+('</div><span class="stage-label">' + copy_text('hospital-copy', 'desktop_mobile') + '</span></div>')

    def hospital_card(level=3):
        route = e(p['route'])
        return (
            '<article class="hospital-feature" data-project><div class="hospital-feature-copy">'
            f'<p class="label">{copy_text("hospital-copy", "healthcare_website_purnea_bihar")}</p>'
            f'<h{level}>{copy_text("hospital-copy", "glisan_akbari")} '
            f'{copy_text("hospital-copy", "super_speciality_hospital")}</h{level}>'
            f'<p>{e(p["summary"])}</p>{status()}<div class="button-row">'
            f'{button(copy_value("hospital-copy", "view_project"), route, "btn-outline")}{live_link()}</div>'
            f'<p class="hospital-credit">{copy_text("hospital-copy", "planning_and_review_by_talha")} '
            f'{copy_text("hospital-copy", "built_with_chatgpt_and_codex")}</p></div>'
            f'<div class="hospital-feature-art" data-reveal><a href="{route}" '
            f'aria-label="View the Glisan Akbari hospital website project">{stage()}</a></div></article>'
        )

    def hospital_feature():
        return '<section class="section wrap work-proof" id="website-project"><div class="section-heading"><div>'+eyebrow(copy_value('hospital-copy', 'selected_website_project'))+('<h2>' + copy_text('hospital-copy', 'a_real_website') + '<br>' + copy_text('hospital-copy', 'a_closer_look') + '</h2></div><p>' + copy_text('hospital-copy', 'explore_the_live_work_and') + '</p></div>')+hospital_card()+'</section>'

    def hospital_project():
        hero='<section class="page-hero case-hero"><div class="wrap">'+site['seo_breadcrumb'](p['route'],site['SEO'])+'<div class="case-hero-grid"><div>'+eyebrow(copy_value('hospital-copy', 'healthcare_website_purnea_bihar'))+('<h1>' + copy_text('hospital-copy', 'glisan_akbari_hospital') + '<br> <span class="accent">' + copy_text('hospital-copy', 'website_project') + '</span></h1><p class="case-hospital-name">')+e(p['name'])+'</p><p class="case-intro">'+e(p['summary'])+'</p><div class="button-row">'+live_link()+link(copy_value('hospital-copy', 'explore_the_work'),'#project-overview')+'</div></div><aside class="case-role">'+status()+('<span class="label">' + copy_text('hospital-copy', 'my_contribution') + '</span><h2>' + copy_text('hospital-copy', 'plan_direct') + '<br>' + copy_text('hospital-copy', 'review_refine') + '</h2><p>')+e(p['role'])+('</p><p class="case-build-note">' + copy_text('hospital-copy', 'built_with_chatgpt_and_codex') + '<br>')+e(p['context'])+'</p></aside></div></div></section>'
        showcase='<section class="case-showcase wrap" aria-label="Desktop and mobile website screenshots">'+stage()+'<p class="screenshot-caption">Actual live-site screenshots · '+e(p['captured_label'])+'. The live website may change.</p></section>'
        overview='<section class="section wrap" id="project-overview"><div class="case-overview"><div>'+eyebrow(copy_value('hospital-copy', 'the_website_goal'))+('<h2>' + copy_text('hospital-copy', 'help_visitors_find') + '<br>' + copy_text('hospital-copy', 'their_next_step') + '</h2><p>')+e(p['goal'])+'</p></div><div>'+eyebrow(copy_value('hospital-copy', 'my_role_in_the_work'))+('<h2>' + copy_text('hospital-copy', 'marketing_thinking') + '<br>' + copy_text('hospital-copy', 'ai_assisted_execution') + '</h2><p>')+e(p['role_description'])+('</p><p>' + copy_text('hospital-copy', 'i_guided_what_to_build') + '</p></div></div></section>')
        decisions='<section class="section soft"><div class="wrap"><div class="section-heading"><div>'+eyebrow(copy_value('hospital-copy', 'inside_the_approach'))+('<h2>' + copy_text('hospital-copy', 'the_decisions_behind_the_pages') + '</h2></div></div><div class="case-decisions">')+''.join(f'<article><span class="num">0{i+1}</span><h3>{e(title)}</h3><p>{e(description)}</p></article>' for i,(title,description) in enumerate((row['heading'], row['description']) for row in p['decisions']))+'</div></div></section>'
        detail='<section class="section wrap"><div class="case-detail"><div>'+eyebrow(copy_value('hospital-copy', 'one_journey_connected'))+('<h2>' + copy_text('hospital-copy', 'from_a_department') + '<br>' + copy_text('hospital-copy', 'to_a_specific_concern') + '</h2><p>' + copy_text('hospital-copy', 'the_urology_page_links_to') + '</p><p>' + copy_text('hospital-copy', 'this_is_the_structure_in') + '</p>')+live_link('Explore the service page',p['service_url'])+'</div><figure class="case-detail-shot">'+screenshot('detail')+('<figcaption>' + copy_text('hospital-copy', 'a_dedicated_service_page_on') + '</figcaption></figure></div></section>')
        seo='<section class="section soft"><div class="wrap case-seo"><div>'+eyebrow(copy_value('hospital-copy', 'current_project_status'))+('<h2>' + copy_text('hospital-copy', 'website_live') + '<br><span class="accent">' + copy_text('hospital-copy', 'seo_in_progress') + '</span></h2><p class="case-status-date">Status recorded ')+e(p['captured_label'])+'</p></div><div><p>'+e(p['seo_description'])+('</p><div class="case-seo-foundations"><span>' + copy_text('hospital-copy', 'page_titles_descriptions') + '</span><span>' + copy_text('hospital-copy', 'headings_service_content') + '</span><span>' + copy_text('hospital-copy', 'connected_care_pages') + '</span></div><p class="case-evidence-note">')+e(p['seo_note'])+'</p></div></div></section>'
        cta='<section class="section wrap"><div class="case-cta"><div>'+eyebrow(copy_value('hospital-copy', 'your_website_next'))+('<h2>' + copy_text('hospital-copy', 'make_your_services') + '<br>' + copy_text('hospital-copy', 'easier_to_understand') + '</h2><p>' + copy_text('hospital-copy', 'let_s_plan_a_website') + '</p></div><div class="case-cta-actions">')+button(copy_value('hospital-copy', 'discuss_your_website'),'/contact/','btn-primary')+link(copy_value('hospital-copy', 'website_design_and_development'),'/website-creation/')+link(copy_value('hospital-copy', 'seo_services'),'/seo/')+link(copy_value('hospital-copy', 'all_projects'),'/projects/')+'</div></div></section>'
        return hero+showcase+overview+decisions+detail+seo+cta

    site.update(HOSPITAL_PROJECT=p,hospital_card=hospital_card,hospital_feature=hospital_feature,hospital_project=hospital_project)
