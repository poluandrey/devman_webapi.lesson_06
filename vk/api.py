from pathlib import Path
from urllib.parse import urljoin

import requests

from vk.vk_types import SaveWallPhotoResp, UploadFotoResp


def retrieve_server_address(
        group_id: str,
        access_token: str,
        api_version: str) -> str:
    vk_url = 'https://api.vk.com/method/'
    url = urljoin(vk_url, 'photos.getWallUploadServer')
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
    upload_result = resp.json()
    server = upload_result.get('server')
    photo = upload_result.get('photo')
    foto_hash = upload_result.get('hash')

    return UploadFotoResp(server, photo, foto_hash)


def retrieve_media_detail(
        access_token: str,
        group_id: str,
        photo: str,
        server: str,
        vk_hash: str,
        api_version: str) -> SaveWallPhotoResp:
    vk_url = 'https://api.vk.com/method/'
    method = 'photos.saveWallPhoto'
    url = urljoin(vk_url, method)
    params = {
        'group_id': group_id,
        'v': api_version,
        'access_token': access_token,
        'photo': photo,
        'server': server,
        'hash': vk_hash,
    }

    resp = requests.post(url, params=params)
    try:
        vk_resp = resp.json().get('response')[0]
    except KeyError:
        return resp.json().get('error')
    owner_id = vk_resp.get('owner_id')
    media_id = vk_resp.get('id')
    return SaveWallPhotoResp(media_id, owner_id)


def post_foto_to_group(
        access_token,
        api_version,
        owner_id: str,
        message: str,
        attachments: str = None,
        from_group: int = 1):
    vk_url = 'https://api.vk.com/method/'
    method = 'wall.post'
    url = urljoin(vk_url, method)
    params = {
        'access_token': access_token,
        'v': api_version,
        'owner_id': owner_id,
        'message': message,
        'attachments': attachments,
        'from_group': from_group,
    }
    resp = requests.post(url, params=params)
    resp.raise_for_status()
