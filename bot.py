from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from sql_uploader import SqlUploader
from token_vk import token, group_token 
import vk

class Bot:

    def __init__(self):
        self.token = token
        self.group_token = group_token
        self.vk = vk_api.VkApi(token=self.group_token)
        self.longpoll = VkLongPoll(self.vk)

    # Сообщение пользователю
    def write_msg(self, user_id, message):
        self.vk.method('messages.send',
                {'user_id': user_id,
                'message': message,
                'random_id': randrange(10 ** 7),
                })

    # Ответ пользователя
    def vk_bot(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    response = event.text
                    return response, event.user_id

    #Приветствие\help
    def greeting_bot(self, user_id):
        self.write_msg(user_id, f"Привет, я бот VKinder!\n"
        f"Для поиска введите 'go'\n"
        f"Чтобы вызвать эти подсказки напишите в чате 'vkinder'\n"
        f"Чтобы выйти - exit")


    # Получить город
    def get_city(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text.lower()
                    city_id = vk.VK().check_city(request)
                    if city_id:
                        return city_id
                    else:
                        self.write_msg(event.user_id, f"Нет такого города. Попробуйте еще раз:")

    # Получить возраст
    def get_age(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text                      
                    if request.isdigit() and int(request) < 100:
                        return int(request)
                    else:
                        self.write_msg(event.user_id, f"Вы ввели не правильный возраст. Попробуйте еще раз:")
    # Получить пол
    def get_sex(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    if request.isdigit() and 0 < int(request) < 3:
                        return int(request)
                    else:
                        self.write_msg(event.user_id, f"Нет такого пола. Попробуйте еще раз:")
    
    # Получить семейное положение
    def get_relation(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    if request.isdigit() and 0 < int(request) < 8:
                        return int(request)
                    else:
                        self.write_msg(event.user_id, f"Нет такого семейного положения. Попробуйте еще раз:")

    # Добавить в избранное или закончить

    def choose_from_find(self, user_id, photo_list):
        for event in self.longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        answer = event.text
                        if answer.lower() == '+':
                            SqlUploader().upload_id_to_table(event.user_id, user_id)
                            for photo in photo_list:
                                SqlUploader().upload_photo_to_table(event.user_id, user_id, photo[3])
                            return True
                        elif answer.lower() == 'exit':
                            self.write_msg(event.user_id, f"До скорого")
                            return False
                        else:
                            return True

