from environs import Env
from redis import Redis


env = Env()
env.read_env()

redis_db = Redis(
    host=env('REDIS_HOST'),
    port=env('REDIS_PORT'), 
    password=env('REDIS_PASSWORD'))

redis_db.set('hello', 'world')
print(redis_db.get('hello'))