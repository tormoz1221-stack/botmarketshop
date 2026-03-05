"""Категории и товары"""

# Игры
GAMES = {
    1: {
        "name": "Brawl Stars",
        "icon": "⭐"
    },
    2: {
        "name": "Clash Royale",
        "icon": "👑"
    },
    3: {
        "name": "Clash of Clans",
        "icon": "🏰"
    },
    4: {
        "name": "Stand Off 2",
        "icon": "🔫"
    }
}

# Подкатегории (подразделы внутри игр)
SUB_CATEGORIES = {
    # Brawl Stars
    1: {
        "name": "💰 Боевой пропуск",
        "description": "Brawl Pass",
        "game_id": 1
    },
    2: {
        "name": "💎 Гемы",
        "description": "Покупка гемов",
        "game_id": 1
    },
    3: {
        "name": "🎯 Бустеры",
        "description": "Бустеры и усилители",
        "game_id": 1
    },
    # Clash Royale
    4: {
        "name": "💰 Боевой пропуск",
        "description": "Pass Royale",
        "game_id": 2
    },
    5: {
        "name": "💎 Гемы",
        "description": "Покупка гемов",
        "game_id": 2
    },
    6: {
        "name": "🏆 Сундуки",
        "description": "Сундуки и награды",
        "game_id": 2
    },
    # Clash of Clans
    7: {
        "name": "💰 Боевой пропуск",
        "description": "Gold Pass",
        "game_id": 3
    },
    8: {
        "name": "💎 Гемы",
        "description": "Покупка гемов",
        "game_id": 3
    },
    9: {
        "name": "🛡️ Ресурсы",
        "description": "Золото, эликсир и темный эликсир",
        "game_id": 3
    },
    # Stand Off 2
    10: {
        "name": "📦 Кейсы",
        "description": "Кейсы с оружием и скинами",
        "game_id": 4
    }
}

# Товары: {id: {name, description, price, sub_category_id, file_id}}
PRODUCTS = {
    # Brawl Stars - Боевой пропуск (sub_category_id: 1)
    1: {
        "name": "Brawl Pass",
        "description": "Brawl Pass - это пропуск в Brawl Stars, который открывает эксклюзивные награды, включая один эксклюзивный скин, пины, иконки и спреи, а также дополнительные стандартные награды, такие как монеты, очки силы, гемы, кредиты, блинги и новые бойцы. Обратите внимание данный товар рандом - шанс на получение Brawl Pass 50%.",
        "price": 199,
        "sub_category_id": 1,
        "file_id": None
    },
    2: {
        "name": "Brawl Pass Plus",
        "description": "Brawl Pass Plus - это пропуск в Brawl Stars, который открывает эксклюзивные награды, включая две дополнительные цветовые вариации эксклюзивного скина, один титул, 20-процентное увеличение прогрессии и дополнительные стандартные награды, такие как монеты, очки силы, гемы, кредиты и блинги. Приобретая Brawl Pass Plus, игроки получают все преимущества стандартного Brawl Pass. Обратите внимание данный товар рандом - шанс на получение Brawl Pass 50%.",
        "price": 299,
        "sub_category_id": 1,
        "file_id": None
    },
    3: {
        "name": "Pro Pass",
        "description": "Pro Pass - это пропуск в Brawl Stars, который предлагает игрокам расширенную систему наград и прогрессии по сравнению с Brawl Pass. Pro Pass дает доступ к эксклюзивным косметическим предметам и другим преимуществам, таким как ускоренное продвижение и дополнительные бонусы. Игроки могут зарабатывать очки Pro Pass, участвуя в различных игровых активностях, включая ранговые матчи. Обратите внимание данный товар рандом - шанс на получение Brawl Pass 50%.",
        "price": 499,
        "sub_category_id": 1,
        "file_id": None
    },
    # Brawl Stars - Гемы (sub_category_id: 2)
    4: {
        "name": "80 Гемов",
        "description": "80 Gems",
        "price": 99,
        "sub_category_id": 2,
        "file_id": None
    },
    5: {
        "name": "500 Гемов",
        "description": "500 Gems",
        "price": 449,
        "sub_category_id": 2,
        "file_id": None
    },
    6: {
        "name": "2800 Гемов",
        "description": "2800 Gems",
        "price": 1799,
        "sub_category_id": 2,
        "file_id": None
    },
    # Brawl Stars - Бустеры (sub_category_id: 3)
    7: {
        "name": "Бустер x1",
        "description": "1 Power Pincher",
        "price": 49,
        "sub_category_id": 3,
        "file_id": None
    },
    8: {
        "name": "Бустеры x10",
        "description": "10 Power Pinchers",
        "price": 399,
        "sub_category_id": 3,
        "file_id": None
    },
    # Clash Royale - Боевой пропуск (sub_category_id: 4)
    9: {
        "name": "Pass Royale",
        "description": "Месячный боевой пропуск",
        "price": 349,
        "sub_category_id": 4,
        "file_id": None
    },
    10: {
        "name": "Pass Royale Premium",
        "description": "Premium боевой пропуск",
        "price": 549,
        "sub_category_id": 4,
        "file_id": None
    },
    # Clash Royale - Гемы (sub_category_id: 5)
    11: {
        "name": "80 Гемов",
        "description": "80 Gems",
        "price": 99,
        "sub_category_id": 5,
        "file_id": None
    },
    12: {
        "name": "500 Гемов",
        "description": "500 Gems",
        "price": 449,
        "sub_category_id": 5,
        "file_id": None
    },
    13: {
        "name": "2500 Гемов",
        "description": "2500 Gems",
        "price": 1799,
        "sub_category_id": 5,
        "file_id": None
    },
    # Clash Royale - Сундуки (sub_category_id: 6)
    14: {
        "name": "Сундук легенды",
        "description": "Legendary Chest",
        "price": 499,
        "sub_category_id": 6,
        "file_id": None
    },
    15: {
        "name": "Сундук чемпиона",
        "description": "Champion Chest",
        "price": 999,
        "sub_category_id": 6,
        "file_id": None
    },
    # Clash of Clans - Боевой пропуск (sub_category_id: 7)
    16: {
        "name": "Gold Pass",
        "description": "Месячный боевой пропуск",
        "price": 399,
        "sub_category_id": 7,
        "file_id": None
    },
    17: {
        "name": "Gold Pass Premium",
        "description": "Premium боевой пропуск",
        "price": 649,
        "sub_category_id": 7,
        "file_id": None
    },
    # Clash of Clans - Гемы (sub_category_id: 8)
    18: {
        "name": "80 Гемов",
        "description": "80 Gems",
        "price": 99,
        "sub_category_id": 8,
        "file_id": None
    },
    19: {
        "name": "500 Гемов",
        "description": "500 Gems",
        "price": 449,
        "sub_category_id": 8,
        "file_id": None
    },
    20: {
        "name": "1200 Гемов",
        "description": "1200 Gems",
        "price": 899,
        "sub_category_id": 8,
        "file_id": None
    },
    21: {
        "name": "14000 Гемов",
        "description": "14000 Gems",
        "price": 6999,
        "sub_category_id": 8,
        "file_id": None
    },
    # Clash of Clans - Ресурсы (sub_category_id: 9)
    22: {
        "name": "2 000 000 Золота",
        "description": "2M Gold",
        "price": 299,
        "sub_category_id": 9,
        "file_id": None
    },
    23: {
        "name": "2 000 000 Эликсира",
        "description": "2M Elixir",
        "price": 299,
        "sub_category_id": 9,
        "file_id": None
    },
    24: {
        "name": "200 000 Тёмного эликсира",
        "description": "200K Dark Elixir",
        "price": 499,
        "sub_category_id": 9,
        "file_id": None
    },
    # Кейс с голдой (sub_category_id: 10)
    28: {
        "name": "Кейс с голдой",
        "description": "Открыв кейс, вы можете получить голду: 10, 50, 100, 500, 1000, 1500, 2500, 5000 или 10000",
        "price": 129,
        "sub_category_id": 10,
        "file_id": None
    }
}

