# -*- coding: UTF-8 -*-

from modules import script_callbacks, extra_networks, prompt_parser, shared, ui_extra_networks
import json
import os
import copy
from urllib.parse import urlparse, parse_qs

filters = [
    # 'filename',
    # 'description',
    'search_term',
    'local_preview',
    'metadata',
]


def parse_thumb_url(url):
    if not url or 'thumb?filename=' not in url:
        return None
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'filename' in params:
            return params['filename'][0]
    except Exception as e:
        pass
    return None


def generate_thumbnail_for_file(file_path, width=200, height=200):
    from scripts.physton_prompt.get_thumbnail import (
        generate_thumbnail, get_cache_path, is_cache_valid,
        get_preview_path, parse_thumb_url
    )
    if not file_path:
        return None
    cache_path = get_cache_path(file_path, width, height)
    if is_cache_valid(cache_path):
        return cache_path
    try:
        preview_path = get_preview_path(file_path)
        if preview_path and os.path.exists(preview_path):
            generated = generate_thumbnail(preview_path, width, height)
            if generated:
                return generated
        generated = generate_thumbnail(file_path, width, height)
        return generated
    except Exception as e:
        return None


def get_thumbnail_url(cache_path, width=200, height=200):
    if not cache_path:
        return None
    import os
    if os.path.exists(cache_path):
        cache_filename = os.path.basename(cache_path)
        return f"/physton_prompt/thumbnail?filename={cache_filename}"
    return None


def get_extra_networks(thumbnail_width=None, thumbnail_height=None):
    import sys
    result = []
    try:
        for extra_page in ui_extra_networks.extra_pages:
            result_item = {
                'name': extra_page.name,
                'title': extra_page.title,
                'items': []
            }
            for oriItem in extra_page.list_items():
                item = copy.deepcopy(oriItem)
                # 解析 metadata
                output_name = None
                try:
                    if 'metadata' in item and item['metadata']:
                        metadata = json.loads(item['metadata'])
                        if metadata and 'ss_output_name' in metadata:
                            output_name = metadata['ss_output_name']
                except Exception as e:
                    pass
                item['output_name'] = output_name

                # 获取 civitai.info
                item['civitai_info'] = {}
                try:
                    if 'filename' in item and item['filename']:
                        item['basename'] = os.path.basename(item['filename'])
                        item['dirname'] = os.path.dirname(item['filename'])
                        base, ext = os.path.splitext(item['filename'])
                        info_file = base + '.civitai.info'
                        if not os.path.isfile(info_file):
                            info_file = item['filename'] + '.civitai.info'
                        if os.path.isfile(info_file):
                            with open(info_file, 'r') as f:
                                info = json.load(f)
                                images = info.get('images', [])
                                info = {
                                    'modelId': info.get('modelId', ''),
                                    'name': info.get('name', ''),
                                    'description': info.get('description', ''),
                                    'baseModel': info.get('baseModel', ''),
                                    'model': info.get('model', {}),
                                    'trainedWords': info.get('trainedWords', []),
                                    'images': [],
                                }
                                if images and len(images) > 0:
                                    for image in images:
                                        info['images'].append(image['url'])
                                item['civitai_info'] = info
                except Exception as e:
                    pass

                # Generate thumbnail if requested
                if thumbnail_width and thumbnail_height:
                    try:
                        filename = item.get('filename', '')
                        if filename:
                            thumb_path = generate_thumbnail_for_file(filename, int(thumbnail_width), int(thumbnail_height))
                            if thumb_path:
                                item['thumbnail'] = get_thumbnail_url(thumb_path, int(thumbnail_width), int(thumbnail_height))
                    except Exception as e:
                        pass

                # 过滤掉不需要的字段
                newItem = {}
                for key in item:
                    if key not in filters:
                        newItem[key] = item[key]

                result_item['items'].append(newItem)

            result.append(result_item)
    except Exception as e:
        print(f'[sd-webui-prompt-all-in-one] get_extra_networks error: {e}')
        pass
    return result
