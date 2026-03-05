"""Клавиатуры бота"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from products import get_games, get_sub_categories_by_game, get_products_by_sub_category


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍️ Каталог")],[KeyboardButton(text="👤 Профиль")],
            [KeyboardButton(text="🎮 Mini-app")],
            [KeyboardButton(text="❓ Помощь"), KeyboardButton(text="📝 Отзывы")]
        ],
        resize_keyboard=True
    )
    return keyboard


def games_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора игры"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    games = get_games()
    
    for game_id, game in games.items():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{game['icon']} {game['name']}",
                callback_data=f"game_{game_id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="back_to_main")
    ])
    return keyboard


def sub_categories_keyboard(game_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подкатегорий игры"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    sub_categories = get_sub_categories_by_game(game_id)
    
    for sub_id, sub_cat in sub_categories.items():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=sub_cat["name"],
                callback_data=f"subcategory_{sub_id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 К играм", callback_data="catalog")
    ])
    return keyboard


def products_keyboard(sub_category_id: int) -> InlineKeyboardMarkup:
    """Клавиатура товаров подкатегории"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    products = get_products_by_sub_category(sub_category_id)
    
    for product_id, product in products.items():
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{product['name']} - {product['price']}₽",
                callback_data=f"product_{product_id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_subcategories")
    ])
    return keyboard


def product_keyboard(product_id: int, price: int) -> InlineKeyboardMarkup:
    """Клавиатура товара с кнопкой покупки"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💳 Купить за {price}₽",
            callback_data=f"buy_{product_id}"
        )],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_products")]
    ])
    return keyboard


def case_keyboard(product_id: int, price: int, has_cases: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура кейса с кнопками купить и открыть"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💳 Купить за {price}₽",
            callback_data=f"buy_{product_id}"
        )]
    ])
    
    if has_cases:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="🎁 Открыть кейс",
                callback_data=f"open_inv_case_{product_id}"
            )
        ])
    
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_products")
    ])
    
    return keyboard


def payment_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура с реквизитами и кнопкой подтверждения оплаты"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="✅ Подтвердить оплату",
            callback_data=f"confirm_payment_{order_id}"
        )]
    ])
    return keyboard


def payment_failed_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура при неудачной оплате с кнопкой попробовать снова"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔄 Попробовать снова",
            callback_data=f"retry_payment_{order_id}"
        )]
    ])
    return keyboard


def payment_failed_final_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура при финальной неудаче с контактами администратора"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📞 Связаться с администратором",
            url="https://t.me/your_admin"
        )],
        [InlineKeyboardButton(
            text="🔙 Главное меню",
            callback_data="back_to_main"
        )]
    ])
    return keyboard


def profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура профиля"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎒 Инвентарь",
                callback_data="inventory"
            )
        ],
        [
            InlineKeyboardButton(
                text="Главное меню",
                callback_data="back_to_main"
            )
        ]
    ])
    return keyboard


def subscription_keyboard(channels: list) -> InlineKeyboardMarkup:
    """Клавиатура проверки подписки с кнопками на каналы"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Добавляем кнопки для каждого канала
    for channel in channels:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"📢 Подписаться на {channel}",
                url=f"https://t.me/{channel}"
            )
        ])
    
    # Кнопка проверки подписки
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="✅ Проверить подписку",
            callback_data="check_subscription"
        )
    ])
    
    return keyboard


def inventory_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура инвентаря с кнопкой продать всё"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💰 Продать всё",
                callback_data="sell_all_inventory"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 В профиль",
                callback_data="profile"
            )
        ]
    ])
    return keyboard


def gold_case_result_keyboard(case_id: int, gold_amount: int) -> InlineKeyboardMarkup:
    """Клавиатура результата открытия кейса с голдой"""
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
            InlineKeyboardButton(
                text="🎁 Открыть ещё",
                callback_data=f"buy_{case_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_products"
            )
        ]
    ])
    return keyboard


def admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Админ-меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📦 Заказы", callback_data="admin_orders")],
        [InlineKeyboardButton(text="🎁 Промокоды", callback_data="admin_promos")],
        [InlineKeyboardButton(text="💰 Скидки", callback_data="admin_discounts")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
    ])
    return keyboard


def admin_orders_keyboard(orders: list, page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура заказов для админа с пагинацией"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Показываем до 5 заказов на странице
    per_page = 5
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_orders = orders[start_idx:end_idx]
    
    for order in page_orders:
        order_id = order.get("order_id", "N/A")
        user_id = order.get("user_id", "N/A")
        product = order.get("product", "Unknown")
        status = order.get("status", "unknown")
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"#{order_id} - {product} ({status})",
                callback_data=f"admin_order_{order_id}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀ Назад", callback_data=f"admin_orders_page_{page-1}"))
    if end_idx < len(orders):
        nav_buttons.append(InlineKeyboardButton(text="Далее ▶", callback_data=f"admin_orders_page_{page+1}"))
    
    if nav_buttons:
        keyboard.inline_keyboard.append(nav_buttons)
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="🔙 Админ-меню", callback_data="admin_menu")])
    return keyboard


def admin_promos_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления промокодами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Создать промокод", callback_data="admin_create_promo")],
        [InlineKeyboardButton(text="🗑️ Удалить промокод", callback_data="admin_delete_promo")],
        [InlineKeyboardButton(text="📋 Список промокодов", callback_data="admin_list_promos")],
        [InlineKeyboardButton(text="🔙 Админ-меню", callback_data="admin_menu")]
    ])
    return keyboard


def admin_discounts_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура управления скидками"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Установить скидку", callback_data="admin_set_discount")],
        [InlineKeyboardButton(text="📋 Все скидки", callback_data="admin_list_discounts")],
        [InlineKeyboardButton(text="🔙 Админ-меню", callback_data="admin_menu")]
    ])
    return keyboard
