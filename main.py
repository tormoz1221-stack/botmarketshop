"""Бот-магазин для Telegram"""
import asyncio
import json
from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import os

from config import BOT_TOKEN, ADMIN_ID, SHOP_NAME, CARD_NUMBER, CARD_HOLDER, REVIEWS_CHANNEL, REQUIRED_CHANNELS, SUBSCRIPTION_BONUS, YMONEY_WALLET, CASE_APP_URL, API_URL, MODE, WEBHOOK_URL, WEBHOOK_SECRET

# Flask приложение для API
app = Flask(__name__)

# Корневой маршрут для проверки работы
@app.route('/', methods=['GET'])
def index():
    return 'Bot is running!'

# Хранилище для Mini-app сессий (token: user_id)
app_sessions = {}

from products import get_product, get_sub_category, get_products_by_sub_category, get_games, get_sub_categories_by_game, get_gold_rewards, get_gold_sell_price
from keyboards import (
    main_menu_keyboard, games_keyboard, sub_categories_keyboard,
    products_keyboard, product_keyboard, case_keyboard, payment_keyboard,
    payment_failed_keyboard, payment_failed_final_keyboard, profile_keyboard,
    subscription_keyboard, inventory_keyboard, gold_case_result_keyboard,
    admin_menu_keyboard, admin_orders_keyboard, admin_promos_keyboard, admin_discounts_keyboard,
    InlineKeyboardButton, InlineKeyboardMarkup
)


# Инициализация бота
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Хранилище для отслеживания категории при возврате
user_category = {}
user_game = {}  # Для отслеживания текущей игры
user_sub_category = {}  # Для отслеживания текущей подкатегории

# Хранилище для ожидающих ввода почты
pending_orders = {}

# Хранилище для ожидающих ввода промокода
pending_promo_codes = {}

# Хранилище для подтверждённых заказов
confirmed_orders = {}

# Хранилище для всех заказов (для админа)
all_orders = []

# Хранилище для отслеживания попыток оплаты
payment_attempts = {}

# Счётчик заказов
order_counter = 1

# Процент скидки при первой покупке
FIRST_PURCHASE_DISCOUNT = 30  # 30%

# Множество пользователей, совершивших первую покупку
first_time_buyers = set()

# Словарь индивидуальных скидок для пользователей (user_id: discount_percent)
user_discounts = {}

# Хранилище для балансов пользователей
user_balances = {}

# Множество пользователей, прошедших проверку подписки
verified_subscribers = set()

# Словарь промокодов (код: {owner_id, user_bonus, owner_bonus, uses, max_uses})
promo_codes = {}

# Множество пользователей, активировавших промокоды (чтобы нельзя было использовать дважды)
promo_code_users = set()

# Хранилище для инвентаря пользователей (user_id: [список наград])
user_inventory = {}

# Хранилище для купленных кейсов (user_id: [список купленных кейсов])
user_cases = {}


def load_user_data():
    """Загрузка данных пользователей из файла при запуске бота"""
    global user_balances, first_time_buyers, verified_subscribers, order_counter, user_discounts, promo_codes, promo_code_users, user_inventory
    import os
    import json
    
    # Определяем путь к файлу данных
    base_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(base_dir, "users_data.json")
    
    print(f"Загружаем данные из: {users_file}")
    print(f"Файл существует: {os.path.exists(users_file)}")
    
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            # Загружаем балансы
            user_balances = data.get("balances", {})
            # Конвертируем ключи в int если они строки
            user_balances = {int(k): v for k, v in user_balances.items()}
            
            # Загружаем список первых покупателей
            first_time_buyers = set(data.get("first_time_buyers", []))
            first_time_buyers = {int(x) for x in first_time_buyers}
            
            # Загружаем верифицированных подписчиков
            verified_subscribers = set(data.get("verified_subscribers", []))
            verified_subscribers = {int(x) for x in verified_subscribers}
            
            # Загружаем счётчик заказов
            order_counter = data.get("order_counter", 1)
            
            # Загружаем скидки пользователей
            user_discounts = data.get("user_discounts", {})
            user_discounts = {int(k): v for k, v in user_discounts.items()}
            
            # Загружаем промокоды
            promo_codes_raw = data.get("promo_codes", {})
            promo_codes = {}
            for code, info in promo_codes_raw.items():
                promo_codes[code] = {
                    "owner_id": int(info.get("owner_id", 0)),
                    "user_bonus": int(info.get("user_bonus", 0)),
                    "owner_bonus": int(info.get("owner_bonus", 0)),
                    "uses": int(info.get("uses", 0)),
                    "max_uses": int(info.get("max_uses", 0))
                }
            
            # Загружаем пользователей, активировавших промокоды
            promo_code_users_raw = data.get("promo_code_users", [])
            promo_code_users = set()
            for x in promo_code_users_raw:
                # Сохраняем как есть (это могут быть строки вида "id_promo" или числа)
                promo_code_users.add(str(x))
            
            # Загружаем инвентарь пользователей
            inventory_raw = data.get("inventory", {})
            user_inventory = {}
            for uid, items in inventory_raw.items():
                user_inventory[int(uid)] = items
            
            # Загружаем купленные кейсы пользователей
            cases_raw = data.get("user_cases", {})
            global user_cases
            user_cases = {}
            for uid, cases in cases_raw.items():
                user_cases[int(uid)] = cases
            
            print(f"Загружено данных пользователей: {len(user_balances)} балансов, {len(promo_codes)} промокодов, {len(user_inventory)} инвентарей, {len(user_cases)} кейсов")
    except FileNotFoundError:
        print("Файл users_data.json не найден, используем значения по умолчанию")
    except Exception as e:
        print(f"Ошибка загрузки данных пользователей: {e}")


