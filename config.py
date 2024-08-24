from dotenv import load_dotenv
import os

DATABASE_NAME = 'data/food_ordering_system.db'

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем переменные из окружения
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
PAYMENT_API_KEY = os.getenv('PAYMENT_API_KEY')

# if not TELEGRAM_API_TOKEN:
#     raise ValueError("No BOT_TOKEN set for application")