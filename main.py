import os
import urllib.parse
from pathlib import Path
from random import randint

import requests
from dotenv import load_dotenv
from vk import api


def retrieve_img_url(comics_id: int):
    url = f'https://xkcd.com/{comics_id}/info.0.json'
    resp = requests.get(url)
    resp.raise_for_status()

    comics_info = resp.json()
    return comics_info['img'], comics_info['alt']


def retrieve_random_comics_num(url) -> int:
    resp = requests.get(url)
    resp.raise_for_status()

    comics_count = resp.json()['num']

    return randint(0, comics_count)


def download_image(url, dir_path: Path) -> Path:
    resp = requests.get(url)
    resp.raise_for_status()

    url_parse = urllib.parse.urlsplit(url)
    path = urllib.parse.unquote(url_parse.path)
    _, file_name = os.path.split(path)

    with open(dir_path.joinpath(file_name), 'wb') as f_in:
        f_in.write(resp.content)

    return dir_path.joinpath(file_name)


def main():
    vk_group_id = os.getenv('VK_GROUP_ID')
    vk_access_token = os.getenv('VK_ACCESS_TOKEN')
    vk_url = os.getenv('VK_URL')
    vk_api_v = os.getenv('VK_API_VERSION')

    img_dir = Path(__file__).resolve().parent.joinpath('images')
    if not img_dir.exists():
        os.mkdir(img_dir)
    url = 'https://xkcd.com/info.0.json'

    comics_id = retrieve_random_comics_num(url)
    img_url, comment = retrieve_img_url(comics_id)
    downloaded_img = download_image(img_url, img_dir)
    upload_url = api.retrieve_server_address(
        group_id=vk_group_id,
        access_token=vk_access_token,
        url=vk_url,
        api_version=vk_api_v)
    resp = api.upload_foto(upload_url, downloaded_img)
    medias_info = api.save_foto(
        url=vk_url,
        access_token=vk_access_token,
        group_id=vk_group_id,
        photo=resp.photo,
        server=resp.server,
        vk_hash=resp.hash,
        api_version=vk_api_v
    )

    for media in medias_info:
        attachments = f'photo{media.owner_id}_{media.media_id}'

    api.post_foto_to_group(
        url=vk_url,
        access_token=vk_access_token,
        attachments=attachments,
        api_version=vk_api_v,
        owner_id=f'-{vk_group_id}',
        message=comment)

    os.remove(downloaded_img)


if __name__ == '__main__':
    load_dotenv()
    main()
