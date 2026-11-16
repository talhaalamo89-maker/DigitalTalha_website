"""Load editable copy and resolve local images during the static build."""
from functools import cache
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read_json(relative):
    return json.loads((ROOT / 'content' / relative).read_text(encoding='utf-8'))


@cache
def page_copy(name):
    return read_json(f'pages/{name}.json')


def copy_value(page, field):
    return page_copy(page)[field]


def copy_text(page, field):
    return escape(copy_value(page, field), quote=False)


def attribute(page, field):
    return escape(copy_value(page, field), quote=True)


def asset_path(value):
    """Accept existing asset filenames and the URLs returned by the media picker."""
    value = value.removeprefix('/assets/')
    if not re.fullmatch(r'(?:[a-zA-Z0-9_-]+/)*[a-zA-Z0-9_.-]+\.(?:webp|jpg|jpeg|png)', value, re.I):
        raise ValueError(f'Expected a local image in assets: {value!r}')
    if not (ROOT / 'assets' / value).is_file():
        raise ValueError(f'Image does not exist: {value!r}')
    return '/assets/' + value


@cache
def asset_info(value):
    from PIL import Image

    path = asset_path(value)
    with Image.open(ROOT / path.lstrip('/')) as image:
        width, height = image.size
        return path, width, height, Image.MIME[image.format]


def load_services():
    return {key: read_json(f'services/{key}.json') for key in read_json('services.json')}


def load_seo():
    return {route: read_json(f'seo/{key}.json') for route, key in read_json('seo.json').items()}
