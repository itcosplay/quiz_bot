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

    else:
        raise ConnectionError('There is no connect to Redis...')


def set_user_score(connect, user_id):
    current_user_score = connect.get(f'{user_id}_score')

    if current_user_score:
        current_user_score = int(current_user_score) + 1
        connect.set(f'{user_id}_score', current_user_score)

    else:
        connect.set(f'{user_id}_score', 1)


def get_vk_user_state(connect, user_id):
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