def save_user_data():
    """Сохранение данных пользователей в файл"""
    global user_balances, first_time_buyers, verified_subscribers, order_counter, user_discounts, promo_codes, promo_code_users, user_inventory
    import json
    import os
    
    # Определяем путь к файлу данных
    base_dir = os.path.dirname(os.path.abspath(__file__))
    users_file = os.path.join(base_dir, "users_data.json")
    
    try:
        data = {
            "balances": user_balances,
            "first_time_buyers": list(first_time_buyers),
            "verified_subscribers": list(verified_subscribers),
            "order_counter": order_counter,
            "user_discounts": user_discounts,
            "promo_codes": promo_codes,
            "promo_code_users": list(promo_code_users),
            "inventory": user_inventory,
            "user_cases": user_cases
        }
        
        with open(users_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в: {users_file}")
    except Exception as e:
        print(f"Ошибка сохранения данных пользователей: {e}")


# Загружаем данные при импорте модуля
load_user_data()


def get_user_orders(user_id: int) -> list:
    """Получение истории заказов пользователя из файла"""
    import os
    orders = []
    
    # Определяем путь к файлу заказов
    base_dir = os.path.dirname(os.path.abspath(__file__))
    orders_file = os.path.join(base_dir, "orders.txt")
    
    print(f"Читаем заказы из: {orders_file}")
    print(f"Файл существует: {os.path.exists(orders_file)}")
    
    try:
        with open(orders_file, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Прочитано {len(content)} символов из файла заказов")
            
            # Разделяем на блоки заказов
            order_blocks = content.split("-" * 30)
            print(f"Найдено блоков: {len(order_blocks)}")
            
            for block in order_blocks:
                block = block.strip()
                if not block:
                    continue
                lines = block.split("\n")
                order_data = {}
                for line in lines:
                    if line.startswith("ID: "):
                        try:
                            order_data["user_id"] = int(line.replace("ID: ", ""))
                        except:
                            pass
                    elif line.startswith("Заказ №: "):
                        try:
                            order_data["order_id"] = int(line.replace("Заказ №: ", ""))
                        except:
                            pass
                    elif line.startswith("Товар: "):
                        order_data["product"] = line.replace("Товар: ", "")
                    elif line.startswith("Цена: "):
                        try:
                            order_data["price"] = int(line.replace("Цена: ", "").replace("₽", ""))
                        except:
                            pass
                # Если заказ принадлежит пользователю
                print(f"Проверяем заказ: {order_data.get('order_id')}, user_id в заказе: {order_data.get('user_id')}, ищем: {user_id}")
                if order_data.get("user_id") == user_id:
                    orders.append(order_data)
            # Сортируем по ID заказа (последние первые)
            orders.sort(key=lambda x: x.get("order_id", 0), reverse=True)
            print(f"Найдено заказов для user_id {user_id}: {len(orders)}")
    except FileNotFoundError:
        print("Файл orders.txt не найден")
        pass
    except Exception as e:
        print(f"Ошибка чтения заказов: {e}")
    return orders


async def check_subscription_status(user_id: int) -> bool:
    """Проверка подписки пользователя на все обязательные каналы"""
    
    for channel_username in REQUIRED_CHANNELS:
        try:
            chat = await bot.get_chat(f"@{channel_username}")
            member = await bot.get_chat_member(chat.id, user_id)
            
            # Проверяем статус подписки (для aiogram 2.x используем строковые значения)
            # Статусы: "creator", "administrator", "member", "restricted", "left", "kicked"
            if member.status in ["left", "kicked"]:
                return False
            if member.status == "restricted":
                # Если пользователь ограничен - считаем что не подписан
                return False
            # "creator", "administrator", "member", "restricted" считаются как подписка
        except Exception as e:
            print(f"Ошибка проверки подписки на {channel_username}: {e}")
            # Если не удалось проверить - пробуем другим способом
            try:
                member = await bot.get_chat_member(chat.id, user_id)
                if member.status not in ["creator", "administrator", "member"]:
                    return False
            except Exception as e2:
                print(f"Вторая ошибка проверки подписки на {channel_username}: {e2}")
                return False
    return True


# Функция сохранения заказа в файл
def save_order_to_file(order_id, product, email, user_full_name, username, user_id):
    """Сохранение информации о заказе в текстовый файл"""
    import os
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        orders_file = os.path.join(base_dir, "orders.txt")
        with open(orders_file, "a", encoding="utf-8") as f:
            f.write(f"Заказ №: {order_id}\n")
            f.write(f"Товар: {product['name']}\n")
            f.write(f"Цена: {product['price']}₽\n")
            f.write(f"Почта Supercell ID: {email}\n")
            f.write(f"Покупатель: {user_full_name}\n")
            f.write(f"Username: @{username}\n")
            f.write(f"ID: {user_id}\n")
            f.write("-" * 30 + "\n")
    except Exception as e:
        print(f"Ошибка записи в файл: {e}")


# Команда /setwebhook для установки webhook
@dp.message(Command("setwebhook"))
async def cmd_setwebhook(message: types.Message):
    """Команда для установки webhook"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    if not WEBHOOK_URL:
        await message.answer("❌ WEBHOOK_URL не настроен в .env файле!")
        return
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    
    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET
        )
        await message.answer(
            f"✅ Webhook установлен!\n\n"
            f"URL: {webhook_url}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# Команда /delwebhook для удаления webhook
@dp.message(Command("delwebhook"))
async def cmd_delwebhook(message: types.Message):
    """Команда для удаления webhook"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    try:
        await bot.delete_webhook()
        await message.answer("✅ Webhook удалён!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# Команда /cmd - список всех команд
@dp.message(Command("cmd"))
async def cmd_list(message: types.Message):
    """Показать список всех команд"""
    user_id = message.from_user.id
    
    text = "📋 Список команд:\n\n"
    text += "• /start - Запустить бота\n"
    text += "• /help - Помощь\n"
    text += "• /my_promos - Мои промокоды\n"
    
    # Если админ - показываем админские команды
    if user_id == ADMIN_ID:
        text += "\n🔧 Админ-команды:\n"
        text += "• /admin_menu - Админ-панель\n"
        text += "• /create_promo - Создать промокод\n"
        text += "• /set_discount - Установить скидку\n"
        text += "• /discounts - Список скидок\n"
    
    await message.answer(text)


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Помощь"""
    text = (
        "❓ Помощь\n\n"
        "Добро пожаловать в магазин!\n\n"
        "Как купить:\n"
        "1. Выберите товар в каталоге\n"
        "2. Оплатите по реквизитам\n"
        "3. Подтвердите оплату\n"
        "4. Получите товар\n\n"
        "Бонусы:\n"
        "• Подпишитесь на каналы - получите бонус!\n"
        "• Используйте промокоды - получайте скидки!\n\n"
        "Команды:\n"
        "• /cmd - Список команд"
    )
    await message.answer(text)


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Приветствие с проверкой подписки"""
    user_id = message.from_user.id
    
    # Проверяем, подписан ли пользователь на все каналы
    is_subscribed = await check_subscription_status(user_id)
    
    if not is_subscribed:
        # Если не подписан - показываем экран подписки
        text = (
            f"👋 Добро пожаловать в {SHOP_NAME}!\n\n"
            "📌 Для использования бота необходимо подписаться на наши каналы:\n\n"
        )
        
        for channel in REQUIRED_CHANNELS:
            text += f"• @{channel}\n"
        
        text += f"\n🎁 После подписки вы получите {SUBSCRIPTION_BONUS} рублей на баланс!\n\n"
        text += "После подписки нажмите кнопку \"Проверить подписку\""
        
        await message.answer(
            text,
            reply_markup=subscription_keyboard(REQUIRED_CHANNELS)
        )
        return
    
    # Если уже верифицирован - показываем главное меню
    await message.answer(
        f"👋 Добро пожаловать в {SHOP_NAME}!\n\n"
        "Выберите раздел:",
        reply_markup=main_menu_keyboard()
    )


# Команда /admin_menu для администратора
@dp.message(Command("admin_menu"))
async def cmd_admin_menu(message: types.Message):
    """Админ-меню"""
    user_id = message.from_user.id
    
    # Проверяем, что команду выполняет администратор
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    text = "🔧 Админ-панель\n\nВыберите раздел:"
    await message.answer(text, reply_markup=admin_menu_keyboard())


# Команда /set_discount для администратора
@dp.message(Command("set_discount"))
async def cmd_set_discount(message: types.Message):
    """Установка скидки на первую покупку (только для админа)"""
    global FIRST_PURCHASE_DISCOUNT, user_discounts
    
    user_id = message.from_user.id
    
    # Проверяем, что команду выполняет администратор
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    # Получаем аргументы команды
    args = message.text.split()
    
    # Синтаксис: /set_discount [user_id] [процент]
    # Если указан user_id - устанавливаем скидку конкретному пользователю
    # Если не указан - показываем/устанавливаем глобальную скидку
    
    if len(args) == 1:
        # Показываем текущую глобальную скидку
        await message.answer(
            f"📊 Текущая скидка на первую покупку: {FIRST_PURCHASE_DISCOUNT}%\n\n"
            "📋 Использование:\n"
            "• /set_discount <процент> - установить глобальную скидку\n"
            "• /set_discount <user_id> <процент> - установить скидку пользователю\n"
            "• /set_discount <user_id> 0 - удалить скидку пользователя\n"
            "• /discounts - показать все индивидуальные скидки\n\n"
            "Примеры:\n"
            "/set_discount 20\n"
            "/set_discount 123456789 15"
        )
        return
    
    # Проверяем, указан ли user_id
    if len(args) == 2:
        # Это глобальная скидка
        try:
            new_discount = int(args[1])
            if new_discount < 0 or new_discount > 100:
                await message.answer("❌ Скидка должна быть от 0 до 100 процентов.")
                return
            
            FIRST_PURCHASE_DISCOUNT = new_discount
            
            await message.answer(f"✅ Глобальная скидка изменена на {new_discount}%")
        except ValueError:
            await message.answer("❌ Введите корректное число.")
        return
    
    # Устанавливаем скидку конкретному пользователю
    if len(args) >= 3:
        try:
            target_user_id = int(args[1])
            new_discount = int(args[2])
            
            if new_discount < 0 or new_discount > 100:
                await message.answer("❌ Скидка должна быть от 0 до 100 процентов.")
                return
            
            if new_discount == 0:
                # Удаляем скидку пользователя
                if target_user_id in user_discounts:
                    del user_discounts[target_user_id]
                await message.answer(f"✅ Скидка для пользователя {target_user_id} удалена.")
                save_user_data()  # Сохраняем скидки
            else:
                # Устанавливаем скидку
                user_discounts[target_user_id] = new_discount
                await message.answer(f"✅ Скидка {new_discount}% установлена для пользователя {target_user_id}")
                save_user_data()  # Сохраняем скидки
                
        except ValueError:
            await message.answer("❌ Введите корректные данные. Пример: /set_discount 123456789 15")


# Команда /discounts для администратора
@dp.message(Command("discounts"))
async def cmd_discounts(message: types.Message):
    """Просмотр всех индивидуальных скидок (только для админа)"""
    user_id = message.from_user.id
    
    # Проверяем, что команду выполняет администратор
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    global user_discounts
    
    if not user_discounts:
        await message.answer("📊 Нет индивидуальных скидок.\n\n"
            f"Глобальная скидка: {FIRST_PURCHASE_DISCOUNT}%")
        return
    
    text = "📊 Список индивидуальных скидок:\n\n"
    for uid, discount in user_discounts.items():
        text += f"👤 {uid}: {discount}%\n"
    
    text += f"\n🌐 Глобальная скидка: {FIRST_PURCHASE_DISCOUNT}%"
    
    await message.answer(text)


# Команда /create_promo для создания промокода
@dp.message(Command("create_promo"))
async def cmd_create_promo(message: types.Message):
    """Создание промокода (только для админа)"""
    user_id = message.from_user.id
    
    # Проверяем, что команду выполняет администратор
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    
    # Синтаксис: /create_promo [код] [бонус_пользователю] [бонус_владельцу] [макс_использований] [id_владельца]
    if len(args) < 4:
        await message.answer(
            "🎁 Создание промокода\n\n"
            "Использование: /create_promo [код] [бонус_пользователю] [бонус_владельцу] [макс_использований] [id_владельца]\n\n"
            "Пример: /create_promo HELLO 50 10 100\n"
            "• Промокод: HELLO\n"
            "• Бонус активировавшему: 50 руб\n"
            "• Бонус владельцу промокода: 10 руб\n"
            "• Максимум использований: 100\n\n"
            "Пример с указанием владельца (ютубер/партнёр):\n"
            "/create_promo HELLO 50 10 100 123456789\n"
            "• Последний параметр - ID владельца промокода (по умолчанию - админ)"
        )
        return
    
    promo_code = args[1].upper()
    
    # Проверяем, не существует ли уже промокод
    if promo_code in promo_codes:
        await message.answer("❌ Промокод с таким названием уже существует!")
        return
    
    try:
        user_bonus = int(args[2])
        owner_bonus = int(args[3])
        max_uses = int(args[4]) if len(args) > 4 else 0  # 0 = безлимит
        
        # Определяем владельца промокода (по умолчанию - админ)
        if len(args) > 5:
            try:
                owner_id = int(args[5])
            except ValueError:
                owner_id = user_id
        else:
            owner_id = user_id  # По умолчанию владелец - админ
        
        if user_bonus <= 0 or owner_bonus < 0:
            await message.answer("❌ Бонус пользователя должен быть > 0, бонус владельца >= 0")
            return
        
        # Создаём промокод
        promo_codes[promo_code] = {
            "owner_id": owner_id,
            "user_bonus": user_bonus,
            "owner_bonus": owner_bonus,
            "uses": 0,
            "max_uses": max_uses
        }
        
        save_user_data()
        
        owner_mention = f"Владелец: {owner_id}" if owner_id != user_id else "Владелец: Вы (админ)"
        
        await message.answer(
            f"✅ Промокод создан!\n\n"
            f"🎫 Код: {promo_code}\n"
            f"💰 Бонус активировавшему: {user_bonus} руб\n"
            f"💵 Бонус владельцу: {owner_bonus} руб\n"
            f"📊 Лимит использований: {max_uses if max_uses > 0 else '∞'}\n\n"
            f"{owner_mention}\n\n"
            f"Владелец может проверить статистику: /my_promos"
        )
        
    except ValueError:
        await message.answer("❌ Введите корректные числа.")


# Команда /my_promos для просмотра своих промокодов
@dp.message(Command("my_promos"))
async def cmd_my_promos(message: types.Message):
    """Просмотр своих промокодов"""
    user_id = message.from_user.id
    
    # Ищем промокоды, где user_id является владельцем
    my_promos = {code: info for code, info in promo_codes.items() if info["owner_id"] == user_id}
    
    if not my_promos:
        await message.answer(
            "🎁 У вас пока нет промокодов.\n\n"
            "Попросите администратора создать промокод командой:\n"
            "/create_promo [код] [бонус_пользователю] [бонус_владельцу] [макс_использований]"
        )
        return
    
    text = "🎁 Ваши промокоды:\n\n"
    total_earned = 0
    
    for code, info in my_promos.items():
        earned = info["uses"] * info["owner_bonus"]
        total_earned += earned
        
        limit_text = f"{info['uses']}/{info['max_uses']}" if info['max_uses'] > 0 else f"{info['uses']}/∞"
        
        text += (
            f"🎫 {code}\n"
            f"   💰 Бонус: {info['user_bonus']} руб\n"
            f"   💵 Вы получаете: {info['owner_bonus']} руб\n"
            f"   📊 Использовано: {limit_text}\n"
            f"   💵 Заработано: {earned} руб\n\n"
        )
    
    text += f"💵 Всего заработано: {total_earned} руб"
    
    await message.answer(text)


# Команда /delete_promo для удаления промокода
@dp.message(Command("delete_promo"))
async def cmd_delete_promo(message: types.Message):
    """Удаление промокода (только для админа)"""
    user_id = message.from_user.id
    
    # Проверяем, что команду выполняет администратор
    if user_id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    args = message.text.split()
    
    # Перезагружаем данные из файла перед операцией
    load_user_data()
    print(f"[DELETE_PROMO] Текущие промокоды: {list(promo_codes.keys())}")
    
    # Синтаксис: /delete_promo [код]
    if len(args) < 2:
        # Показываем список промокодов
        if not promo_codes:
            await message.answer(
                "🎁 Нет промокодов для удаления."
            )
            return
        
        text = "🎁 Доступные промокоды:\n\n"
        for code, info in promo_codes.items():
            limit_text = f"{info['uses']}/{info['max_uses']}" if info['max_uses'] > 0 else f"{info['uses']}/∞"
            text += f"• {code} - Использовано: {limit_text}\n"
        
        text += "\n📋 Использование:\n/delete_promo [код]\n\nПример:\n/delete_promo TEST"
        
        await message.answer(text)
        return
    
    promo_code = args[1].upper()
    print(f"[DELETE_PROMO] Пытаемся удалить: {promo_code}")
    
    if promo_code not in promo_codes:
        await message.answer(
            f"❌ Промокод {promo_code} не найден!\n\n"
            f"Список промокодов: /delete_promo"
        )
        return
    
    # Удаляем промокод
    del promo_codes[promo_code]
    print(f"[DELETE_PROMO] Удалили промокод, осталось: {list(promo_codes.keys())}")
    
    # Удаляем всех пользователей, использовавших этот промокод
    users_to_remove = [u for u in promo_code_users if u.endswith(f"_{promo_code}")]
    for u in users_to_remove:
        promo_code_users.discard(u)
    
    # Сохраняем данные
    save_user_data()
    print(f"[DELETE_PROMO] Сохранено!")
    
    await message.answer(
        f"✅ Промокод {promo_code} удалён!\n\n"
        f"Удалено использований: {len(users_to_remove)}"
    )


# Обработчик сообщений
@dp.message()
async def handle_message(message: types.Message):
    """Обработчик всех сообщений"""
    text = message.text
    user_id = message.from_user.id
    
    # Проверяем, ожидаем ли ввод промокода (ПРОВЕРЯЕМ СНАЧАЛА!)
    if user_id in pending_promo_codes:
        promo_code = message.text.strip().upper()
        del pending_promo_codes[user_id]
        
        print(f"[ПРОМОКОД] Пользователь {user_id} активирует код: {promo_code}")
        print(f"[ПРОМОКОД] Доступные промокоды: {list(promo_codes.keys())}")
        
        # Проверяем промокод
        if promo_code not in promo_codes:
            await message.answer(
                "❌ Промокод не найден!\n\n"
                "Проверьте правильность ввода и попробуйте снова.",
                reply_markup=profile_keyboard()
            )
            return
        
        promo_info = promo_codes[promo_code]
        print(f"[ПРОМОКОД] Информация о промокоде: {promo_info}")
        print(f"[ПРОМОКОД] Лимит: {promo_info['max_uses']}, Использовано: {promo_info['uses']}")
        
        # Проверяем лимит использований
        if promo_info["max_uses"] > 0 and promo_info["uses"] >= promo_info["max_uses"]:
            await message.answer(
                "❌ Промокод больше не действителен!\n\n"
                "Лимит использований исчерпан.",
                reply_markup=profile_keyboard()
            )
            return
        
        # Проверяем, не является ли пользователь владельцем промокода
        user_promo_key = f"{user_id}_{promo_code}"
        if promo_info["owner_id"] == user_id and user_id != ADMIN_ID:
            await message.answer(
                "❌ Вы не можете активировать свой собственный промокод!",
                reply_markup=profile_keyboard()
            )
            return
        
        # Проверяем, не использовал ли уже пользователь промокод
        # Администратор может использовать промокод повторно для тестирования
        if user_promo_key in promo_code_users and user_id != ADMIN_ID:
            await message.answer(
                "❌ Вы уже активировали этот промокод!\n\n"
                "Промокод можно использовать только один раз.",
                reply_markup=profile_keyboard()
            )
            return
        
        # Активируем промокод - начисляем бонус активировавшему
        current_balance = user_balances.get(user_id, 0)
        user_balances[user_id] = current_balance + promo_info["user_bonus"]
        
        # Увеличиваем счётчик использований
        promo_codes[promo_code]["uses"] += 1
        
        # Добавляем пользователя в список активировавших
        promo_code_users.add(user_promo_key)
        
        # Начисляем бонус владельцу промокода
        owner_id = promo_info["owner_id"]
        if owner_id in user_balances:
            user_balances[owner_id] += promo_info["owner_bonus"]
        else:
            user_balances[owner_id] = promo_info["owner_bonus"]
        
        # Сохраняем данные
        save_user_data()
        print(f"[ПРОМОКОД] Сохранено! Баланс пользователя: {user_balances.get(user_id, 0)}")
        
        await message.answer(
            f"✅ Промокод активирован!\n\n"
            f"🎁 Ваш бонус: +{promo_info['user_bonus']} руб\n"
            f"💳 Ваш баланс: {user_balances[user_id]} руб",
            reply_markup=profile_keyboard()
        )
        return
    
    # Список всех команд бота
    all_commands = ["/start", "/help", "/cmd", "/my_promos"]
    admin_commands = ["/set_discount", "/discounts", "/create_promo", "/delete_promo"]
    
    # Проверяем, является ли сообщение командой
    if text.startswith("/"):
        command = text.split()[0]
        
        # Проверяем, существует ли команда
        if command not in all_commands and command not in admin_commands:
            await message.answer(
                "❌ Такой команды не существует.\n\n"
                "Доступные команды:\n"
                "• /start - Запустить бота\n"
                "• /help - Помощь\n"
                "• /cmd - Список команд\n"
                "• /my_promos - Мои промокоды"
            )
            return
        
        # Если команда админская, проверяем права
        if command in admin_commands and user_id != ADMIN_ID:
            await message.answer(
                "❌ Такой команды не существует.\n\n"
                "Доступные команды:\n"
                "• /start - Запустить бота\n"
                "• /help - Помощь\n"
                "• /cmd - Список команд\n"
                "• /my_promos - Мои промокоды"
            )
            return
    
    # Если пользователь нажал кнопку меню (Каталог или Помощь) - сбрасываем заказ
    if text in ["🛍️ Каталог", "❓ Помощь", "📝 Отзывы", "👤 Профиль", "🎮 Mini-app"]:
        if user_id in pending_orders:
            del pending_orders[user_id]
        if user_id in pending_promo_codes:
            del pending_promo_codes[user_id]
    
    # Обработка кнопки Mini-app
    if text == "🎮 Mini-app":
        from aiogram.types import WebAppInfo
        await message.answer(
            "🎮 Открыть магазин в Mini-app\n\n"
            "Нажмите кнопку ниже для открытия полной версии магазина:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🚀 Открыть магазин",
                    web_app=WebAppInfo(url=CASE_APP_URL)
                )]
            ])
        )
        return
    
    # Проверяем, ожидаем ли ввод почты от этого пользователя
    if user_id in pending_orders:
        # Обрабатываем ввод почты
        email = message.text.strip()
        order_info = pending_orders[user_id]
        
        # Проверяем, содержит ли почта @gmail.com
        if "@gmail.com" not in email:
            await message.answer(
                "❌ Почта введена некорректно!\n\n"
                "Пожалуйста, введите почту, содержащую @gmail.com\n"
                "Пример: example@gmail.com"
            )
            return
        
        product = order_info["product"]
        
        # Сохраняем почту в заказе
        order_info["email"] = email
        
        # Генерируем ID заказа
        global order_counter
        order_id = order_counter
        order_counter += 1
        save_user_data()  # Сохраняем счётчик заказов
        order_info["order_id"] = order_id
        
        # Проверяем первую ли это покупка у пользователя
        original_price = product['price']
        is_first_purchase = user_id not in first_time_buyers
        discount_amount = 0
        final_price = original_price
        discount_text = ""
        
        # Проверяем индивидуальную скидку для пользователя
        discount_percent = user_discounts.get(user_id, FIRST_PURCHASE_DISCOUNT) if is_first_purchase else 0
        
        if is_first_purchase and discount_percent > 0:
            # Применяем скидку
            discount_amount = int(original_price * discount_percent / 100)
            final_price = original_price - discount_amount
            
            # Определяем тип скидки для сообщения
            if user_id in user_discounts:
                discount_text = f"🎁 Ваша персональная скидка {discount_percent}%: -{discount_amount}₽\n"
            else:
                discount_text = f"🎁 Скидка {discount_percent}% на первую покупку: -{discount_amount}₽\n"
            
            order_info["discount"] = discount_amount
            order_info["discount_percent"] = discount_percent
        
        order_info["final_price"] = final_price
        order_info["is_first_purchase"] = is_first_purchase
        
        # Формируем сообщение с реквизитами
        text = (
            f"💳 Оплата\n\n"
            f"Товар: {product['name']}\n"
            f"Сумма: {original_price}₽\n"
            f"{discount_text}"
            f"💰 К оплате: {final_price}₽\n"
            f"Почта: {email}\n\n"
            f"📦 Реквизиты для перевода:\n\n"
            f"💳 Карта: {CARD_NUMBER}\n"
            f"👤 Получатель: {CARD_HOLDER}\n\n"
            "После перевода нажмите кнопку ниже для подтверждения оплаты."
        )
        
        # Отправляем сообщение с реквизитами и кнопкой
        await message.answer(text, reply_markup=payment_keyboard(order_id))
        return
    
    if text == "🛍️ Каталог":
        text_msg = "🛍️ Каталог\n\nВыберите игру:"
        await message.answer(text_msg, reply_markup=games_keyboard())
    elif text == "👤 Профиль":
        user = message.from_user
        user_full_name = user.full_name
        user_id = message.from_user.id
        
        # Получаем баланс пользователя
        balance = user_balances.get(user_id, 0)
        
        # Отладочная информация
        print(f"Профиль: user_id={user_id}, balance={balance}")
        print(f"Все балансы: {user_balances}")
        
        # Получаем историю заказов
        orders = get_user_orders(user_id)
        
        # Формируем сообщение профиля
        text_msg = (
            f"👤 Профиль\n\n"
            f"📛 Имя: {user_full_name}\n"
            f"🆔 ID: {user_id}\n\n"
            f"💰 Баланс: {balance}₽\n\n"
        )
        
        # Добавляем историю заказов
        if orders:
            order_count = len(orders)
            # Склонение слова "заказ"
            if order_count % 10 == 1 and order_count % 100 != 11:
                order_word = "заказ"
            elif 2 <= order_count % 10 <= 4 and (order_count % 100 < 10 or order_count % 100 >= 20):
                order_word = "заказа"
            else:
                order_word = "заказов"
            
            text_msg += f"📦 Всего {order_count} {order_word}\n"
        else:
            text_msg += "📦 У вас пока нет заказов"
        
        await message.answer(text_msg, reply_markup=profile_keyboard())
    elif text == "❓ Помощь":
        text_msg = """❓ Помощь

• Выберите категорию из каталога
• Нажмите на товар для покупки
• После оплаты получите товар

💬 По вопросам: @your_admin"""
        await message.answer(text_msg, reply_markup=main_menu_keyboard())
    elif text == "📝 Отзывы":
        text_msg = "📝 Отзывы\n\nОзнакомьтесь с отзывами наших довольных клиентов!"
        await message.answer(
            text_msg,
            reply_markup=main_menu_keyboard(),
            disable_web_page_preview=False
        )
        await message.answer(f"Перейти в канал отзывов: {REVIEWS_CHANNEL}")


