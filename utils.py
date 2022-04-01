from itertools import count
from multiprocessing import connection
from turtle import right
from environs import Env
from redis import Redis

env = Env()
env.read_env()


def create_redis_connect():
    connect = Redis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'), 
        password=env('REDIS_PASSWORD'),
        decode_responses=True)

    if connect.ping():
        return connect
        
    else:
        raise


def get_question(connect):
    question = connect.hrandfield('question')
    # answer = connect.hget('question', question)

    return question


def check_answer(connect, question, user_answer):
    right_answer = connect.hget('question', question)
    return get_short_answer(user_answer) == get_short_answer(right_answer)


def get_short_answer(unswer):
    return unswer.replace(
        ',', '.').replace('(', '.').split('.')[0].strip().lower()


def get_explanation(connect, question):
    right_answer = connect.hget('question', question)
    index = 0
    for char in right_answer:
        if char == '.':
            index += 1
            break
        if char == ',':
            break
        if char =='(':
            index -= 1
            break

        index += 1

    explanation = right_answer[index:].strip()

    if len(explanation) > 2: 
        return right_answer[index:]
    
    else:
        return ''


def set_user_score(connect, user_id):
    current_user_score = connect.get(f'{user_id}_score')
    user_id = str(user_id)

    if current_user_score is None:
        connect.set(f'{user_id}_score', 1)
    
    else:
        current_user_score = int(current_user_score) + 1
        connect.set(f'{user_id}_score', current_user_score)


if __name__ == '__main__':
    pass