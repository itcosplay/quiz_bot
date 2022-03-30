import json

from environs import Env

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, Updater, CommandHandler, MessageHandler
from telegram.ext import Filters
import logging

logging.basicConfig (
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

env = Env()
env.read_env()

quiz_keyboard = [
    ['Новый вопрос', 'Сдаться'], 
    ['Мой счет']
]


reply_markup = ReplyKeyboardMarkup(quiz_keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext):
    context.bot.send_message (
        chat_id=update.effective_chat.id,
        text="I'm a quiz bot, let's play!",
        reply_markup=reply_markup
    )


def update_user_data(user_data):
    with open('users_data.json') as json_file:
        users_data = json.load(json_file)

    is_user_exists = False
    for user in users_data:
        print(user)
        print(user_data['user_id'])

        if user['user_id'] == user_data['user_id']:
            user['current_question'] = user_data['current_question']
            user['score'] = user_data['score']
            is_user_exists = True
            print('we_are_here')
            break
    
    if not is_user_exists:
        users_data.append(user_data)

    with open("users_data.json", "w") as write_file:
        json.dump(users_data, write_file, )


def send_question(update: Update, context: CallbackContext):
    if update.message.text == 'Новый вопрос':
        with open('quiz_data.json') as json_file:
            questions = json.load(json_file)
        
        current_question = questions[0]['question']

        user_data = {
            'user_id': update.message.from_user.id,
            'current_question': current_question,
            'score': 0
        }

        update_user_data(user_data)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=questions[0]['question'],
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='zzz...',
        )


def main():
    """Start the bot."""

    updater = Updater(env('TG_BOT_TOKEN'), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(
        MessageHandler(Filters.text, send_question)
    )

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()