# Обработчик данных из Web App (Mini-app)
@dp.message(types.WebAppData)
async def process_web_app_data(message: types.Message):
    """Обработка данных из мини-аппа кейса с голдой"""
    user_id = message.from_user.id
    
    try:
        web_data = message.web_app_data.data
        print(f"Raw web_app_data: {web_data}")
        
        web_data_json = json.loads(web_data)
        action = web_data_json.get('action')
        amount = web_data_json.get('amount')
        price = web_data_json.get('price', 0)
        
        print(f"Parsed: action={action}, amount={amount}, price={price}")
        
        if action == 'save_gold' and amount:
            await save_gold_to_inventory(message, user_id, int(amount))
        elif action == 'sell_gold' and amount:
            await sell_gold(message, user_id, int(amount), int(price))
    except Exception as e:
        print(f"Error processing web_app_data: {e}")
        import traceback
        traceback.print_exc()


# Обработчик callback-запросов
@dp.callback_query()
async def process_callback(callback: types.CallbackQuery):
    """Обработчик всех callback"""
    data = callback.data
    user_id = callback.from_user.id
    
    # Обработка данных из Mini-app (web_app_data)
    # Проверяем разные способы получения данных
    web_data = None
    
    # Способ 1: callback.web_app_data
    if hasattr(callback, 'web_app_data') and callback.web_app_data:
        web_data = callback.web_app_data.data
    # Способ 2: callback.message.web_app_data
    elif hasattr(callback, 'message') and callback.message:
        msg = callback.message
        if hasattr(msg, 'web_app_data') and msg.web_app_data:
            web_data = msg.web_app_data.data
    # Способ 3: callback.message.web_app
    elif hasattr(callback, 'message') and callback.message:
        msg = callback.message
        if hasattr(msg, 'web_app') and msg.web_app:
            web_data = msg.web_app.data
    
    if web_data:
        try:
            web_data_json = json.loads(web_data)
            action = web_data_json.get('action')
            amount = web_data_json.get('amount')
            price = web_data_json.get('price', 0)
            
            print(f"Received web_app_data: action={action}, amount={amount}, price={price}")
            
            if action == 'save_gold' and amount:
                await save_gold_to_inventory(callback, user_id, amount)
                return
            elif action == 'sell_gold' and amount:
                await sell_gold(callback, user_id, amount, price)
                return
        except Exception as e:
            print(f"Error processing web_app_data: {e}")
    
    # Главное меню
    if data == "back_to_main":
        await callback.message.edit_text(
            f"👋 Добро пожаловать в {SHOP_NAME}!\n\nВыберите раздел:",
            reply_markup=None
        )
        await callback.answer()
        return
    
    # Админ-меню
    if data == "admin_menu":
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        await callback.message.edit_text(
            "🔧 Админ-панель\n\nВыберите раздел:",
            reply_markup=admin_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Статистика
    if data == "admin_stats":
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        # Здесь можно добавить статистику
        text = "📊 Статистика\n\n"
        text += f"👥 Пользователей: {len(user_balances)}\n"
        text += f"📦 Заказов: {len(confirmed_orders)}\n"
        await callback.message.edit_text(text, reply_markup=admin_menu_keyboard())
        await callback.answer()
        return
    
    # Заказы
    if data == "admin_orders":
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        if not confirmed_orders:
            await callback.message.edit_text(
                "📦 Заказы\n\nЗаказов пока нет.",
                reply_markup=admin_menu_keyboard()
            )
        else:
            # Формируем список заказов для админа
            order_list = []
            for order_id, order_info in confirmed_orders.items():
                order_list.append({
                    "order_id": order_id,
                    "user_id": order_info.get("user_id", "N/A"),
                    "product": order_info.get("product", "Unknown"),
                    "status": order_info.get("status", "unknown")
                })
            await callback.message.edit_text(
                "📦 Заказы",
                reply_markup=admin_orders_keyboard(order_list)
            )
        await callback.answer()
        return
    
    # Пагинация заказов
    if data.startswith("admin_orders_page_"):
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        page = int(data.split("_")[-1])
        order_list = []
        for order_id, order_info in confirmed_orders.items():
            order_list.append({
                "order_id": order_id,
                "user_id": order_info.get("user_id", "N/A"),
                "product": order_info.get("product", "Unknown"),
                "status": order_info.get("status", "unknown")
            })
        await callback.message.edit_text(
            "📦 Заказы",
            reply_markup=admin_orders_keyboard(order_list, page)
        )
        await callback.answer()
        return
    
    # Промокоды
    if data == "admin_promos":
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        await callback.message.edit_text(
            "🎁 Управление промокодами",
            reply_markup=admin_promos_keyboard()
        )
        await callback.answer()
        return
    
    # Скидки
    if data == "admin_discounts":
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        await callback.message.edit_text(
            "💰 Управление скидками",
            reply_markup=admin_discounts_keyboard()
        )
        await callback.answer()
        return
    
    # Рассылка
    if data == "admin_broadcast":
        if user_id != ADMIN_ID:
            await callback.answer("❌ У вас нет доступа", show_alert=True)
            return
        await callback.message.edit_text(
            "📢 Рассылка\n\nВведите сообщение для рассылки:\n"
            "Для отмены нажмите /cancel",
            reply_markup=admin_menu_keyboard()
        )
        # Здесь можно добавить логику ожидания ввода сообщения
        await callback.answer()
        return
    
    # Проверка подписки
    if data == "check_subscription":
        is_subscribed = await check_subscription_status(user_id)
        
        if is_subscribed:
            # Проверяем, первый ли это раз, когда пользователь проходит верификацию
            if user_id not in verified_subscribers:
                # Добавляем пользователя в верифицированные
                verified_subscribers.add(user_id)
                save_user_data()  # Сохраняем список верифицированных подписчиков
                
                # Начисляем бонус на баланс
                current_balance = user_balances.get(user_id, 0)
                user_balances[user_id] = current_balance + SUBSCRIPTION_BONUS
                save_user_data()  # Сохраняем баланс
                
                await callback.message.edit_text(
                    f"🎉 Поздравляем! Вы успешно подписались на все каналы!\n\n"
                    f"💰 Вам начислен бонус: {SUBSCRIPTION_BONUS} рублей\n"
                    f"💳 Ваш баланс: {user_balances[user_id]} рублей\n\n"
                    f"Добро пожаловать в {SHOP_NAME}!\n\n"
                    "Выберите раздел:",
                    reply_markup=main_menu_keyboard()
                )
            else:
                # Пользователь уже получал бонус
                await callback.message.edit_text(
                    f"✅ Вы уже подписаны на все каналы!\n\n"
                    f"Добро пожаловать в {SHOP_NAME}!\n\n"
                    "Выберите раздел:",
                    reply_markup=main_menu_keyboard()
                )
        else:
            # Пользователь не подписан
            text = (
                "❌ Вы еще не подписались на все каналы!\n\n"
                "Пожалуйста, подпишитесь на все каналы и нажмите \"Проверить подписку\"\n\n"
            )
            
            for channel in REQUIRED_CHANNELS:
                text += f"• @{channel}\n"
            
            text += f"\n🎁 После подписки вы получите {SUBSCRIPTION_BONUS} рублей на баланс!"
            
            await callback.message.edit_text(
                text,
                reply_markup=subscription_keyboard(REQUIRED_CHANNELS)
            )
        
        await callback.answer()
        return
    
    # Инвентарь
    if data == "inventory":
        await show_inventory(callback, user_id)
        return
    
    # Продать все из инвентаря
    if data == "sell_all_inventory":
        await sell_all_inventory(callback, user_id)
        return
    
    # Сохранить голду в инвентарь (callback_data: save_gold_caseId_amount)
    if data.startswith("save_gold_"):
        parts = data.split("_")
        if len(parts) >= 3:
            try:
                gold_amount = int(parts[-1])  # Берем последний элемент
                await save_gold_to_inventory(callback, user_id, gold_amount)
            except ValueError:
                await callback.message.edit_text(
                    "❌ Ошибка при сохранении голды.",
                    reply_markup=profile_keyboard()
                )
                await callback.answer()
        return
    
    # Продать голду (callback_data: sell_gold_caseId_amount)
    if data.startswith("sell_gold_"):
        parts = data.split("_")
        if len(parts) >= 3:
            try:
                gold_amount = int(parts[-1])  # Берем последний элемент
                await sell_gold(callback, user_id, gold_amount)
            except ValueError:
                await callback.message.edit_text(
                    "❌ Ошибка при продаже голды.",
                    reply_markup=profile_keyboard()
                )
                await callback.answer()
        return
    
    # Вернуться в профиль
    if data == "profile":
        balance = user_balances.get(user_id, 0)
        text_msg = (
            f"👤 Ваш профиль\n\n"
            f"💳 Ваш баланс: {balance} руб"
        )
        await callback.message.edit_text(text_msg, reply_markup=profile_keyboard())
        await callback.answer()
        return
    
    # Каталог категорий
    if data == "catalog":
        text = "🛍️ Каталог\n\nВыберите игру:"
        await callback.message.edit_text(text, reply_markup=games_keyboard())
        await callback.answer()
        return
    
    # Назад к товарам подкатегории
    if data == "back_to_catalog":
        sub_cat_id = user_sub_category.get(user_id, 1)
        text = f"Товары\n\nВыберите товар:"
        await callback.message.edit_text(text, reply_markup=products_keyboard(sub_cat_id))
        await callback.answer()
        return
    
    # Назад к подкатегориям
    if data == "back_to_subcategories":
        game_id = user_game.get(user_id, 1)
        text = f"Выберите раздел:"
        await callback.message.edit_text(text, reply_markup=sub_categories_keyboard(game_id))
        await callback.answer()
        return
    
    # Назад к товарам (из карточки товара)
    if data == "back_to_products":
        sub_cat_id = user_sub_category.get(user_id, 1)
        text = f"Товары\n\nВыберите товар:"
        await callback.message.edit_text(text, reply_markup=products_keyboard(sub_cat_id))
        await callback.answer()
        return
    
    # Выбор игры
    if data.startswith("game_"):
        game_id = int(data.split("_")[1])
        user_game[user_id] = game_id
        
        game = get_games()[game_id]
        text = f"{game['name']}\n\nВыберите раздел:"
        
        await callback.message.edit_text(text, reply_markup=sub_categories_keyboard(game_id))
        await callback.answer()
        return
    
    # Выбор подкатегории
    if data.startswith("subcategory_"):
        sub_category_id = int(data.split("_")[1])
        user_sub_category[user_id] = sub_category_id
        
        sub_category = get_sub_category(sub_category_id)
        text = f"{sub_category['name']}\n\n{sub_category['description']}\n\nВыберите товар:"
        
        await callback.message.edit_text(text, reply_markup=products_keyboard(sub_category_id))
        await callback.answer()
        return
    
    # Просмотр товара
    if data.startswith("product_"):
        product_id = int(data.split("_")[1])
        product = get_product(product_id)
        
        if product:
            text = f"{product['name']}\n\n"
            text += f"{product['description']}\n\n"
            text += f"Цена: {product['price']}₽"
            
            # Проверяем, является ли товар кейсом с голдой
            is_gold_case = product_id == 28
            
            if is_gold_case:
                # Проверяем, есть ли кейсы в инвентаре
                has_cases = False
                if user_id in user_inventory:
                    case_items = [item for item in user_inventory[user_id] 
                                 if item.get("type") == "case" and item.get("case_id") == product_id]
                    has_cases = len(case_items) > 0
                
                await callback.message.edit_text(
                    text, 
                    reply_markup=case_keyboard(product_id, product['price'], has_cases)
                )
            else:
                await callback.message.edit_text(
                    text, 
                    reply_markup=product_keyboard(product_id, product['price'])
                )
        
        await callback.answer()
        return
    
    # Открыть кейс из инвентаря
    if data.startswith("open_inv_case_"):
        case_id = int(data.split("_")[-1])
        product = get_product(case_id)
        
        if product:
            # Проверяем, есть ли кейс в инвентаре
            if user_id in user_inventory:
                case_items = [item for item in user_inventory[user_id] 
                             if item.get("type") == "case" and item.get("case_id") == case_id]
                
                if case_items:
                    # Удаляем один кейс из инвентаря
                    for i, item in enumerate(user_inventory[user_id]):
                        if item.get("type") == "case" and item.get("case_id") == case_id:
                            user_inventory[user_id].pop(i)
                            break
                    
                    save_user_data()
                    
                    # Открываем кейс
                    await open_case(callback, user_id, case_id, product)
                    await callback.answer()
                    return
                else:
                    await callback.message.edit_text(
                        "❌ У вас нет этого кейса!",
                        reply_markup=profile_keyboard()
                    )
                    await callback.answer()
                    return
            else:
                await callback.message.edit_text(
                    "❌ У вас нет кейсов!",
                    reply_markup=profile_keyboard()
                )
                await callback.answer()
                return
        return
    
    # Покупка товара - запрос почты
    if data.startswith("buy_"):
        product_id = int(data.split("_")[1])
        product = get_product(product_id)
        
        if product:
            # Проверяем, является ли это кейсом с голдой
            is_gold_case = product_id == 28
            
            if is_gold_case:
                # Проверяем баланс
                balance = user_balances.get(user_id, 0)
                case_price = product["price"]
                
                if balance < case_price:
                    await callback.message.edit_text(
                        f"❌ Недостаточно средств!\n\n"
                        f"💰 Ваш баланс: {balance}₽\n"
                        f"💳 Цена кейса: {case_price}₽\n\n"
                        f"Пополните баланс для покупки кейса.",
                        reply_markup=profile_keyboard()
                    )
                    await callback.answer()
                    return
                
                # Списываем баланс
                user_balances[user_id] = balance - case_price
                
                # Добавляем кейс в инвентарь
                if user_id not in user_inventory:
                    user_inventory[user_id] = []
                user_inventory[user_id].append({
                    "type": "case",
                    "case_id": product_id,
                    "name": product["name"],
                    "price": case_price
                })
                
                save_user_data()
                
                # Открываем кейс
                await open_case(callback, user_id, product_id, product, from_purchase=True)
                await callback.answer()
                return
            
            # Обычная покупка - сохраняем информацию о заказе
            pending_orders[user_id] = {
                "product_id": product_id,
                "product": product
            }
            
            # Запрашиваем почту
            text = f"💳 Оплата\n\n"
            text += f"Товар: {product['name']}\n"
            text += f"Сумма: {product['price']}₽\n\n"
            text += "📧 Введите почту вашего Supercell ID:"
            
            # Удаляем сообщение с кнопкой и отправляем новое сообщение без клавиатуры
            await callback.message.delete()
            await bot.send_message(user_id, text)
            await callback.answer()
        
        return


async def open_case(callback, user_id: int, case_id: int, case_product: dict, from_purchase: bool = False):
    """Открытие кейса - открывает Mini-app"""
    from aiogram.types import WebAppInfo
    
    case_price = case_product["price"]
    case_name = case_product["name"]
    
    # Если это не покупка, проверяем баланс
    if not from_purchase:
        balance = user_balances.get(user_id, 0)
        if balance < case_price:
            await callback.message.edit_text(
                f"❌ Недостаточно средств!\n\n"
                f"💰 Ваш баланс: {balance}₽\n"
                f"💳 Цена кейса: {case_price}₽\n\n"
                f"Пополните баланс для открытия кейса.",
                reply_markup=profile_keyboard()
            )
            return
    
    # Удаляем кейс из инвентаря (если он там есть)
    if user_id in user_inventory:
        case_items = [item for item in user_inventory[user_id] 
                     if item.get("type") == "case" and item.get("case_id") == case_id]
        if case_items:
            for i, item in enumerate(user_inventory[user_id]):
                if item.get("type") == "case" and item.get("case_id") == case_id:
                    user_inventory[user_id].pop(i)
                    break
            save_user_data()
    
    # Открываем Mini-app
    await callback.message.edit_text(
        f"🎁 {case_name}\n\n"
        f"Открытие кейса...",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🎰 Открыть кейс",
                web_app=WebAppInfo(url=f"{CASE_APP_URL}?case_id={case_id}&price={case_price}")
            )]
        ])
    )
    await callback.answer()


