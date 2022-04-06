import os
import random
import logging

from environs import Env

from vk_api import VkApi
from vk_api.longpoll import VkEventType
from vk_api.longpoll import VkLongPoll
from vk_api.keyboard import VkKeyboard
from vk_api.keyboard import VkKeyboardColor

from utils import create_redis_connect
from utils import check_answer
from utils import get_explanation
from utils import set_user_score
from utils import get_or_set_vk_user_state


logger = logging.getLogger(__file__)


def handle_commands(event, vk_api, connect):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.POSITIVE)

    user_id=event.user_id

    if event.text == "Новый вопрос":
        user_state = get_or_set_vk_user_state(connect, user_id)

        if user_state == 'NEUTRAL':
            current_question = connect.hrandfield('question')
            connect.set(user_id, current_question)
            connect.set(f'{user_id}_state', 'ASKED_QUESTION')

            vk_api.messages.send(
                user_id=user_id,
                message=current_question,
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))

        else:
            vk_api.messages.send(
                user_id=user_id,
                message='Чтобы получить следующий вопрос, вам необходимо дать ответ на текущий :)',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))

    elif event.text == 'Сдаться':
        user_state = get_or_set_vk_user_state(connect, user_id)

        if user_state == 'ASKED_QUESTION':
            current_question = connect.get(user_id)
            right_answer = connect.hget('question', current_question)

            text = 'Что ж, вот какой был правильный ответ:'
            text += f'\n{right_answer}'
            text += '\n\nВот другой вопрос'

            vk_api.messages.send(
                user_id=user_id,
                message=text,
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))

            current_question = connect.hrandfield('question')
            connect.set(user_id, current_question)

            vk_api.messages.send(
                user_id=user_id,
                message=current_question,
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))

        else:
            vk_api.messages.send(
                user_id=user_id,
                message='Используйте меню чтобы сыграть в викторину ;)',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))

    elif event.text == 'Мой счет':
        user_state = get_or_set_vk_user_state(connect, user_id)

        if user_state == 'NEUTRAL':
            user_score = connect.get(f'{user_id}_score')
            text = f'Правильных ответов: {user_score}'

            vk_api.messages.send(
                    user_id=user_id,
                    message=text,
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1,1000))
        
        else:
            vk_api.messages.send(
                user_id=user_id,
                message='Чтобы увидеть счет, ответьте на вопрос :)',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))
    
    else:
        user_state = get_or_set_vk_user_state(connect, user_id)

        if user_state == 'NEUTRAL':
            vk_api.messages.send(
                user_id=user_id,
                message='Используйте меню чтобы сыграть в викторину ;)',
                keyboard=keyboard.get_keyboard(),
                random_id=random.randint(1,1000))
        
        if user_state == 'ASKED_QUESTION':
            user_answer = event.text
            current_question = connect.get(user_id)
            if check_answer(connect, current_question, user_answer):
                connect.set(f'{user_id}_state', 'NEUTRAL')
                additional_answer = get_explanation(connect, current_question)
                text = 'Правильно! Поздравляю!'
                text += f' {additional_answer}'
                text += '\n\nДля следующего вопроса нажми «Новый вопрос»'

                set_user_score(connect, user_id)

                vk_api.messages.send(
                    user_id=user_id,
                    message=text,
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1,1000))
            
            else:
                vk_api.messages.send(
                    user_id=user_id,
                    message='Неправильно… Попробуешь ещё раз?',
                    keyboard=keyboard.get_keyboard(),
                    random_id=random.randint(1,1000))


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    connect = create_redis_connect(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('REDIS_PASSWORD')
    )

    vk_session = VkApi(token=os.environ['VK_GROUP_TOKEN'])
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_commands(event, vk_api, connect)


if __name__ == '__main__':
    main()