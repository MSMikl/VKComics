import os

from pathlib import Path
from random import randint

import requests

def download_picture(url, path='./'):
    comics_picture = requests.get(url)
    comics_picture.raise_for_status()
    with open (Path(path, os.path.basename(url)), 'wb') as image:
        image.write(comics_picture.content)

path = './Pictures/'
Path(path).mkdir(parents=True, exist_ok=True)
comics_number = randint(0, 1000)
response = requests.get('https://xkcd.com/{}/info.0.json'.format(comics_number))
response.raise_for_status()
comics_data = response.json()
print (comics_data)
download_picture(comics_data['img'], path)

