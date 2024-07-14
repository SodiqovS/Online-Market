import os
from dotenv import load_dotenv
load_dotenv()

APP_ENV = os.getenv('APP_ENV', 'development')
DATABASE_USERNAME = os.getenv('DATABASE_USERNAME', 'sodiqovs')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', '1221')
DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'optomdb')
TEST_DATABASE_NAME = os.getenv('DATABASE_NAME', 'test_optomdb')
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = os.getenv('REDIS_DB', '0' if APP_ENV == 'TESTING' else '0')

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

BOT_TOKEN = os.getenv('BOT_TOKEN', '5029844586:AAEamXOIHkKBZa8UM3wbnoVNfqkX8XD78vk')
