from environs import Env

env = Env()
env.read_env()

APP_ENV = env.str('APP_ENV')
DATABASE_USERNAME = env.str('DATABASE_USERNAME')
DATABASE_PASSWORD = env.str('DATABASE_PASSWORD')
DATABASE_HOST = env.str('DATABASE_HOST')
DATABASE_NAME = env.str('DATABASE_NAME')
TEST_DATABASE_NAME = env.str('DATABASE_NAME')
REDIS_HOST = env.str('REDIS_HOST')
REDIS_PORT = env.str('REDIS_PORT')
REDIS_DB = env.str('REDIS_DB', '0' if APP_ENV == 'TESTING' else '0')

BASE_URL = env.str('BASE_URL')

BOT_TOKEN = env.str('BOT_TOKEN')

XAPIKEY = env.str('XAPIKEY')
