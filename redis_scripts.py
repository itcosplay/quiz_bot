from environs import Env
from redis import Redis

env = Env()
env.read_env()


def create_redis_connect():
    connect = Redis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'), 
        password=env('REDIS_PASSWORD'))

    if connect.ping():
        return connect
        
    else:
        raise