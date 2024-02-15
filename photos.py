import requests
import json
from tqdm import tqdm
from urllib.parse import urlencode
from datetime import datetime

def oauth_url():
    APP_ID = '51847994'
    OAUTH_BASE_URL = 'https://oauth.vk.com/authorize'
    params = {
        'client_id': APP_ID,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'page',
        'scope': 'photos',
        'response_type': 'token'
        }
    oauth_url = f'{OAUTH_BASE_URL}?{urlencode(params)}'
    return oauth_url

class API_VK_YAD:

    API_BASE_URL = 'https://api.vk.com/method'
    URL_YADISK = 'https://cloud-api.yandex.net'

    def __init__(self, token_vk, token_yad, user_id):
        self.user_id = user_id
        self.token_vk = token_vk
        self.token_yad = token_yad

    def get_common_params(self):
        return {
            'access_token': self.token_vk,
            'v': '5.131'
        }

    def headers_dict(self):
        return {'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token_yad}'}

    def _build_url(self, api_method):
        return f'{self.API_BASE_URL}/{api_method}'

    def get_photos(self):
        params = self.get_common_params()
        params.update({'owner_id': self.user_id, 'album_id': 'profile', 'extended': '1', 'count': '5', 'rev': '1'})
        response = requests.get(self._build_url('photos.get'), params=params)
        photos = response.json()['response']['items']
        return photos

    def create_folder(self, name_folder):
        url_create_folder = f'{self.URL_YADISK}/v1/disk/resources'
        params_dict = {
            'path': name_folder
        }
        response = requests.put(url_create_folder,
                                params=params_dict,
                                headers=self.headers_dict())
        return response

    def name_photo(self, photo, photo_names):
        likes_count = photo['likes']['count']
        if likes_count not in photo_names:
            name = likes_count
        else:
            date = datetime.fromtimestamp(photo['date']).strftime('%Y-%m-%d_%H-%M-%S')
            name = date
        return name

    def photos_info(self, photo, name):
        photos_info = {}
        photos_info['file_name'] = name
        photos_info['size'] = photo['sizes'][-1]['type']
        with open(f'{name}.json', 'w') as file:
            json.dump(photos_info, file)

    def upload_photo(self, name_folder, name):
        url_upload = f'{self.URL_YADISK}/v1/disk/resources/upload'
        response = requests.get(url_upload, headers=self.headers_dict(), params={'path': f'{name_folder}/{name}.jpg'})
        upload_url = response.json().get('href', '')
        with open(f'{name}.jpg', 'rb') as f:
            response = requests.put(upload_url, files={"file": f})

    def save_photos(self):
        photos = client.get_photos()
        self.create_folder('Profile')
        photo_names = []
        for photo in tqdm(photos):
            url = photo['sizes'][-1]['url']
            response = requests.get(url)
            name = self.name_photo(photo, photo_names)
            photo_names.append(name)
            with open(f'{name}.jpg', 'wb') as file:
                file.write(response.content)
            self.photos_info(photo, name)
            self.upload_photo('Profile', name)

if __name__ == '__main__':
    print('Ссылка для получения токена VK:', oauth_url())
    TOKEN_VK = input('Введите токен ВК: ')
    TOKEN_YAN = input('Введите токен Яндекс Диска: ')
    response = requests.get(f'https://api.vk.com/method/users.get', params={'access_token': TOKEN_VK, 'v': '5.131'})
    user_id = response.json()['response'][0]['id']
    client = API_VK_YAD(TOKEN_VK, TOKEN_YAN, user_id)
    client.save_photos()


