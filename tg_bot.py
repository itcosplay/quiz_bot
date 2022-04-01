import logging
from turtle import right, update

from environs import Env

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.ext import Filters
from telegram.ext import ConversationHandler

from utils import create_redis_connect
from utils import get_question
from utils import check_answer
from utils import get_explanation
from utils import set_user_score


logging.basicConfig (
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

env = Env()
env.read_env()

connect = create_redis_connect()

quiz_keyboard = [
    ['Новый вопрос', 'Сдаться'], 
    ['Мой счет']
]

reply_markup = ReplyKeyboardMarkup(quiz_keyboard, resize_keyboard=True)

ASKED_QUESTION =  range(1)


def start(update: Update, _):
    update.message.reply_text(
        text="I'm a quiz bot, let's play! (Use keyboard please)",
        reply_markup=reply_markup)


def send_question(update: Update, _):
    user_id = update.message.from_user.id

    current_question = get_question(connect)
    connect.set(user_id, current_question)
    print('right answer: ', connect.hget('question', current_question))

    update.message.reply_text(text=current_question)

    return ASKED_QUESTION


def handle_answer(update, _):
    user_answer = update.message.text

    if user_answer == 'Новый вопрос':
        update.message.reply_text('Чтобы получить следующий вопрос, вам необходимо дать ответ на текущий :)')
        return ASKED_QUESTION
    
    if user_answer == 'Сдаться':
        give_up(update, _)
        return

    if user_answer == 'Мой счет':
        update.message.reply_text('Чтобы увидеть счет, ответьте на вопрос :)')
        return ASKED_QUESTION

    user_id = update.message.from_user.id
    current_question = connect.get(user_id)
    
    if check_answer(connect, current_question, user_answer):
        additional_answer = get_explanation(connect, current_question)
        text = 'Правильно! Поздравляю!'
        text += f' {additional_answer}'
        text += '\n\nДля следующего вопроса нажми «Новый вопрос»'
        
        set_user_score(connect, user_id)

        update.message.reply_text(text)
        return ConversationHandler.END
    
    else:
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return ASKED_QUESTION


def give_up(update, _):
    user_id = update.message.from_user.id
    current_question = connect.get(user_id)

    right_answer = connect.hget('question', current_question)

    text = 'Что ж, вот какой был правильный ответ:'
    text += f'\n{right_answer}'
    text += '\n\nВот другой вопрос'
    update.message.reply_text(text)

    current_question = get_question(connect)
    connect.set(user_id, current_question)
    print('right answer: ', connect.hget('question', current_question))

    update.message.reply_text(current_question)

    return ASKED_QUESTION


def leave_quiz(update, _):
    update.message.reply_text('Вы покинули виктрорину, если захотите сыграть еще, нажмите «Новый вопрос»')
    return ConversationHandler.END

def show_score(update, _):
    user_id = update.message.from_user.id
    user_id = str(user_id)
    user_score = connect.get(f'{user_id}_score')

    text = f'Правильных ответов: {user_score}'

    update.message.reply_text(text)

def main():
    """Start the bot."""

    updater = Updater(env('TG_BOT_TOKEN'), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler
    
    dp.add_handler(
        ConversationHandler (
            entry_points=[MessageHandler(Filters.regex('^(Новый вопрос)$'), send_question)],
            states = {
                ASKED_QUESTION: [MessageHandler(Filters.text & (~Filters.command), handle_answer)]
            },
            fallbacks=[CommandHandler('refuse', leave_quiz)])
        )
    
    dp.add_handler(MessageHandler(Filters.regex('^(Мой счет)$'), show_score))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()