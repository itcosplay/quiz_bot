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


def get_short_answer(unswer):
    return unswer.replace(
        ',', '.').replace(
        '(', '.').replace('"', '.').split('.')[0].strip().lower()


def get_explanation(right_answer):
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

    if current_user_score:
        current_user_score = int(current_user_score) + 1
        connect.set(f'{user_id}_score', current_user_score)

    else:
        connect.set(f'{user_id}_score', 1)


def get_or_set_vk_user_state(connect, user_id):
    '''
    If user has state - return state,
    else will be created new state and returned one
    '''
    user_state = connect.get(f'{user_id}_state')

    if not user_state:
        connect.set(f'{user_id}_state', 'NEUTRAL')

        return('NEUTRAL')

    else:
        return user_state
