import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

import re
import asyncio

load_dotenv()
TOKEN = os.getenv('TOKEN')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')


def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email)


def send_email(recipient_email, subject, body):
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_LOGIN
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
            server.sendmail(EMAIL_LOGIN, recipient_email, message.as_string())
        return True
    except Exception as e:
        print(f"Ошибка отправки письма: {e}")
        return False


class EmailForm(StatesGroup):
    waiting_for_email = State()
    waiting_for_message = State()


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


@dp.message(F.text == "/start")
async def start_command(message: types.Message, state: FSMContext):
    await state.set_state(EmailForm.waiting_for_email)
    await message.answer("Привет! Введите ваш email:")


@dp.message(EmailForm.waiting_for_email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text.strip()
    if is_valid_email(email):
        await state.update_data(email=email)
        await state.set_state(EmailForm.waiting_for_message)
        await message.answer("Email принят! Теперь введите текст сообщения:")
    else:
        await message.answer("Пожалуйста, введите корректный email:")


@dp.message(EmailForm.waiting_for_message)
async def get_message(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data["email"]
    text = message.text.strip()

    if send_email(email, "Тестовое письмо от бота", text):
        await message.answer("Письмо успешно отправлено!")
    else:
        await message.answer("Произошла ошибка при отправке письма.")

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
