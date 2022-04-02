import logging
import os

from utils import create_redis_connect


logging.basicConfig (
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def get_text_by_index(list, start_index):
    text = ''

    for row_index in range(start_index, len(list)):
        if list[row_index-1].startswith('\n'):
            return text[:-1]

        elif not list[row_index].startswith('\n'):
            text += list[row_index]
            text = text.replace('\n', ' ')

    return None
     

def get_questions_from_file(from_folder, file):
    with open(f'{from_folder}/{file}', 'r', encoding='KOI8-R') as questions_file:
        questions_file_rows = [row for row in questions_file]

    questions_and_answers = []
    for row_index in range(0, len(questions_file_rows)):

        if questions_file_rows[row_index].startswith('Вопрос') \
            and questions_file_rows[row_index-1].startswith('\n'):
            question_answer = {
                'question': None,
                'answer': None
            }

            question_answer['question'] = get_text_by_index(
                list = questions_file_rows,
                start_index = row_index + 1)

        if questions_file_rows[row_index].startswith('Ответ') \
            and questions_file_rows[row_index-1].startswith('\n'):
            question_answer['answer'] = get_text_by_index(
                list = questions_file_rows,
                start_index = row_index + 1)

            questions_and_answers.append(question_answer)

            question_answer = {
                'question': None,
                'answer': None
            }

    return questions_and_answers


def load_questions_to_redis_db(questions):
    connect = create_redis_connect()
    for question in questions:
        connect.hset(
            name='question',
            key=question['question'],
            value=question['answer'])


def main(from_folder='questions'):
    '''Load questions from folders' files.txt to Redis'''

    if not os.path.isdir(from_folder):
        logger.error('Folder "questions" is not exists...')
        return

    for file in os.listdir(from_folder):
        questions = get_questions_from_file(from_folder, file)
        load_questions_to_redis_db(questions)
        print(f'questions from {file} was uploaded')
    

if __name__ == '__main__':
    main()
    



