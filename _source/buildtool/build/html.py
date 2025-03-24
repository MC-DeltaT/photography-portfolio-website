from collections.abc import Mapping
from dataclasses import dataclass, fields
import datetime as dt
from pathlib import Path
import logging
from typing import Any

import jinja2

from ..photo_info import PhotoInfo
from ..resource.html import get_html_resources_path
from ..url import ABOUT_PAGE_URL, GALLERY_BY_DATE_PAGE_URL, GALLERY_BY_STYLE_PAGE_URL, INDEX_PAGE_URL, URLPath, get_css_asset_url, get_single_photo_page_url, get_photo_asset_url
from .common import BuildContext


logger = logging.getLogger(__name__)


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
    )


def get_copyright_date_tag() -> str:
    begin = 2025
    end = dt.date.today().year
    if begin == end:
        return str(begin)
    else:
        return f'{begin}-{end}'


def get_common_html_render_context() -> dict[str, Any]:
    return {
        'urls': {
            'main_stylesheet': get_css_asset_url('style.css'),
            'about': ABOUT_PAGE_URL,
            'gallery_by_style': GALLERY_BY_STYLE_PAGE_URL,
            'gallery_by_date': GALLERY_BY_DATE_PAGE_URL
        },
        'copyright_date': get_copyright_date_tag()
    }


def create_html_render_context(extra: Mapping[str, Any]) -> dict[str, Any]:
    context = get_common_html_render_context()
    context.update(extra)
    return context


def build_html_page(template_name: str, url: URLPath, context: HTMLBuildContext,
        render_context: Mapping[str, Any] = {}) -> None:
    logger.info(f'Building HTML page URL: {url}')
    template = context.jinja2_env.get_template(template_name)
    render_context = create_html_render_context(render_context)
    rendered_html = template.render(render_context)
    dest_path = context.build_dir.prepare_file(url.fs_path)
    logger.debug(f'Writing HTML: "{dest_path}"')
    if not context.dry_run:
        dest_path.write_text(rendered_html, encoding='utf8')


def build_html(context: BuildContext) -> None:
    html_resources_path = get_html_resources_path(context.resources_path)
    jinja2_env = create_jinja2_environment(html_resources_path)
    context = HTMLBuildContext.new(context, jinja2_env)

    build_simple_pages(context)
    build_single_photo_pages(context)


# Pages that don't require any special handling and can be rendered systematically.
SIMPLE_PAGES = [
    ('index.html', INDEX_PAGE_URL),
    ('about.html', ABOUT_PAGE_URL)
]


def build_simple_pages(context: HTMLBuildContext) -> None:
    for template_name, url in SIMPLE_PAGES:
        build_html_page(template_name, url, context)


F_NUMBER_SYMBOL = 'ƒ'


def replace_f_number_with_symbol(s: str) -> str:
    return s.replace('f/', f'{F_NUMBER_SYMBOL}/')


def make_photo_settings_list(photo: PhotoInfo) -> list[str]:
    result: list[str] = []
    if photo.camera_model:
        result.append(photo.camera_model)
    if photo.lens_model:
        result.append(replace_f_number_with_symbol(photo.lens_model))
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
        result.append(f'{exposure_time_str} s')
    if photo.iso:
        result.append(f'ISO {photo.iso}')
    return result


def build_single_photo_page(photo: PhotoInfo, context: HTMLBuildContext) -> None:
    url = get_single_photo_page_url(photo.unique_id)
    render_context = create_html_render_context({
        'photo_page_title': photo.title or photo.unique_id,
        'photo': {
            'image_url': get_photo_asset_url(photo.unique_id, photo.file_extension),
            'title': photo.title,
            'location': photo.location,
            'description': photo.description,
            'settings': make_photo_settings_list(photo),
            'genre': photo.genre
        }
    })
    build_html_page('single_photo.html', url, context, render_context)


def build_single_photo_pages(context: HTMLBuildContext) -> None:
    for photo in context.photos:
        build_single_photo_page(photo, context)
