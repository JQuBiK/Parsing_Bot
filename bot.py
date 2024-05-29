import logging
import time
import schedule
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, SessionPasswordNeededError
from telethon.tl.types import PeerChannel
from datetime import datetime, timedelta, timezone
from telegram import Bot
from telegram.error import BadRequest
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Параметры Telethon
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
source_channels = [os.getenv(f'SOURCE_CHANNEL_{i}') for i in range(1, 9)]  # Увеличено до 8 каналов

# Параметры Telegram Bot
bot_token = os.getenv('BOT_TOKEN')
target_channel_id = os.getenv('TARGET_CHANNEL_ID')

# Ключевые слова для фильтрации сообщений
KEYWORDS = ['Bitrix', 'bitrix', 'Bitrix24', 'bitrix24', 'Bitrix 24', 'bitrix 24', 'Битрик24', 'битрикс24', 'Битрикс',
            'битрикс', 'Битрик 24', 'битрик 24']

# Создаем клиент Telethon с сессионным файлом пользователя
client = TelegramClient('user_session', api_id, api_hash)

# Создаем бота Telegram
bot = Bot(token=bot_token)


async def fetch_and_forward_messages():
    try:
        for channel in source_channels:
            if not channel:
                continue
            try:
                entity = await client.get_input_entity(channel)
                logger.info(
                    f"Fetching messages from channel {channel} (ID: {entity.channel_id if isinstance(entity, PeerChannel) else 'N/A'})")

                channel_name = (await client.get_entity(entity)).title

                # Получаем сообщения за последние 5 минут
                end_time = datetime.now(timezone.utc)
                start_time = end_time - timedelta(minutes=5)

                async for message in client.iter_messages(entity, offset_date=end_time):
                    if message.date < start_time:
                        break
                    if message.message and any(keyword in message.message for keyword in KEYWORDS):
                        try:
                            sender = await message.get_sender()
                            sender_name = sender.username if sender.username else sender.first_name
                            text = f"Канал: {channel_name}\nАвтор: {sender_name}\n\n{message.message}"
                            if message.media:
                                file_path = await message.download_media()
                                with open(file_path, 'rb') as file:
                                    await bot.send_photo(chat_id=target_channel_id, photo=file, caption=text)
                            else:
                                await bot.send_message(chat_id=target_channel_id, text=text)
                            time.sleep(1)  # Задержка между сообщениями
                        except FloodWaitError as e:
                            logger.warning(f"Flood wait error: sleeping for {e.seconds} seconds")
                            time.sleep(e.seconds)
                        except BadRequest as e:
                            logger.error(f"Bad request error: {e}")
                        except Exception as e:
                            logger.error(f"Error sending message: {e}")
            except Exception as e:
                logger.error(f"Error processing channel {channel}: {e}")
    except Exception as e:
        logger.error(f"Error fetching or forwarding messages: {e}")


def job():
    client.loop.run_until_complete(fetch_and_forward_messages())


def main():
    try:
        # Запускаем Telethon клиента с сессионным файлом пользователя
        client.start()
    except SessionPasswordNeededError:
        logger.error("Two-step verification is enabled. Please provide your password.")
        return
    except Exception as e:
        logger.error(f"Error starting client: {e}")
        return

    # Планируем выполнение задачи каждые 5 минут
    schedule.every(5).minutes.do(job)

    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            logger.error(f"Error in schedule: {e}")
        time.sleep(1)


if __name__ == '__main__':
    main()