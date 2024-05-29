from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')

# Создаем клиент Telethon и запускаем его
client = TelegramClient('user_session', api_id, api_hash)

async def main():
    await client.start(phone)
    print("Client Created")

with client:
    client.loop.run_until_complete(main())
