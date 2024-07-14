# telegram_bot.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
import random

from ecommerce import config, redis_config

TOKEN = config.BOT_TOKEN
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())


def get_contact_button():
    button = ReplyKeyboardMarkup(resize_keyboard=True)
    contact = KeyboardButton(text='Kontaktni yuborish 📱', request_contact=True)
    button.add(contact)
    return button


@dp.message_handler(commands=['start', 'login'])
async def send_welcome(message: types.Message):
    msg = (f"Salom {message.from_user.first_name} 👋\n"
           f"'Online Marketning'ning rasmiy botiga xush kelibsiz\n\n"
           f"⬇️ Kontaktingizni yuboring (tugmani bosib)")
    await message.answer(msg, reply_markup=get_contact_button())


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def check_contact(message: types.Message):
    if message.from_user.id == message.contact.user_id:
        code = generate_code()
        telegram_id = message.from_user.id
        phone_number = message.contact.phone_number
        redis_config.redis_client.setex(code, 300, telegram_id)
        redis_config.redis_client.setex(telegram_id, 300, phone_number)
        msg = (f"🔒 Kodingiz: \n"
               f"{code}")
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
        await message.answer("Kodni ilovamizga kiriting \n🔑 Yangi kod olish uchun /login ni bosing")
    else:
        await message.answer("Shahsiy kontaktingizni yuboring")


def generate_code():
    number = '123456789'
    return ''.join(random.choice(number) for i in range(6))


def run_bot():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    run_bot()
