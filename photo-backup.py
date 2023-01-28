import requests
import json
import logging
from pprinty import pprint
import datetime

logging.basicConfig(level=logging.DEBUG, filename='mylog.log')

token_YandexDisk = input('Введите токен с Полигона Яндекс.Диска: ')
token_VK = '*****'


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.token = token
        self.version = version
        self.owner_id = []
        self.profile_photos = []

    # Получение информации о профиле
    def get_profile_info(self):
        url = self.url + 'account.getProfileInfo'
        profile_info_params = {'access_token': self.token, 'v': self.version}
        req = requests.get(url, params={**self.params, **profile_info_params}).json()
        self.owner_id = req['response']['id']
        first_name = req['response']['first_name']
        last_name = req['response']['last_name']
        pprint(f'Информация по пользователю {first_name} {last_name} получена')
        return req['response']

    # Получение информации о фотографиях профиля пользователя
    def get_profile_photos(self):
        url = self.url + 'photos.get'
        profile_photos_params = {
            'access_token': self.token,
            'owner_id': self.owner_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 0,
            'count': '5',
            'v': self.version
        }
        req = requests.get(url, params={**self.params, **profile_photos_params}).json()
        self.profile_photos = req['response']['items']
        return self.profile_photos

    # Получение ссылок на максимальный размер фотографий
    def get_url_max_size_photos(self):
        max_size_photos = list()
        max_size_photos_url = list()
        for photo in self.profile_photos:
            max_size_photos.append(photo['sizes'][-1])
        for item in max_size_photos:
            max_size_photos_url.append(item['url'])
        return max_size_photos_url

    # Получение списка имен фотографий
    def get_photo_names(self):
        photo_names = list()
        for photo in self.profile_photos:
            old_date = datetime.datetime.fromtimestamp(photo['date'])
            str_date = old_date.strftime('%Y-%m-%d')
            photo_names.append(str(photo['likes']['count']) + '_' + str(str_date) + '.jpg')
        return photo_names

    # Получение списка максимальных размеров фотографий
    def get_photo_max_size(self):
        max_size_photos_info = list()
        max_size_photos = list()
        for photo in self.profile_photos:
            max_size_photos_info.append(photo['sizes'][-1])
        for item in max_size_photos_info:
            max_size_photos.append(item['type'])
        return max_size_photos

    # Создание словаря сохраняемых фотографий и запись в .json файл
    def create_photo_dict(self):
        photo_name = self.get_photo_names()
        photo_size = self.get_photo_max_size()
        photo_info = list(zip(photo_name, photo_size))
        saved_photo_info = []
        for name, size in photo_info:
            max_size_photo = {'file name': name, 'size': size}
            saved_photo_info.append(max_size_photo)
        with open('result.json', 'w') as f:
            json.dump(saved_photo_info, f, indent=2)
        return saved_photo_info


class YaDisk:
    url = "https://cloud-api.yandex.net/v1/disk/"

    def __init__(self, token):
        self.token = token

    # Сохранение фото на ЯндексДиск
    def save_photo(self):
        folder_name = input('Введите название папки, в которую будут сохраняться фотографии: ')
        url_put = self.url + 'resources'
        url_post = self.url + 'resources/upload'
        headers = {"Authorization": f"OAuth {self.token}"}
        requests.put(url_put, params={'path': {folder_name}}, headers=headers)
        photo_name = user.get_photo_names()
        photo_url = user.get_url_max_size_photos()
        photo_info = list(zip(photo_name, photo_url))
        for name, url_photo in photo_info:
            requests.post(url_post, params={"path": {folder_name+'/'+name}, 'url': url_photo}, headers=headers)
            pprint(f'Фотография {name} сохранена')
        pprint(f'Ваши фотографии доступны по ссылке: https://disk.yandex.ru/client/disk/{folder_name}')
        return


disk = YaDisk(token_YandexDisk)
user = VkUser(token_VK, '5.131')

user.get_profile_info()
user.get_profile_photos()
user.create_photo_dict()
disk.save_photo()
