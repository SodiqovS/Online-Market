from environs import Env

env = Env()
env.read_env()

APP_ENV = env.str('APP_ENV', 'development')
DATABASE_USERNAME = env.str('DATABASE_USERNAME', 'sodiqovs')
DATABASE_PASSWORD = env.str('DATABASE_PASSWORD', '1221')
DATABASE_HOST = env.str('DATABASE_HOST', 'localhost')
DATABASE_NAME = env.str('DATABASE_NAME', 'optomdb')
TEST_DATABASE_NAME = env.str('DATABASE_NAME', 'test_optomdb')
REDIS_HOST = env.str('REDIS_HOST', '127.0.0.1')
REDIS_PORT = env.str('REDIS_PORT', '6379')
REDIS_DB = env.str('REDIS_DB', '0' if APP_ENV == 'TESTING' else '0')

BASE_URL = env.str('BASE_URL', 'http://localhost:8000')


BOT_TOKEN = env.str('BOT_TOKEN')

XAPIKEY = env.str('XAPIKEY')
