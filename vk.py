from token_vk import token
import bot
import requests
import sql_uploader

class VK:
    
    def __init__(self):
        self.vk_token = token

# Информация для поиска
    def get_info_for_search(self, user_id):
        user_info = self.get_info_about_user(user_id)
        bot.Bot().write_msg(user_id, f"Введите возраст:")
        user_info['age'] = bot.Bot().get_age()
        
        if user_info['city'] == None:
            bot.Bot().write_msg(user_id, f"Введите город:")
            user_info['city'] = bot.Bot().get_city()
        if user_info['sex'] == None:
            bot.Bot().write_msg(user_id, f"""
                                        Укажите цифру соответствующую полу:
                                        1 - женский
                                        2 - мужской""")
            user_info['sex'] = bot.Bot().get_sex()
        if user_info['relation'] == None:
            bot.Bot().write_msg(user_id, f"""
                                        Укажите цифру соответствующую статусу:
                                        1 — не женат (не замужем);
                                        2 — встречается;
                                        3 — помолвлен(-а);
                                        4 — женат (замужем);
                                        5 — всё сложно;
                                        7 — влюблен(-а);
                                        8 — в гражданском браке.""")
            user_info['relation'] = bot.Bot().get_relation()
        return user_info


    # Информация по пользователю
    def get_info_about_user(self, id):
        response = requests.get("https://api.vk.com/method/users.get",
                                params={"access_token": self.vk_token, "v": "5.131", "user_ids": id,
                                        'fields': 'bdate, sex, relation, city'})
        if 'error' not in response.json():
            user_info = {}
            user_info['id'] = response.json()['response'][0]['id']
            user_info['name'] = response.json()['response'][0]['first_name']
            if 'city' in response.json()['response'][0]:
                user_info['city'] = response.json()['response'][0]['city']['id']
            else:
                user_info['city'] = None
            if 'sex' in response.json()['response'][0]:
                user_info['sex'] = response.json()['response'][0]['sex']
            else:
                user_info['sex'] = None
            if 'relation' in response.json()['response'][0]:
                user_info['relation'] = response.json()['response'][0]['relation']
            else:
                user_info['relation'] = None
            return user_info
        else:
            return False
    

    # Проверка города
    def check_city(self, city):
        response = requests.get("https://api.vk.com/method/database.getCities",
                                params={"access_token": self.vk_token, "v": "5.131", 'country_id': 1, 'q': city})
        for item in response.json()['response']['items']:
            if city.lower() == item['title'].lower():
                return item['id']
        return False


    # Результат поиска
    def show_users(self, user_id, user_info):
        users = self.search_users(user_info)
        sql_uploader.SqlUploader().create_table(user_id)
        for find_user_id, first_name, last_name in users:
            if not sql_uploader.SqlUploader().check_id_in_base(user_id, find_user_id):
                photos_list = []
                response = requests.get("https://api.vk.com/method/photos.get", params={"access_token": self.vk_token,
                                                                                        "owner_id": find_user_id,
                                                                                        "v": "5.131",
                                                                                        "album_id": "profile",
                                                                                        "extended": "1"})
                photos = response.json()['response']['items']
                for photo in photos:
                    photo_id = photo['id']
                    likes = photo['likes']['count']
                    comments = photo['comments']['count']
                    url = photo['sizes'][-1]['url']
                    new_tuple = (likes, comments, photo_id, url)
                    photos_list.append(new_tuple)
                max_3_photos = sorted(photos_list, key=lambda x: (x[0], x[1]), reverse=True)[:3]
                for item in max_3_photos:
                    bot.Bot().vk.method('messages.send',{'user_id': user_id, "attachment": f'photo{find_user_id}_{item[2]}',
                                                    'random_id': 0})
                user_url = f'https://vk.com/id{find_user_id}'
                bot.Bot().write_msg(user_id, f"{first_name} {last_name} {user_url}")
                bot.Bot().write_msg(user_id, f'Отправьте в чат "+", чтобы добавить в избраное и продолжить\n'
                                              f'или любой символ для продолжения без сохранения\n'
                                              f'Для выхода отправьте "exit"')
                if bot.Bot().choose_from_find(find_user_id, max_3_photos) == False:
                    break

    # Поиск
    def search_users(self, user_info):
        if user_info['sex'] == 2:
            gender = user_info['sex'] - 1
        else:
            gender = user_info['sex'] + 1
        response = requests.get("https://api.vk.com/method/users.search",
                                params={"access_token": self.vk_token, "v": "5.131", "count": "1000",
                                        'has_photo': '1', 'sex': gender, 'status': user_info['relation'],
                                        'city': user_info['city'], 'age_from': user_info['age'] - 5,
                                        'age_to': user_info['age'] + 5})
        response.raise_for_status()
        users_list = response.json()['response']['items']
        find_list = [(user['id'], user['first_name'],
                  user['last_name']) for user in users_list if user['is_closed'] == False]

        return find_list