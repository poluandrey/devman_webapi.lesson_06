import os
import urllib.parse
from pathlib import Path
from random import randint

import requests
from dotenv import load_dotenv

from vk import api


def retrieve_comic(comic_id: int):
    url = f'https://xkcd.com/{comic_id}/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()

    comic = resp.json()
    return comic['img'], comic['alt']


def retrieve_random_comic_num() -> int:
    url = 'https://xkcd.com/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()

    comics_count = resp.json()['num']

    return randint(0, comics_count)


def download_comic(url, dir_path: Path) -> Path:
    resp = requests.get(url)
    resp.raise_for_status()

    url_part = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(url_part.path)
    _, file_name = os.path.split(path)

    with open(dir_path.joinpath(file_name), 'wb') as f_in:
        f_in.write(resp.content)

    return dir_path.joinpath(file_name)


def main():
    vk_group_id = os.getenv('VK_GROUP_ID')
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_api_v = os.getenv('VK_API_VERSION')

    img_dir = Path(__file__).resolve().parent.joinpath('images')
    os.makedirs(img_dir, exist_ok=True)

    comics_id = retrieve_random_comic_num()
    img_url, comment = retrieve_comic(comics_id)
    downloaded_img = download_comic(img_url, img_dir)
    try:
        upload_url = api.retrieve_server_address(
            group_id=vk_group_id,
            access_token=vk_access_token,
            api_version=vk_api_v)
        uploaded_foto = api.upload_foto(upload_url, downloaded_img)
        media_detail = api.retrieve_media_detail(
            access_token=vk_access_token,
            group_id=vk_group_id,
            photo=uploaded_foto.photo,
            server=uploaded_foto.server,
            vk_hash=uploaded_foto.hash,
            api_version=vk_api_v
        )

        attachments = f'photo{media_detail.owner_id}_{media_detail.media_id}'

        api.post_foto_to_group(
            access_token=vk_access_token,
            attachments=attachments,
            api_version=vk_api_v,
            owner_id=f'-{vk_group_id}',
            message=comment)
    finally:
        os.remove(downloaded_img)


if __name__ == '__main__':
    load_dotenv()
    main()
