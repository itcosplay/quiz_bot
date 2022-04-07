import logging

from environs import Env

from enum import Enum

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler

from redis_scripts import create_redis_connect
from redis_scripts import set_user_score
from answers_handlers import get_short_answer
from answers_handlers import get_explanation


logger = logging.getLogger(__file__)


class DialogStatus(Enum):
    ASKED_QUESTION = 1


def start(update, _):
    quiz_keyboard = [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']
    ]

    reply_markup = ReplyKeyboardMarkup(quiz_keyboard, resize_keyboard=True)

    update.message.reply_text(
        text="I'm a quiz bot, let's play! (Use keyboard please)",
        reply_markup=reply_markup
    )


def send_question(update, context):
    user_id = update.message.from_user.id
    connect = context.bot_data.get('connect')

    current_question = connect.hrandfield('question')
    connect.set(user_id, current_question)

    update.message.reply_text(text=current_question)

    return DialogStatus.ASKED_QUESTION


def handle_answer(update, context):
    user_answer = update.message.text

    if user_answer == 'Новый вопрос':
        update.message.reply_text(
            'Чтобы получить следующий вопрос,'
            ' вам необходимо дать ответ на текущий :)'
        )

        return DialogStatus.ASKED_QUESTION

    if user_answer == 'Сдаться':
        give_up(update, context)

        return

    if user_answer == 'Мой счет':
        update.message.reply_text('Чтобы увидеть счет, ответьте на вопрос :)')

        return DialogStatus.ASKED_QUESTION

    connect = context.bot_data.get('connect')

    user_id = update.message.from_user.id
    current_question = connect.get(user_id)
    right_answer = connect.hget('question', current_question)

    if get_short_answer(user_answer) == get_short_answer(right_answer):
        set_user_score(connect, user_id)

        explanation = get_explanation(right_answer)

        text = 'Правильно! Поздравляю!'
        text += f' {explanation}'
        text += '\n\nДля следующего вопроса нажми «Новый вопрос»'

        update.message.reply_text(text)

        return ConversationHandler.END

    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')

        return DialogStatus.ASKED_QUESTION


def give_up(update, context):
    connect = context.bot_data.get('connect')
    user_id = update.message.from_user.id
    current_question = connect.get(user_id)

    right_answer = connect.hget('question', current_question)

    text = 'Что ж, вот какой был правильный ответ:'
    text += f'\n{right_answer}'
    text += '\n\nВот другой вопрос'
    update.message.reply_text(text)

    current_question = connect.hrandfield('question')
    connect.set(user_id, current_question)

    update.message.reply_text(current_question)

    return DialogStatus.ASKED_QUESTION


def leave_quiz(update, _):
    update.message.reply_text(
        'Вы покинули виктрорину,'
        ' если захотите сыграть еще, нажмите «Новый вопрос»'
    )

    return ConversationHandler.END


def show_score(update, context):
    connect = context.bot_data.get('connect')
    user_id = update.message.from_user.id
    user_score = connect.get(f'{user_id}_score')

    text = f'Правильных ответов: {user_score}'

    update.message.reply_text(text)


def main():
    """Start the bot."""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    env = Env()
    env.read_env()

    connect = create_redis_connect(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('REDIS_PASSWORD')
    )

    updater = Updater(env('TG_BOT_TOKEN'), use_context=True)
    updater.dispatcher.bot_data.update({'connect': connect})

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(
        ConversationHandler(
            entry_points=[
                MessageHandler(
                    Filters.regex('^(Новый вопрос)$'),
                    send_question
                )
            ],
            states={
                DialogStatus.ASKED_QUESTION: [
                    MessageHandler(
                        Filters.text & (~Filters.command),
                        handle_answer
                    )
                ]
            },
            fallbacks=[CommandHandler('refuse', leave_quiz)]
        )
    )
    dp.add_handler(MessageHandler(Filters.regex('^(Мой счет)$'), show_score))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
