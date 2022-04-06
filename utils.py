from redis import Redis


def create_redis_connect(host, port, password):
    connect = Redis(
        host=host,
        port=port,
        password=password,
        decode_responses=True
    )

    if connect.ping():
        return connect


def check_answer(connect, question, user_answer):
    right_answer = connect.hget('question', question)
    return get_short_answer(user_answer) == get_short_answer(right_answer)


def get_short_answer(unswer):
    return unswer.replace(
        ',', '.').replace(
        '(', '.').replace('"', '.').split('.')[0].strip().lower()


def get_explanation(connect, question):
    right_answer = connect.hget('question', question)
    index = 0
    for char in right_answer:
        if char == '.':
            index += 1
            break
        if char == ',':
            break
        if char == '(':
            index -= 1
            break

        index += 1

    explanation = right_answer[index:].strip()

    if len(explanation) > 2:

        return right_answer[index:]

    return ''


def set_user_score(connect, user_id):
    current_user_score = connect.get(f'{user_id}_score')
    user_id = str(user_id)

    if current_user_score is None:
        connect.set(f'{user_id}_score', 1)

    else:
        current_user_score = int(current_user_score) + 1
        connect.set(f'{user_id}_score', current_user_score)


def get_or_set_vk_user_state(connect, user_id):
    '''
    If user has state - return state,
    else will be created new state and returned one
    '''
    user_id = str(user_id)
    user_state = connect.get(f'{user_id}_state')

    if user_state is None:
        connect.set(f'{user_id}_state', 'NEUTRAL')
        return('NEUTRAL')

    else:
        return user_state
