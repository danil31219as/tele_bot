import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from refbot import RefBot
import requests

TOKEN = 'd0e6e53559580aa6e56608dd0850968ac79d90cc4f78ee875762790c2813440741703c484fdf526d837cf'
GROUP_ID = 194612355


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            bot = RefBot(vk, event.obj.message['from_id'], event.obj.message)
            try:
                bot.analyse_message()
            except Exception as e:
                print(e)
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message='Что-то пошло не так, попробуйте еще раз.',
                                 random_id=random.randint(0, 2 ** 64))


if __name__ == '__main__':
    main()