async def open_gold_case(callback, user_id: int, case_id: int, case_product: dict, remove_case: bool = False):
    """Открытие кейса с голдой - показывает результат напрямую"""
    import random
    from keyboards import InlineKeyboardButton, InlineKeyboardMarkup
    global user_inventory
    
    case_price = case_product["price"]
    case_name = case_product["name"]
    
    # Если нужно удалить кейс из инвентаря
    if remove_case and user_id in user_inventory:
        case_items = [item for item in user_inventory[user_id] 
                     if item.get("type") == "case" and item.get("case_id") == case_id]
        if case_items:
            for i, item in enumerate(user_inventory[user_id]):
                if item.get("type") == "case" and item.get("case_id") == case_id:
                    user_inventory[user_id].pop(i)
                    break
            save_user_data()
    
    # Вычисляем результат
    rewards = get_gold_rewards()
    roll = random.random() * 10000
    cumulative = 0
    selected_reward = None
    
    sorted_rewards = sorted(rewards.items(), key=lambda x: x[1]["chance"])
    for _, reward in sorted_rewards:
        cumulative += reward["chance"] * 100
        if roll <= cumulative:
            selected_reward = reward
            break
    
    if not selected_reward:
        selected_reward = sorted_rewards[0][1]
    
    gold_amount = selected_reward["amount"]
    gold_price = get_gold_sell_price(gold_amount)
    
    # Показываем результат с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📦 Отложить",
                callback_data=f"save_gold_{case_id}_{gold_amount}"
            ),
            InlineKeyboardButton(
                text="💵 Продать",
                callback_data=f"sell_gold_{case_id}_{gold_amount}"
            )
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_products")]
    ])
    
    # Эмодзи для редкости
    if gold_amount >= 1000:
        emoji = "🟡"
    elif gold_amount >= 100:
        emoji = "⚪"
    else:
        emoji = "🟤"
    
    await callback.message.edit_text(
        f"🎁 Кейс открыт!\n\n"
        f"📦 Кейс: {case_name}\n"
        f"💰 Потрачено: {case_price}₽\n\n"
        f"{emoji} ВЫПАЛО: {gold_amount} голды\n"
        f"💵 Цена продажи: {gold_price}₽",
        reply_markup=keyboard
    )


