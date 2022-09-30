from pathlib import Path
from typing import List
from urllib.parse import urljoin

import requests
from vk.vk_types import SaveWallPhotoResp, UploadFotoResp


def retrieve_server_address(
        group_id: str,
        access_token: str,
        url: str,
        api_version: str) -> str:
    url = urljoin(url, 'photos.getWallUploadServer')
    params = {
        'v': api_version,
        'group_id': group_id,
        'access_token': access_token
    }
    resp = requests.get(url, params=params)

    resp.raise_for_status()

    return resp.json().get('response').get('upload_url')


def upload_foto(url: str, file: Path) -> UploadFotoResp:
    with open(file, 'rb') as upload_file:
        files = {
            'file1': upload_file
        }
        resp = requests.post(url, files=files)
        resp.raise_for_status()
        server = resp.json().get('server')
        photo = resp.json().get('photo')
        foto_hash = resp.json().get('hash')

    return UploadFotoResp(server, photo, foto_hash)


def save_foto(
        url: str,
        access_token: str,
        group_id: str,
        photo: str,
        server: str,
        vk_hash: str,
        api_version: str) -> List[SaveWallPhotoResp]:
    media_info = []
    method = 'photos.saveWallPhoto'
    vk_url = urljoin(url, method)
    params = {
        'group_id': group_id,
        'v': api_version,
        'access_token': access_token,
        'photo': photo,
        'server': server,
        'hash': vk_hash,
    }

    resp = requests.post(vk_url, params=params)
    try:
        vk_resp = resp.json().get('response')
    except KeyError:
        return resp.json().get('error')
    for resp_detail in vk_resp:
        owner_id = resp_detail.get('owner_id')
        media_id = resp_detail.get('id')
        media_info.append(SaveWallPhotoResp(media_id, owner_id))
    return media_info


def post_foto_to_group(
        url,
        access_token,
        api_version,
        owner_id: str,
        message: str,
        attachments: str = None,
        from_group: int = 1):
    method = 'wall.post'
    vk_url = urljoin(url, method)
    params = {
        'access_token': access_token,
        'v': api_version,
        'owner_id': owner_id,
        'message': message,
        'attachments': attachments,
        'from_group': from_group,
    }
    resp = requests.post(vk_url, params=params)
    resp.raise_for_status()
