import logging
from telethon import TelegramClient, events
import asyncio
from dotenv import load_dotenv
import os
from telethon.errors import FloodWaitError

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем параметры из .env файла
load_dotenv()

# Настройки для Telegram API из .env файла
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
channel_ids = [int(channel_id) for channel_id in os.getenv('CHANNEL_IDS').split(',')]
target_channel_id = int(os.getenv('TARGET_CHANNEL_ID'))

# Список ключевых слов для фильтрации сообщений
keywords = [
    'Bitrix', 'bitrix', 'Bitrix24', 'bitrix24', 'Bitrix 24', 'bitrix 24', 'Битрикс24', 'битрикс24', 'Битрикс',
    'битрикс', 'Битрикс 24', 'битрикс 24', 'Амо', 'АмоСРМ', 'aмоСРМ', 'Амоcrm', 'aмоcrm', 'AMOСРМ', 'AmoСРМ',
    'СРМ', 'CRM', 'B24', 'b24', 'Б24', 'б24', 'Автоматизация', 'автоматизация', 'Рассылка', 'рассылка',
    'рекламные каналы', 'Рекламные каналы', 'Сквозная аналитика', 'сквозная аналитика', 'Проекты', 'проекты',
    'Проект', 'проект', 'Лиды', 'лиды', 'Лид', 'лид'
]

# Создаем клиента
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)

# Словарь для хранения последних обработанных сообщений для каждого канала
last_processed_message_id = {channel_id: 0 for channel_id in channel_ids}


async def check_messages():
    while True:
        logger.info("Бот читает сообщения")
        await asyncio.sleep(180)  # Ждем 3 минуты
        for channel_id in channel_ids:
            logger.info(f"Бот собирает сообщения из канала {channel_id}")
            try:
                async for message in client.iter_messages(channel_id, limit=10):  # Получаем последние 10 сообщений
                    if message.id > last_processed_message_id[channel_id]:
                        if message.message and any(keyword in message.message for keyword in keywords):
                            await client.forward_messages(target_channel_id, message)
                            last_processed_message_id[channel_id] = message.id
                            logger.info(f"Бот переслал сообщение из канала {channel_id} в целевой канал")
            except FloodWaitError as e:
                logger.warning(f"Flood wait error: ждем {e.seconds} секунд перед повторной попыткой")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщений из канала {channel_id}: {e}")
                await asyncio.sleep(10)  # Задержка перед повторной попыткой в случае ошибки


async def main():
    logger.info("Бот запущен")
    try:
        # Запускаем задачу для периодической проверки сообщений
        client.loop.create_task(check_messages())

        # Ожидание завершения работы клиента
        await client.run_until_disconnected()
    except Exception as e:
        logger.error(f"Ошибка в основном процессе: {e}")


# Запуск клиента
with client:
    logger.info("Бот подключен")
    client.loop.run_until_complete(main())