async def save_gold_to_inventory(obj, user_id: int, gold_amount: int):
    """Сохранение голды в инвентарь"""
    global user_inventory
    
    # Инициализируем инвентарь пользователя, если его нет
    if user_id not in user_inventory:
        user_inventory[user_id] = []
    
    # Добавляем голду в инвентарь
    user_inventory[user_id].append({
        "type": "gold",
        "amount": gold_amount
    })
    
    save_user_data()
    
    message_to_send = f"✅ Голда ({gold_amount}) добавлена в инвентарь!\n\nВы можете найти её в разделе \"🎒 Инвентарь\" в профиле."
    
    if hasattr(obj, 'message') and hasattr(obj, 'answer'):
        try:
            await obj.message.edit_text(message_to_send, reply_markup=gold_case_result_keyboard(28, gold_amount))
        except:
            pass
        await obj.answer()
    else:
        try:
            await obj.answer(message_to_send)
        except:
            try:
                await bot.send_message(user_id, message_to_send)
            except Exception as e:
                print(f"Error sending save message: {e}")


async def sell_gold(obj, user_id: int, gold_amount: int, price: int = None):
    """Продажа голды за рубли"""
    global user_balances
    
    # Получаем цену продажи
    if price is None:
        sell_price = get_gold_sell_price(gold_amount)
    else:
        sell_price = price
    
    if sell_price == 0:
        # Просто закрываем мини-апп
        return
    
    # Добавляем деньги на баланс
    balance = user_balances.get(user_id, 0)
    user_balances[user_id] = balance + sell_price
    save_user_data()
    
    # Отправляем сообщение пользователю
    message_text = f"✅ Голда успешно продана!\n\n💎 Продано: {gold_amount} голды\n💰 Получено: {sell_price}₽\n💵 Ваш баланс: {user_balances[user_id]}₽"
    
    if hasattr(obj, 'message') and hasattr(obj, 'answer'):
        try:
            await obj.message.edit_text(message_text, reply_markup=profile_keyboard())
        except:
            pass
        await obj.answer()
    else:
        # Это Message от WebApp
        try:
            await obj.answer(message_text)
        except:
            try:
                await bot.send_message(user_id, message_text)
            except Exception as e:
                print(f"Error sending sell message: {e}")


