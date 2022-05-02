import os

from pathlib import Path
from random import randint

import requests

from environs import Env


ENV = Env()
ENV.read_env()
ACCESS_TOKEN = ENV('ACCESS_TOKEN')


def download_picture(url, path='./'):
    comics_picture = requests.get(url)
    comics_picture.raise_for_status()
    with open(Path(path, os.path.basename(url)), 'wb') as image:
        image.write(comics_picture.content)


def get_xkcd_picture():
    path = './Pictures/'
    Path(path).mkdir(parents=True, exist_ok=True)
    comics_number = randint(0, 2613)
    response = requests.get(
        'https://xkcd.com/{}/info.0.json'.format(comics_number)
    )
    response.raise_for_status()
    comics_data = response.json()
    download_picture(comics_data['img'], path)
    return [
        os.path.join(path, os.path.basename(comics_data['img'])),
        comics_data['alt']
    ]


def post_picture(picture, text=''):
    group_id = ENV('GROUP_ID')
    user_id = ENV('USER_ID')
    params_for_get_server = {
        'group_id': group_id,
        'access_token': ACCESS_TOKEN,
        'v': '5.131'
    }
    response_1stage = requests.get(
        'https://api.vk.com/method/photos.getWallUploadServer',
        params=params_for_get_server
    ).json()
    if response_1stage.get('error', None):
        return 'Ошибка получения сервера загрузки'
    upload_url = response_1stage['response']['upload_url']
    with open(picture, 'rb') as file:
        files = {
            'file1': file
        }
        response_2stage = requests.post(
            upload_url,
            params=params_for_get_server,
            files=files
        ).json()
    if not response_2stage['photo']:
        return 'Ошибка загрузки на сервер'
    response_2stage.update(
        group_id=group_id,
        access_token=ACCESS_TOKEN,
        v='5.131'
    )
    response_3stage = requests.post(
        'https://api.vk.com/method/photos.saveWallPhoto',
        params=response_2stage
    ).json()
    if response_3stage.get('error', None):
        return 'Ошибка передачи фотографии в сообщество'
    attachments = 'photo{}_{}'.format(
        user_id,
        response_3stage['response'][0]['id']
    )
    params_for_post = {
        'owner_id': '-{}'.format(group_id),
        'from_group': '1',
        'friends_only': '1',
        'message': text,
        'attachments': attachments,
        'access_token': ACCESS_TOKEN,
        'v': '5.131'
    }
    response_4stage = requests.get(
        'https://api.vk.com/method/wall.post',
        params=params_for_post
    )
    os.remove(picture)
    return "Комикс успешно опубликован"


if __name__ == '__main__':
    picture, text = get_xkcd_picture()
    print(post_picture(picture, text))
