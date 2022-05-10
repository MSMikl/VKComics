import os

from pathlib import Path
from random import randint
from urllib.error import HTTPError
from urllib.parse import urlparse, unquote

import requests

from environs import Env


def download_picture(url, path='./'):
    comics_picture = requests.get(url)
    comics_picture.raise_for_status()
    parsed_url = urlparse(unquote(url))
    filename = Path(parsed_url.path).name
    with open(Path(path, filename), 'wb') as image:
        image.write(comics_picture.content)
    return filename


def get_random_comics_number():
    start_response = requests.get('https://xkcd.com/info.0.json')
    start_response.raise_for_status()
    return randint(0, start_response.json()['num'])


def get_xkcd_picture(number):
    path = './Pictures/'
    Path(path).mkdir(parents=True, exist_ok=True)
    response = requests.get(
        'https://xkcd.com/{}/info.0.json'.format(number)
    )
    response.raise_for_status()
    comics_data = response.json()
    filename = download_picture(comics_data['img'], path)
    return [
        os.path.join(path, filename),
        comics_data['alt']
    ]


def get_upload_server(group_id, access_token, version):
    params = {
        'group_id': group_id,
        'access_token': access_token,
        'v': version
    }
    response = requests.get(
        'https://api.vk.com/method/photos.getWallUploadServer',
        params=params
    )
    response.raise_for_status()
    response = response.json()
    if response.get('error', None):
        raise HTTPError('Ошибка получения сервера загрузки')
    return response['response']['upload_url']


def upload_picture(upload_url, picture, group_id, access_token, version):
    params = {
        'group_id': group_id,
        'access_token': access_token,
        'v': version
    }
    with open(picture, 'rb') as file:
        files = {
            'file1': file
        }
        response = requests.post(
            upload_url,
            params=params,
            files=files
        )
    response.raise_for_status()
    response = response.json()
    if not response['photo']:
        raise HTTPError('Ошибка загрузки на сервер')
    return response


def send_picture_to_public(params, group_id, access_token, version):
    params.update(
        group_id=group_id,
        access_token=access_token,
        v=version
    )
    response = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=params
    )
    response.raise_for_status()
    response = response.json()
    if response.get('error', None):
        raise HTTPError('Ошибка передачи фотографии в сообщество')
    return response['response'][0]['id']


def post_to_public(picture_id, text, user_id, group_id, access_token, version):
    attachments = 'photo{}_{}'.format(
        user_id,
        picture_id
    )
    params = {
        'owner_id': '-{}'.format(group_id),
        'from_group': '1',
        'friends_only': '1',
        'message': text,
        'attachments': attachments,
        'access_token': access_token,
        'v': version
    }
    response = requests.get(
        'https://api.vk.com/method/wall.post',
        params=params
    )
    response.raise_for_status()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    access_token = env('access_token')
    group_id = env('GROUP_ID')
    user_id = env('USER_ID')
    version = env('VERSION')
    picture, text = get_xkcd_picture(
        get_random_comics_number()
    )
    try:
        upload_url = get_upload_server(
            access_token=access_token,
            group_id=group_id,
            version=version
        )
        upload_response = upload_picture(
            upload_url=upload_url,
            picture=picture,
            access_token=access_token,
            group_id=group_id,
            version=version
        )
        uploaded_picture = send_picture_to_public(
            params=upload_response,
            access_token=access_token,
            group_id=group_id,
            version=version
        )
        post_to_public(
            picture_id=uploaded_picture,
            text=text,
            access_token=access_token,
            user_id=user_id,
            group_id=group_id,
            version=version
        )
    finally:
        os.remove(picture)
