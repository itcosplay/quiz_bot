import os
import random
import logging

from environs import Env

from vk_api import VkApi
from vk_api.longpoll import VkEventType
from vk_api.longpoll import VkLongPoll
from vk_api.keyboard import VkKeyboard
from vk_api.keyboard import VkKeyboardColor


logger = logging.getLogger(__name__)


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1,1000))


def main():
    env = Env()
    env.read_env()

    logging.basicConfig (
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    vk_session = VkApi(token=os.environ['VK_GROUP_TOKEN'])
    vk_api = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Белая кнопка', color=VkKeyboardColor.DEFAULT)
    keyboard.add_button('Зелёная кнопка', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()  # Переход на вторую строку
    keyboard.add_button('Красная кнопка', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Синяя кнопка', color=VkKeyboardColor.PRIMARY)
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                echo(event, vk_api)


if __name__ == '__main__':
    main()