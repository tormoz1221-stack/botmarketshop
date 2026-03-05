"""Конфигурация бота"""
import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ID администратора
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Режим работы: "webhook" или "polling" (по умолчанию polling)
MODE = os.getenv("MODE", "polling")

# URL для webhook (например, https://your-app.onrender.com)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Секретный токен для webhook (для безопасности)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your_secret_token_here")

# Название магазина
SHOP_NAME = "Лучший магазин по донату в любимые игры"

# Реквизиты для оплаты
CARD_NUMBER = "2200 0000 0000 0000"  # Номер карты
CARD_HOLDER = "Иван Иванов"  # Имя владельца

# ЮMoney кошелёк для пополнения баланса
YMONEY_WALLET = ""  # Пример: 410012345678901 карты

# Канал для отзывов
REVIEWS_CHANNEL = "https://t.me/fire_ontaxi"

# Каналы для обязательной подписки (укажите username каналов без @)
# Пример: ["channel1", "channel2", "channel3"]
REQUIRED_CHANNELS = [
    "brawlnewsfree",
    "halavabstarss",
    "brawlpassfrees"
]

# Бонус за подписку (в рублях)
SUBSCRIPTION_BONUS = 100

# URL Mini-app для кейса с голдой
CASE_APP_URL = "https://case-app-git-main-tormoz1221-stacks-projects.vercel.app/"

# URL API сервера (для миниаппа)
API_URL = os.getenv("API_URL", "http://localhost:5000")