async def show_inventory(callback, user_id: int):
    """Показать инвентарь пользователя"""
    global user_inventory
    
    # Проверяем, есть ли инвентарь у пользователя
    if user_id not in user_inventory or not user_inventory[user_id]:
        try:
            await callback.message.edit_text(
                "🎒 Ваш инвентарь пуст!\n\n"
                "Купите кейс в магазине, чтобы открыть его и получить награды.",
                reply_markup=profile_keyboard()
            )
        except:
            pass
        await callback.answer()
        return
    
    inventory = user_inventory[user_id]
    
    # Группируем предметы по типу
    gold_items = [item for item in inventory if item.get("type") == "gold"]
    case_items = [item for item in inventory if item.get("type") == "case"]
    
    # Формируем текст
    text = "🎒 Ваш инвентарь:\n\n"
    
    if case_items:
        text += "📦 Кейсы:\n"
        # Группируем кейсы по названию
        case_counts = {}
        for item in case_items:
            name = item.get("name", "Кейс")
            if name not in case_counts:
                case_counts[name] = 0
            case_counts[name] += 1
        
        for name, count in case_counts.items():
            text += f"  • {name} x{count}\n"
        text += "\n"
    
    if gold_items:
        text += "💎 Голда:\n"
        # Группируем по количеству
        gold_counts = {}
        for item in gold_items:
            amount = item.get("amount", 0)
            if amount not in gold_counts:
                gold_counts[amount] = 0
            gold_counts[amount] += 1
        
        for amount, count in sorted(gold_counts.items(), reverse=True):
            sell_price = get_gold_sell_price(amount)
            text += f"  • {amount} голды x{count} (продать за {sell_price}₽)\n"
        text += "\n"
    
    text += f"📊 Всего предметов: {len(inventory)}"
    
    await callback.message.edit_text(
        text,
        reply_markup=inventory_keyboard()
    )
    await callback.answer()


