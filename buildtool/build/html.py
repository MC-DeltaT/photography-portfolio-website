from collections.abc import Mapping
from dataclasses import dataclass, fields
import datetime as dt
import logging
from pathlib import Path
import re
from typing import Any

import jinja2
import minify_html

from buildtool.build.common import BuildContext, BuildState
from buildtool.photo_collection import PhotoCollection
from buildtool.photo_info import PhotoInfo
from buildtool.resource.html import get_html_resources_path
from buildtool.types import ImageSrcSet, URLPath
from buildtool.url import ABOUT_PAGE_URL, ASSETS_CSS_URL, ASSETS_JS_URL, GALLERY_PAGE_URL, INDEX_PAGE_URL, get_photo_page_url


logger = logging.getLogger(__name__)


def build_all_html(context: BuildContext) -> None:
    logger.info('Building HTML')
    html_resources_path = get_html_resources_path(context.resources_path)
    jinja2_env = create_jinja2_environment(html_resources_path)
    context = HTMLBuildContext.new(context, jinja2_env)
    build_basic_pages(context)
    build_photo_pages(context)


@dataclass(frozen=True)
class HTMLBuildContext(BuildContext):
    jinja2_env: jinja2.Environment

    @classmethod
    def new(cls, build_context: BuildContext, jinja2_env: jinja2.Environment):
        return cls(
            **{f.name: getattr(build_context, f.name) for f in fields(build_context)},
            jinja2_env=jinja2_env)


def create_jinja2_environment(html_resources_path: Path) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(html_resources_path),
        autoescape=jinja2.select_autoescape(),
        undefined=jinja2.StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True
    )


def build_html_page(template_name: str, url: URLPath, context: HTMLBuildContext,
        render_context: Mapping[str, Any] = {}) -> None:
    logger.info(f'Building HTML page URL: {url}')
    template = context.jinja2_env.get_template(template_name)
    render_context = create_html_render_context(context, render_context)
    logger.debug(f'Render context: {render_context}')
    rendered_html = template.render(render_context)
    minified_html = minify_html.minify(
        rendered_html,
        minify_js=True, minify_css=True,
        keep_closing_tags=True, keep_html_and_head_opening_tags=True, keep_input_type_text_attr=True)
    context.build_dir.build_content(minified_html, url)


RenderContext = dict[str, Any]


def get_common_html_render_context(context: HTMLBuildContext) -> RenderContext:
    return {
        'css': {
            'main': ASSETS_CSS_URL / 'main.css',
            'index': ASSETS_CSS_URL / 'index.css',
            'about': ASSETS_CSS_URL / 'about.css',
            'gallery': ASSETS_CSS_URL / 'gallery.css',
            'photo': ASSETS_CSS_URL / 'photo.css'
        },
        'js': {
            'gallery': ASSETS_JS_URL / 'gallery.js'
        },
        'pages': {
            'about': ABOUT_PAGE_URL,
            'gallery': GALLERY_PAGE_URL
        },
        'copyright_date': get_copyright_date_tag(),
        'gallery_age': get_gallery_age(context.photos),
        'images': {
            image_id: create_image_render_context(srcset)
            for image_id, srcset in context.state.image_srcsets.items()
        }
    }


def create_html_render_context(context: HTMLBuildContext, extra: Mapping[str, Any]) -> RenderContext:
    render_context = get_common_html_render_context(context)
    render_context.update(extra)
    return render_context


def get_copyright_date_tag() -> str:
    begin = 2025
    end = dt.date.today().year
    if begin == end:
        return str(begin)
    else:
        return f'{begin}-{end}'


def get_gallery_age(photos: PhotoCollection) -> int:
    oldest_photo = min((p for p in photos if p.date), key=lambda p: p.date)
    assert oldest_photo.date.year
    age = round(dt.date.today().year - oldest_photo.date.year)
    assert age >= 0
    age = max(1, age)
    return age

@dataclass(frozen=True)
class BasicPage:
    template: str
    url: URLPath

    def render_context(self, context: BuildContext) -> RenderContext:
        return {}


@dataclass(frozen=True)
class GalleryPage(BasicPage):
    def __init__(self) -> None:
        super().__init__(
            template='pages/gallery.html',
            url=GALLERY_PAGE_URL
        )

    def render_context(self, context: BuildContext) -> dict[str, Any]:
        # Get all photos sorted by date (newest first). Also order by ID to break ties consistently.
        all_photos = sorted(context.photos, key=lambda p: p.chronological_sort_key, reverse=True)
        
        # Get unique years and months for filters
        years = sorted({d.year for d in context.photos.dates if d.year}, reverse=True)
        months = sorted(
            {f'{d.year}-{d.month:02d}' for d in context.photos.dates if d.year and d.month},
            reverse=True
        )
        
        return {
            'photos': [create_photo_render_context(p, context.state) for p in all_photos],
            'genres': [genre.value for genre in context.photos.genres],
            'years': years,
            'months': months
        }


