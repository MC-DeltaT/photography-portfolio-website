from pathlib import Path
import logging
from typing import Any

import jinja2

from ..photo_info import PhotoInfo
from ..resource.html import get_html_resources_path
from ..url import get_css_asset_url, get_single_photo_page_url, get_photo_asset_url
from .common import BuildContext, BuildDirectory


logger = logging.getLogger(__name__)


def create_jinja2_environment(html_resources_path: Path) -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(html_resources_path),
        autoescape=jinja2.select_autoescape(),
        undefined=jinja2.StrictUndefined,
    )


def get_common_html_render_context() -> dict[str, Any]:
    return {
        'urls': {
            'main_stylesheet': get_css_asset_url('style.css')
        }
    }


def get_html_render_context(**extra: Any) -> dict[str, Any]:
    context = get_common_html_render_context()
    context.update(extra)
    return context


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


def build_single_photo_page(build_dir: BuildDirectory, photo: PhotoInfo, jinja2_env: jinja2.Environment, *,
        dry_run: bool) -> None:
    url = get_single_photo_page_url(photo.unique_id)
    logger.info(f'Building single photo page URL: {url}')
    template = jinja2_env.get_template('single_photo.html')
    render_context = get_html_render_context(
        photo_page_title=photo.title or photo.unique_id,
        image_url=get_photo_asset_url(photo.unique_id, photo.file_extension),
        photo_title=photo.title,
        photo_location=photo.location,
        photo_description=photo.description,
        photo_settings=make_photo_settings_list(photo),
        photo_genre=photo.genre
    )
    rendered_html = template.render(render_context)
    dest_path = build_dir.prepare_file(url.fs_path)
    logger.debug(f'Writing HTML: "{dest_path}"')
    if not dry_run:
        dest_path.write_text(rendered_html, encoding='utf8')


def build_single_photo_pages(context: BuildContext) -> None:
    html_resources_path = get_html_resources_path(context.resources_path)
    jinja2_env = create_jinja2_environment(html_resources_path)

    for photo in context.photos:
        build_single_photo_page(context.build_dir, photo, jinja2_env, dry_run=context.dry_run)