async def show_my_cases(callback, user_id: int):
    """Показать купленные кейсы пользователя"""
    global user_inventory
    
    # Проверяем кейсы в инвентаре
    if user_id not in user_inventory or not user_inventory[user_id]:
        await callback.message.edit_text(
            "📦 У вас нет кейсов!\n\n"
            "Купите кейс в магазине.",
            reply_markup=profile_keyboard()
        )
        await callback.answer()
        return
    
    inventory = user_inventory[user_id]
    case_items = [item for item in inventory if item.get("type") == "case"]
    
    if not case_items:
        await callback.message.edit_text(
            "📦 У вас нет кейсов!\n\n"
            "Купите кейс в магазине.",
            reply_markup=profile_keyboard()
        )
        await callback.answer()
        return
    
    # Группируем кейсы
    case_counts = {}
    for item in case_items:
        name = item.get("name", "Кейс")
        case_id = item.get("case_id", 0)
        key = f"{name}_{case_id}"
        if key not in case_counts:
            case_counts[key] = {"name": name, "case_id": case_id, "count": 0}
        case_counts[key]["count"] += 1
    
    text = "📦 Ваши кейсы:\n\n"
    
    for key, data in case_counts.items():
        text += f"• {data['name']} x{data['count']}\n"
    
    text += "\nНажмите на кейс, чтобы открыть его!"
    
    # Создаём клавиатуру с кейсами
    from keyboards import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard_buttons = []
    for key, data in case_counts.items():
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📦 {data['name']} ({data['count']} шт.)",
                callback_data=f"open_case_{data['case_id']}"
            )
        ])
    
    keyboard_buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="profile")
    ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()


async def sell_all_inventory(callback, user_id: int):
    """Продать все предметы из инвентаря"""
    global user_inventory, user_balances
    
    # Проверяем, есть ли инвентарь у пользователя
    if user_id not in user_inventory or not user_inventory[user_id]:
        await callback.message.edit_text(
            "❌ Ваш инвентарь пуст!\n\n"
            "Нечего продавать.",
            reply_markup=profile_keyboard()
        )
        await callback.answer()
        return
    
    inventory = user_inventory[user_id]
    total_earnings = 0
    items_sold = 0
    
    # Продаем все предметы
    for item in inventory:
        if item.get("type") == "gold":
            amount = item.get("amount", 0)
            sell_price = get_gold_sell_price(amount)
            if sell_price > 0:
                total_earnings += sell_price
                items_sold += 1
    
    if total_earnings == 0:
        await callback.message.edit_text(
            "❌ Не удалось продать предметы!\n\n"
            "В инвентаре нет предметов для продажи.",
            reply_markup=profile_keyboard()
        )
        await callback.answer()
        return
    
    # Очищаем инвентарь
    user_inventory[user_id] = []
    
    # Добавляем деньги на баланс
    balance = user_balances.get(user_id, 0)
    user_balances[user_id] = balance + total_earnings
    
    save_user_data()
    
    await callback.message.edit_text(
        f"✅ Все предметы проданы!\n\n"
        f"💎 Продано предметов: {items_sold}\n"
        f"💰 Получено: {total_earnings}₽\n"
        f"💵 Ваш баланс: {user_balances[user_id]}₽",
        reply_markup=profile_keyboard()
    )
    await callback.answer()
    
    # Подтверждение оплаты
    if data.startswith("confirm_payment_"):
        order_id = int(data.split("_")[2])
        
        # Проверяем, не подтверждал ли уже пользователь этот заказ
        if order_id in confirmed_orders:
            try:
                await callback.message.edit_text(
                    "Вы уже подтвердили оплату, ожидайте код.",
                    reply_markup=main_menu_keyboard()
                )
            except:
                await callback.message.answer(
                    "Вы уже подтвердили оплату, ожидайте код.",
                    reply_markup=main_menu_keyboard()
                )
            await callback.answer()
            return
        
        # Ищем заказ пользователя
        order_info = None
        for uid, order in pending_orders.items():
            if order.get("order_id") == order_id:
                order_info = order
                user_id = uid
                break
        
        if order_info:
            # Увеличиваем счётчик попыток
            if order_id not in payment_attempts:
                payment_attempts[order_id] = 0
            payment_attempts[order_id] += 1
            
            # Если это первая покупка - добавляем пользователя в список
            is_first_purchase = order_info.get("is_first_purchase", False)
            if is_first_purchase and user_id in pending_orders:
                # Проверяем, что пользователь ещё не в списке
                order_for_check = pending_orders.get(user_id, {})
                if order_for_check.get("is_first_purchase", False):
                    first_time_buyers.add(user_id)
                    save_user_data()  # Сохраняем список первых покупателей
            
            # Если первая попытка - показываем сообщение о неудаче с кнопкой повтора
            if payment_attempts[order_id] == 1:
                text = "❌ Оплата не прошла. Пожалуйста, проверьте правильность введённых данных и попробуйте снова."
                await callback.message.edit_text(text, reply_markup=payment_failed_keyboard(order_id))
                await callback.answer()
                return
            
            # Если вторая попытка - показываем сообщение с контактами администратора
            product = order_info["product"]
            email = order_info.get("email", "")
            final_price = order_info.get("final_price", product['price'])
            
            text = (
                "❌ Оплата не прошла.\n\n"
                "Пожалуйста, свяжитесь с администратором для решения проблемы.\n\n"
                "📞 Контакты для связи: @your_admin\n"
                f"📧 Ваша почта: {email}\n"
                f"💰 Сумма: {final_price}₽"
            )
            
            await callback.message.edit_text(text, reply_markup=payment_failed_final_keyboard())
            await callback.answer()
            return
        else:
            await callback.message.edit_text(
                "❌ Заказ не найден. Пожалуйста, оформите заказ заново.",
                reply_markup=main_menu_keyboard()
            )
        
        await callback.answer()
        return
    
    # Повторная попытка оплаты
    if data.startswith("retry_payment_"):
        order_id = int(data.split("_")[2])
        
        # Увеличиваем счётчик попыток
        if order_id not in payment_attempts:
            payment_attempts[order_id] = 0
        payment_attempts[order_id] += 1
        
        # Если вторая попытка (первая была при нажатии "Подтвердить оплату")
        if payment_attempts[order_id] >= 2:
            # Ищем заказ для получения информации
            order_info = None
            for uid, order in pending_orders.items():
                if order.get("order_id") == order_id:
                    order_info = order
                    break
            
            if order_info:
                product = order_info["product"]
                email = order_info.get("email", "")
                
                text = (
                    "❌ Оплата не прошла.\n\n"
                    "Пожалуйста, свяжитесь с администратором для решения проблемы.\n\n"
                    "📞 Контакты для связи: @your_admin\n"
                    f"📧 Ваша почта: {email}\n"
                    f"💰 Сумма: {product['price']}₽"
                )
                
                await callback.message.edit_text(text, reply_markup=payment_failed_final_keyboard())
            else:
                await callback.message.edit_text(
                    "❌ Заказ не найден. Пожалуйста, оформите заказ заново.",
                    reply_markup=main_menu_keyboard()
                )
        else:
            # Первая попытка повтора - показываем снова сообщение о неудаче
            text = "❌ Оплата не прошла. Пожалуйста, проверьте правильность введённых данных и попробуйте снова."
            await callback.message.edit_text(text, reply_markup=payment_failed_keyboard(order_id))
        
        await callback.answer()
        return
    