# Награды кейса с голдой
GOLD_REWARDS = {
    1: {"amount": 10, "chance": 60},
    2: {"amount": 50, "chance": 50},
    3: {"amount": 100, "chance": 5},
    4: {"amount": 500, "chance": 2},
    5: {"amount": 1000, "chance": 1},
    6: {"amount": 1500, "chance": 0.5},
    7: {"amount": 2500, "chance": 0.3},
    8: {"amount": 5000, "chance": 0.2},
    9: {"amount": 10000, "chance": 0.1}
}

# Цены продажи голды (сколько рублей дают за указанное количество голды)
GOLD_SELL_PRICES = {
    10: 49,
    50: 89,
    100: 199,
    500: 399,
    1000: 699,
    1500: 899,
    2500: 1299,
    5000: 1999,
    10000: 3999
}


def get_games() -> dict:
    """Получить все игры"""
    return GAMES


def get_sub_categories_by_game(game_id: int) -> dict:
    """Получить подкатегории игры"""
    return {
        sub_id: sub_cat 
        for sub_id, sub_cat in SUB_CATEGORIES.items() 
        if sub_cat["game_id"] == game_id
    }


def get_sub_category(sub_category_id: int) -> dict:
    """Получить подкатегорию по ID"""
    return SUB_CATEGORIES.get(sub_category_id)


def get_products_by_sub_category(sub_category_id: int) -> dict:
    """Получить товары подкатегории"""
    return {
        pid: product 
        for pid, product in PRODUCTS.items() 
        if product["sub_category_id"] == sub_category_id
    }


# Обратная совместимость
def get_categories() -> dict:
    """Получить все подкатегории (для обратной совместимости)"""
    return SUB_CATEGORIES


def get_products_by_category(category_id: int) -> dict:
    """Получить товары подкатегории (для обратной совместимости)"""
    return get_products_by_sub_category(category_id)


def get_product(product_id: int) -> dict:
    """Получить товар по ID"""
    return PRODUCTS.get(product_id)


def get_gold_rewards() -> dict:
    """Получить все награды кейса с голдой"""
    return GOLD_REWARDS


def get_gold_sell_price(amount: int) -> int:
    """Получить цену продажи голды по количеству"""
    return GOLD_SELL_PRICES.get(amount, 0)
