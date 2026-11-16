"""Validate Git-backed blog entries and render published Markdown to static pages."""
from datetime import date
from html import escape
import re

from cms_content import ROOT, asset_info, read_json

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


def cards(posts):
    return ''.join(
        f'<article class="project-feature" data-project>'
        + (f'<a class="project-art" href="{route}">{cover(post)}</a>' if post.get('image') else '')
        + f'<div class="project-info"><span class="label">Blog post</span>'
          f'<h2><a href="{route}">{escape(post["title"])}</a></h2>'
          f'<p>{escape(post["summary"])}</p></div></article>'
        for route, post in posts.items()
    )


def render(route, post, breadcrumb, link):
    label = date.fromisoformat(post['date']).strftime('%d %B %Y').lstrip('0')
    title = escape(post['title'])
    summary = escape(post['summary'])
    return (
        f'<section class="page-hero"><div class="wrap article-hero">{breadcrumb(route)}'
        f'<h1>{title}</h1><p>{summary}</p><div class="article-meta"><span>By Talha Alam</span>'
        f'<time datetime="{post["date"]}">Published {label}</time></div></div></section>'
        f'<section class="section wrap"><article class="prose article-body">{cover(post, eager=True)}'
        f'{markdown(post["body"])}<div class="button-row">{link("Back to projects and blog", BLOG_PATH)}'
        '</div></article></section>'
    )
