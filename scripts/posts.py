"""Validate Git-backed blog entries and render published Markdown to static pages."""
from datetime import date
from html import escape
import re

from cms_content import ROOT, asset_info, copy_text, read_json

BLOG_PATH = '/blog/'
POST_DIRECTORY = ROOT / 'content/posts'


def load_posts():
    posts = {}
    for path in POST_DIRECTORY.glob('*.json'):
        slug = path.stem
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError(f'Invalid blog filename: {path.name}')
        post = read_json(f'posts/{path.name}')
        if post.get('draft', True) is True:
            continue
        if post['draft'] is not False:
            raise ValueError(f'{path.name}: draft must be true or false')
        for field in ('title', 'summary', 'seo_title', 'seo_description', 'body'):
            if not isinstance(post.get(field), str) or not post[field].strip():
                raise ValueError(f'{path.name}: {field} is required to publish')
        post['date'] = date.fromisoformat(post['date']).isoformat()
        if post.get('image'):
            asset_info(post['image'])
            if not post.get('image_alt', '').strip():
                raise ValueError(f'{path.name}: enter alt text for the cover image')
        posts[f'{BLOG_PATH}{slug}/'] = post
    return dict(sorted(posts.items(), key=lambda item: (item[1]['date'], item[0]), reverse=True))


def seo_fields(post):
    return {
        'title': post['seo_title'], 'description': post['seo_description'],
        'label': post['title'], 'headline': ' '.join(post['title'].split()),
        'date_published': post['date'], 'article': True, 'blog_post': True,
        **({'image': post['image'], 'image_alt': post['image_alt']} if post.get('image') else {}),
    }


def markdown(body):
    from markdown_it import MarkdownIt

    renderer = MarkdownIt('commonmark', {'html': False})
    render_image = renderer.renderer.rules['image']

    def local_image(tokens, index, options, env):
        image = tokens[index]
        path, width, height, _ = asset_info(image.attrGet('src'))
        if not any(child.content.strip() for child in image.children or []):
            raise ValueError(f'Enter alt text for {path}')
        for key, value in {'src': path, 'width': width, 'height': height,
                           'loading': 'lazy', 'decoding': 'async'}.items():
            image.attrSet(key, value)
        return render_image(tokens, index, options, env)

    renderer.renderer.rules['image'] = local_image
    # The page template owns the H1. Keep authored headings in a valid outline.
    tokens = renderer.parse(body)
    previous = 1
    for token in tokens:
        if token.type == 'heading_open':
            previous = min(max(int(token.tag[1]), 2), previous + 1)
            token.tag = f'h{previous}'
        if token.type == 'heading_close':
            token.tag = f'h{previous}'
    return renderer.renderer.render(tokens, renderer.options, {})


def cover(post, eager=False):
    if not post.get('image'):
        return ''
    path, width, height, _ = asset_info(post['image'])
    alt = escape(post['image_alt'], quote=True)
    priority = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{path}" width="{width}" height="{height}" alt="{alt}" {priority} decoding="async">'


def published_time(post):
    published = post['date']
    label = date.fromisoformat(published).strftime('%d %B %Y').lstrip('0')
    return f'<time datetime="{published}">{label}</time>'


def listing(posts, breadcrumb):
    hero = (
        f'<section class="page-hero blog-hero"><div class="wrap">{breadcrumb}'
        f'<h1>{copy_text("blog", "heading")}</h1><p>{copy_text("blog", "intro")}</p></div></section>'
    )
    if not posts:
        return f'{hero}<div class="wrap blog-list"><p class="blog-empty">{copy_text("blog", "empty")}</p></div>'

    cards = []
    for route, post in posts.items():
        artwork = cover(post)
        title_id = f'blog-card-{route[len(BLOG_PATH):-1]}'
        cards.append(
            f'<article class="blog-card"><a class="blog-card-link" href="{route}" aria-labelledby="{title_id}">'
            f'<div class="blog-card-image">{artwork}</div>'
            f'<div class="blog-card-copy">{published_time(post)}'
            '<span class="blog-card-arrow" aria-hidden="true">↗</span>'
            f'<h2 id="{title_id}">{escape(post["title"])}</h2></div></a></article>'
        )
    return f'{hero}<section class="wrap blog-list blog-grid" aria-label="Blog posts">{"".join(cards)}</section>'


def render(route, post, breadcrumb, link):
    title = escape(post['title'])
    summary = escape(post['summary'])
    return (
        '<article>'
        f'<header class="page-hero blog-hero"><div class="wrap blog-reading">{breadcrumb(route)}'
        f'<h1>{title}</h1><p>{summary}</p><div class="article-meta"><a href="/about/">Talha Alam</a>'
        f'{published_time(post)}</div></div></header>'
        f'<div class="wrap blog-reading prose blog-body">{cover(post, eager=True)}{markdown(post["body"])}'
        f'<div class="blog-back">{link("Back to the blog", BLOG_PATH)}</div></div></article>'
    )
