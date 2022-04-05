import argparse
import logging
import os

from environs import Env

from utils import create_redis_connect


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def get_text_by_index(list, start_index):
    text = ''

    for index in range(start_index, len(list)):
        if list[index-1].startswith('\n'):
            return text[:-1]

        elif not list[index].startswith('\n'):
            text += list[index]
            text = text.replace('\n', ' ')


def get_questions_from_file(from_folder, file):
    with open(
        f'{from_folder}/{file}', 'r', encoding='KOI8-R'
    ) as questions_file:
        questions_file_rows = [row for row in questions_file]

    quizzes = []
    for index, row in enumerate(questions_file_rows):

        if row.startswith('Вопрос') and \
                questions_file_rows[index-1].startswith('\n'):

            quiz = {
                'question': None,
                'answer': None
            }

            quiz['question'] = get_text_by_index(
                list=questions_file_rows,
                start_index=index + 1
            )

        if row.startswith('Ответ') and \
                questions_file_rows[index-1].startswith('\n'):

            quiz['answer'] = get_text_by_index(
                list=questions_file_rows,
                start_index=index + 1)

            quizzes.append(quiz)

            quiz = {
                'question': None,
                'answer': None
            }

    return quizzes


def load_questions_to_redis_db(quizzes, connect):
    for quiz in quizzes:
        connect.hset(
            name='question',
            key=quiz['question'],
            value=quiz['answer']
        )


def main():
    '''Load questions from folders' files.txt to Redis'''
    env = Env()
    env.read_env()

    parser = argparse.ArgumentParser(
        description='Выгружает вопросы из папки в Redis'
    )
    parser.add_argument(
        '-f', '--folder', default='questions', help='Наименование папки'
    )
    parser.parse_args()
    args = parser.parse_args()

    folder = args.folder

    if not os.path.isdir(folder):
        logger.error('Folder "questions" is not exists...')
        return

    host = env('REDIS_HOST')
    port = env('REDIS_PORT')
    password = env('REDIS_PASSWORD')

    connect = create_redis_connect(host, port, password)

    for file in os.listdir(folder):
        quizzes = get_questions_from_file(folder, file)
        load_questions_to_redis_db(quizzes, connect)
        print(f'questions from {file} was uploaded')


if __name__ == '__main__':
    main()