BASIC_PAGES = [
    BasicPage('pages/index.html', INDEX_PAGE_URL),
    BasicPage('pages/about.html', ABOUT_PAGE_URL),
    GalleryPage()
]


def build_basic_pages(context: HTMLBuildContext) -> None:
    for page in BASIC_PAGES:
        render_context = page.render_context(context)
        build_html_page(page.template, page.url, context, render_context)


def build_photo_pages(context: HTMLBuildContext) -> None:
    for photo in context.photos:
        build_photo_page(photo, context)


def build_photo_page(photo: PhotoInfo, context: HTMLBuildContext) -> None:
    url = get_photo_page_url(photo.id)
    render_context = create_html_render_context(context, {
        'photo_page_title': photo.title or photo.id.split('.')[0],
        'photo': create_photo_render_context(photo, context.state)
    })
    build_html_page('pages/photo.html', url, context, render_context)


def create_image_render_context(srcset: ImageSrcSet) -> RenderContext:
    render_context: RenderContext = {
        'default_url': srcset.default.url,
        'srcset_urls': ', '.join(f'{s.url} {s.descriptor}' for s in srcset),
    }
    return render_context


def create_photo_render_context(photo: PhotoInfo, build_state: BuildState) -> RenderContext:
    # Page design doesn't really support photos without year or month (e.g. how do you sort them?).
    # Should think twice about allowing photos with no date.
    assert photo.date.year is not None
    assert photo.date.month is not None
    # Page design assumes genres are always present.
    assert photo.genre
    return {
        'image': create_image_render_context(
            build_state.image_srcsets[build_state.photo_id_to_image_id[photo.id]]),
        'title': photo.title,
        'date': photo.date,
        'location': photo.location,
        'description': photo.description,
        'settings': create_photo_settings_list(photo),
        'genre': [genre.value for genre in sorted(photo.genre)],
        'page_url': get_photo_page_url(photo.id),
        'chronological_sort_key': '-'.join(photo.chronological_sort_key)
    }


def fix_up_canon_lens_model(lens_model: str) -> str:
    # Some Canon lens names from the camera don't have a space between the "EF" and the rest of the name, e.g.:
    # EF50mm f/1.8 STM
    # EF-S18-135mm f/3.5-5.6 IS USM
    if m := re.search(r'(?:^|\s)EF(?:-[A-Z])?(\d)', lens_model):
        idx = m.start(1)
        lens_model = lens_model[:idx] + ' ' + lens_model[idx:]

    # Some Canon lens names from the camera don't have a space between the f-rating and the "L" series marker, e.g.:
    # EF100-400mm f/4.5-5.6L IS USM
    number_regex = r'\d+(?:\.\d+)?'
    if m := re.search(rf'(?:^|\s)f/{number_regex}(?:-{number_regex})?(L)(?:\s|$)', lens_model):
        idx = m.start(1)
        lens_model = lens_model[:idx] + ' ' + lens_model[idx:]

    return lens_model


F_NUMBER_SYMBOL = 'ƒ'


def replace_f_number_with_symbol(s: str) -> str:
    return s.replace('f/', f'{F_NUMBER_SYMBOL}/')


def create_photo_settings_list(photo: PhotoInfo) -> list[str]:
    result: list[str] = []
    if photo.camera_model:
        result.append(photo.camera_model)
    if photo.lens_model:
        lens_model = fix_up_canon_lens_model(photo.lens_model)
        lens_model = replace_f_number_with_symbol(lens_model)
        result.append(lens_model)
    if photo.focal_length:
        if photo.focal_length < 10:
            focal_length_str = str(round(photo.focal_length, 1))
        else:
            focal_length_str = str(int(photo.focal_length))
        result.append(f'{focal_length_str}mm')
    if photo.aperture:
        result.append(f'{F_NUMBER_SYMBOL}/{photo.aperture}')
    if photo.exposure_time:
        if photo.exposure_time >= 0.1:
            exposure_time_str = str(round(photo.exposure_time, 1))
        else:
            exposure_time_str = f"1/{int(round(1 / photo.exposure_time))}"
        result.append(f'{exposure_time_str}s')
    if photo.iso:
        result.append(f'ISO {photo.iso}')
    return result
