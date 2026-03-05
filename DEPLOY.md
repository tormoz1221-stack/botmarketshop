# Инструкция по деплою бота и мини-аппа на хостинг

## Выбор хостинга

Рекомендуемые бесплатные хостинги для Telegram ботов:
- **Render** (render.com) - бесплатный, требует привязки карты
- **Fly.io** - бесплатный лимит
- **Railway** - платный, но удобный
- **VPS** (Timeweb, Reg.ru) - платный, но стабильный

## Подготовка

### 1. Настройка .env файла

Отредактируйте файл `.env`:

```env
BOT_TOKEN=ваш_токен_бота
ADMIN_ID=ваш_telegram_id
MODE=webhook
WEBHOOK_URL=https://your-app-name.onrender.com
WEBHOOK_SECRET=любой_случайный_токен
API_URL=https://your-app-name.onrender.com
```

**Важно:** Замените `your-app-name.onrender.com` на ваш реальный URL после деплоя!

### 2. Настройка мини-аппа

В файле `case-app/index.html` строка 843:
```javascript
window.API_URL = 'https://your-app-name.onrender.com';  // Замените на ваш URL
```

## Деплой на Render

### Шаг 1: Регистрация и создание приложения

1. Зарегистрируйтесь на [render.com](https://render.com)
2. Создайте новый Web Service
3. Подключите ваш GitHub репозиторий

### Шаг 2: Настройка

- **Name**: имя вашего бота
- **Environment**: Python
- **Build Command**: `pip install -r telegram_shop_bot/requirements.txt`
- **Start Command**: `cd telegram_shop_bot && python main.py`

### Шаг 3: Переменные окружения

Добавьте все переменные из `.env` файла в раздел "Environment Variables".

### Шаг 4: Деплой

Нажмите "Create Web Service" и дождитесь завершения.

## Деплой мини-аппа

### Вариант 1: Vercel (рекомендуется)

1. Зарегистрируйтесь на [vercel.com](https://vercel.com)
2. Создайте новый проект
3. Загрузите папку `case-app`
4. Vercel автоматически настроит хостинг

### Вариант 2: GitHub Pages

1. Создайте репозиторий для мини-аппа
2. Загрузите файлы из `case-app`
3. Включите GitHub Pages в настройках

## Настройка webhook после деплоя

После запуска бота на хостинге:

1. Откройте бота в Telegram
2. Отправьте команду `/setwebhook`
3. Бот ответит, что webhook установлен

## Проверка работы

1. Откройте бота в Telegram
2. Нажмите кнопку "🎮 Mini-app"
3. Мини-апп должен загрузиться и работать

## Устранение проблем

### Бот не отвечает
- Проверьте логи на хостинге
- Убедитесь, что webhook установлен: отправьте `/setwebhook`

### Мини-апп не загружается
- Проверьте, что `API_URL` в `index.html` соответствует вашему хостингу
- Проверьте консоль браузера на ошибки

### Ошибки CORS
- Убедитесь, что Flask сервер настроен правильно
- Проверьте, что API доступен по HTTPS
