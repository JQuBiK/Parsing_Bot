from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerChannel
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')
source_channels = [os.getenv(f'SOURCE_CHANNEL_{i}') for i in range(1, 9)]

# Создаем клиент Telethon и запускаем его
client = TelegramClient('check_channels_session', api_id, api_hash)


async def main():
    await client.start(phone)

    for channel in source_channels:
        if not channel:
            continue
        try:
            entity = await client.get_input_entity(channel)
            if isinstance(entity, InputPeerChannel):
                channel_id = entity.channel_id
            else:
                channel_id = entity.user_id
            channel_name = (await client.get_entity(entity)).title if hasattr(entity, 'title') else "Неизвестный канал"
            print(f"Channel: {channel}, ID: {channel_id}, Name: {channel_name}")
        except Exception as e:
            print(f"Cannot access channel {channel}: {e}")


with client:
    client.loop.run_until_complete(main())