async def main():
    """Запуск бота и веб-сервера"""
    print("Bot started!")
    
    # Запускаем Flask сервер в фоновом режиме
    import threading
    
    # Запускаем Flask сервер в отдельном потоке
    def run_flask():
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask API server started on port 5000")
    
    if MODE == "webhook":
        # Режим webhook - не используем polling
        print(f"Webhook mode enabled. URL: {WEBHOOK_URL}")
        print("Use /setwebhook command to configure webhook with Telegram")
        # Просто ожидаем, webhook будет обрабатываться через Flask
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
    else:
        # Режим polling (по умолчанию)
        print("Polling mode enabled")
        await dp.start_polling(bot)


# ============== Webhook Endpoint ==============

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Обработка webhook запросов от Telegram"""
    if request.headers.get('secret') != WEBHOOK_SECRET:
        return jsonify({'error': 'Unauthorized'}), 401
    
    update = types.Update(**request.json)
    await dp.feed_update(bot, update)
    return jsonify({'success': True})


# ============== Команда для установки webhook ==============

async def set_webhook_command(message: types.Message):
    """Команда для установки webhook"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    if not WEBHOOK_URL:
        await message.answer("❌ WEBHOOK_URL не настроен в .env файле!")
        return
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    
    try:
        await bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET
        )
        await message.answer(
            f"✅ Webhook установлен!\n\nURL: {webhook_url}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


async def delete_webhook_command(message: types.Message):
    """Команда для удаления webhook"""
    user_id = message.from_user.id
    
    if user_id != ADMIN_ID:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return
    
    try:
        await bot.delete_webhook()
        await message.answer("✅ Webhook удалён!")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


# ============== API Эндпоинты для Mini-App ==============

@app.route('/api/check_admin', methods=['POST'])
def check_admin():
    """Проверка админ-прав"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id == ADMIN_ID:
        return jsonify({'success': True, 'is_admin': True})
    return jsonify({'success': True, 'is_admin': False})

@app.route('/api/get_balance', methods=['POST'])
def get_balance():
    """Получение баланса пользователя"""
    data = request.json
    user_id = data.get('user_id')
    
    balance = user_balances.get(user_id, 0)
    return jsonify({'success': True, 'balance': balance})

@app.route('/api/create_promo', methods=['POST'])
def create_promo():
    """Создание промокода"""
    data = request.json
    user_id = data.get('user_id')
    
    # Проверка админ-прав
    if user_id != ADMIN_ID:
        return jsonify({'success': False, 'error': 'Нет доступа'})
    
    code = data.get('code')
    user_bonus = data.get('user_bonus', 0)
    owner_bonus = data.get('owner_bonus', 0)
    max_uses = data.get('max_uses', 0)
    owner_id = data.get('owner_id', 0)
    
    if not code:
        return jsonify({'success': False, 'error': 'Не указан код промокода'})
    
    if code in promo_codes:
        return jsonify({'success': False, 'error': 'Промокод уже существует'})
    
    promo_codes[code] = {
        'owner_id': owner_id,
        'user_bonus': user_bonus,
        'owner_bonus': owner_bonus,
        'uses': 0,
        'max_uses': max_uses
    }
    
    save_user_data()
    return jsonify({'success': True, 'message': f'Промокод {code} создан'})

@app.route('/api/change_balance', methods=['POST'])
def change_balance():
    """Изменение баланса пользователя"""
    data = request.json
    user_id = data.get('user_id')
    admin_id = data.get('admin_id')
    
    # Проверка админ-прав
    if admin_id != ADMIN_ID:
        return jsonify({'success': False, 'error': 'Нет доступа'})
    
    target_user = data.get('target_user_id')
    amount = data.get('amount', 0)
    
    if not target_user:
        return jsonify({'success': False, 'error': 'Не указан пользователь'})
    
    current_balance = user_balances.get(target_user, 0)
    new_balance = current_balance + amount
    user_balances[target_user] = new_balance
    
    save_user_data()
    
    return jsonify({
        'success': True, 
        'message': f'Баланс изменён. Новый баланс: {new_balance}₽'
    })

@app.route('/api/add_inventory', methods=['POST'])
def add_inventory():
    """Добавление предмета в инвентарь"""
    data = request.json
    user_id = data.get('user_id')
    admin_id = data.get('admin_id')
    
    # Проверка админ-прав
    if admin_id != ADMIN_ID:
        return jsonify({'success': False, 'error': 'Нет доступа'})
    
    target_user = data.get('target_user_id')
    item_type = data.get('item_type', 'gold')
    amount = data.get('amount', 0)
    
    if not target_user or amount <= 0:
        return jsonify({'success': False, 'error': 'Неверные данные'})
    
    # Добавляем в инвентарь
    if target_user not in user_inventory:
        user_inventory[target_user] = []
    
    item = {
        'type': item_type,
        'amount': amount,
        'timestamp': asyncio.get_event_loop().time()
    }
    user_inventory[target_user].append(item)
    
    save_user_data()
    
    return jsonify({
        'success': True, 
        'message': f'Предмет добавлен в инвентарь пользователя {target_user}'
    })

@app.route('/api/get_stats', methods=['POST'])
def get_stats():
    """Получение статистики"""
    data = request.json
    user_id = data.get('user_id')
    
    # Проверка админ-прав
    if user_id != ADMIN_ID:
        return jsonify({'success': False, 'error': 'Нет доступа'})
    
    total_users = len(user_balances)
    active_promos = len([p for p in promo_codes.values() if p['max_uses'] == 0 or p['uses'] < p['max_uses']])
    total_activations = sum(p['uses'] for p in promo_codes.values())
    
    return jsonify({
        'success': True,
        'stats': {
            'total_users': total_users,
            'active_promos': active_promos,
            'total_activations': total_activations,
            'total_orders': len(confirmed_orders),
            'total_balance': sum(user_balances.values())
        }
    })

@app.route('/api/get_orders', methods=['POST'])
def get_orders():
    """Получение списка заказов"""
    data = request.json
    user_id = data.get('user_id')
    
    # Проверка админ-прав
    if user_id != ADMIN_ID:
        return jsonify({'success': False, 'error': 'Нет доступа'})
    
    # Возвращаем последние 50 заказов
    orders_list = list(confirmed_orders.values())[-50:]
    
    return jsonify({
        'success': True,
        'orders': orders_list
    })


if __name__ == "__main__":
    asyncio.run(main())
