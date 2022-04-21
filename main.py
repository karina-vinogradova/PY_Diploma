from bot import Bot
from vk import VK


# Старт кода
if __name__ == '__main__':
    

    #Запуск бота
    while True:
        message_text, user_id = Bot().vk_bot()
        if message_text != '':
            Bot().greeting_bot(user_id)
            message_text, user_id = Bot().vk_bot()
            if message_text.lower() == 'vkinder':
                Bot().greeting_bot(user_id)
            elif message_text.lower() == 'go':
                user_info = VK().get_info_for_search(user_id)
                VK().show_users(user_id, user_info)
            elif message_text.lower() == 'exit':
                Bot().write_msg(user_id, f"До скорого!")
            else:
                Bot().write_msg(user_id, 'Простите, я не знаю такой команды')

