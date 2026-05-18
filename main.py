import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "ТВОЙ_ТОКЕН_СЮДА"
ADMIN_ID = 123456789  # Замени на свой Telegram ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# База данных
def init_db():
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        created_at TEXT,
        premium_until TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER,
        status TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def create_user(user_id, username):
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, created_at) VALUES (?, ?, ?)",
              (user_id, username, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def set_premium(user_id, days=30):
    until = (datetime.now() + timedelta(days=days)).isoformat()
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute("UPDATE users SET premium_until=? WHERE user_id=?", (until, user_id))
    conn.commit()
    conn.close()

def has_premium(user_id):
    user = get_user(user_id)
    if not user or not user[3]:
        return False
    return datetime.fromisoformat(user[3]) > datetime.now()

def add_purchase(user_id, amount, status='pending'):
    conn = sqlite3.connect('vpn_bot.db')
    c = conn.cursor()
    c.execute("INSERT INTO purchases (user_id, amount, status, created_at) VALUES (?, ?, ?, ?)",
              (user_id, amount, status, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Конфиги
FREE_SERVERS = {
    "Нидерланды 🇳🇱": "vless://45e55198-a5ad-4f19-bb39-236822141d25@188.72.103.3:443?security=tls&allowInsecure=0&encryption=none&type=ws&host=cdn.lovecrafty.link&path=/stream/updates/b66b78d7/019dfd7f-0777-6283-7287-911777c3720f4&sni=cdn.tracker.yandex.net&fp=chrome#",
    "Эстония 🇪🇪": "vless://79d6a159-67c8-4164-9534-89f103c81aaf@bez2.stream-room.com:8443?type=tcp&headerType=none&security=reality&encryption=none&sni=bez2.stream-room.com&fp=chrome&pbk=QHkXBS2ENHV0khgY9VBYi8_9bpfqnUYDcfQN4cW5Qg0&sid=4326&flow=xtls-rprx-vision#",
    "Финляндия 🇫🇮": "vless://5a478129-3e7e-Fade-99d7-95e1da14fbdc@195.209.82.149:443?encryption=none&type=ws&host=s28233.cdn.ngenix.net&path=%2F&security=tls&alpn=h2%2Chttp%2F1.1&fp=qq&sni=s28233.cdn.ngenix.net#",
    "Гонконг 🇭🇰": "vless://b2b62085-f202-4c49-9f19-a44676a3d76d@121.165.93.96:20332?encryption=none&type=ws&path=%2Fray&security=tls&sni=vpn2.rnmcnm.com#",
}

PREMIUM_SERVERS = {
    "США 🇺🇸": "vless://c8d1c6d3-388f-48fc-a8f0-ed90d955d096@2.27.7.250:443?encryption=none&flow=xtls-rprx-vision&fp=&pbk=nPcUKydxoRI66O3tT9O4QCZpLjOBvkGsiXG7pDX1BBw&security=reality&sid=6ba85179e30d4fc2&sni=www.google.com&type=tcp#",
    "Германия 🇩🇪": "vless://9fdfb76e-e677-43b5-9856-97abcb7f778d@81.90.25.255:443?type=tcp&security=reality&flow=xtls-rprx-vision&fp=chrome&pbk=CWGfbuuzEV6_SOecdsIqgrvl1RjcRcemRdHjxWap1wc&sid=71d6a884d0a5&sni=www.icloud.com&spx=/#",
    "Канада 🇨🇦": "vless://ec13d921-3072-4e16-b2cd-af709f7f7894@150.241.83.60:443?type=tcp&headerType=none&security=reality&encryption=none&sni=www.icloud.com&fp=chrome&pbk=xDFXqfhZ7-IQiFwXpXltNe2Axo5O33k4LAqDfAVtyz4&sid=7b&spx=%2F&flow=xtls-rprx-vision#",
}

INSTRUCTION = """📱 Инструкция для iOS-Android:

1. Установите V2Box из App Store или Google Play (бесплатно).

2. Скопируйте URI-конфиг, который вам отправлен.

3. Откройте V2Box, нажмите «Разрешить», затем перейдите на вкладку «Конфигурация».

4. Нажмите на плюсик (+) вверху справа → выберите «Импортировать v2ray URI из буфера».

5. V2Box мгновенно добавит конфиг. Нажмите на него, чтобы подключиться.

6. Готово! Теперь ваш iPhone/Android работает через наш VPN."""

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)
    create_user(user_id, username)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆓 Бесплатный доступ", callback_data="free_access")],
        [InlineKeyboardButton(text="💎 Платный доступ", callback_data="premium_access")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
    ])
    await message.answer(
        "⚡️ RapidTunVPN — интернет без лагов и ограничений.\n"
        "Работаем даже когда всё блокируют и глушат.\n"
        "Высокая скорость, наши локации:\n"
        "🇳🇱 Нидерланды | 🇪🇪 Эстония | 🇫🇮 Финляндия | 🇭🇰 Гонконг (бесплатно)\n"
        "🇺🇸 США | 🇩🇪 Германия | 🇨🇦 Канада (премиум)\n\n"
        "Выберите нужный доступ:",
        reply_markup=kb
    )

@dp.callback_query(lambda c: c.data == "free_access")
async def free_access(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"free_{name}")] for name in FREE_SERVERS
    ])
    await callback.message.answer("🌍 Выберите страну для бесплатного подключения:", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("free_"))
async def send_free_config(callback: CallbackQuery):
    country = callback.data[5:]
    uri = FREE_SERVERS.get(country)
    if uri:
        await callback.message.answer(f"🔗 Ваш конфиг для {country}:\n\n`{uri}`\n\n{INSTRUCTION}", parse_mode="Markdown")
    else:
        await callback.message.answer("❌ Конфиг не найден")

@dp.callback_query(lambda c: c.data == "premium_access")
async def premium_access(callback: CallbackQuery):
    user_id = callback.from_user.id
    if has_premium(user_id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"prem_{name}")] for name in PREMIUM_SERVERS
        ])
        await callback.message.answer("💎 Ваши премиум-страны:", reply_markup=kb)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Купить подписку (150₽/мес)", callback_data="buy_premium")],
            [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")],
        ])
        await callback.message.answer(
            "🔒 Для доступа к премиум-странам нужна подписка.\n"
            "Стоимость: 150₽/месяц (вместо 399₽).\n\n"
            "После покупки вы сразу получите доступ к США, Германии и Канаде.",
            reply_markup=kb
        )

@dp.callback_query(lambda c: c.data.startswith("prem_"))
async def send_premium_config(callback: CallbackQuery):
    user_id = callback.from_user.id
    if not has_premium(user_id):
        await callback.answer("⛔ У вас нет премиум-доступа")
        return
    country = callback.data[5:]
    uri = PREMIUM_SERVERS.get(country)
    if uri:
        await callback.message.answer(f"🔗 Ваш конфиг для {country}:\n\n`{uri}`\n\n{INSTRUCTION}", parse_mode="Markdown")
    else:
        await callback.message.answer("❌ Конфиг не найден")

@dp.callback_query(lambda c: c.data == "profile")
async def profile(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)
    if not user:
        await callback.message.answer("❌ Профиль не найден, нажмите /start")
        return
    prem = "✅ Активна" if has_premium(user_id) else "❌ Нет"
    msg = f"👤 Профиль\nID: {user_id}\nПремиум: {prem}\n\nМои покупки: пока нет"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Купить подписку (150₽/мес)", callback_data="buy_premium")],
    ])
    await callback.message.answer(msg, reply_markup=kb)

@dp.callback_query(lambda c: c.data == "buy_premium")
async def buy_premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    add_purchase(user_id, 150, status='pending')
    await callback.message.answer(
        "💳 Для оплаты подписки переведите 150₽ по реквизитам:\n\n"
        "Сбер: 2202 20XX XXXX XXXX\n"
        "Или напишите @RapidTunSupport\n\n"
        "После оплаты администратор активирует ваш доступ в течение 5 минут."
    )
    # Уведомление админу
    await bot.send_message(ADMIN_ID, f"🛒 Новый заказ от пользователя {user_id} на 150₽")

# Админ-команда для подтверждения оплаты
@dp.message(Command("approve"))
async def approve_payment(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /approve <user_id>")
        return
    try:
        user_id = int(args[1])
        set_premium(user_id)
        add_purchase(user_id, 150, status='approved')
        await message.answer(f"✅ Премиум-доступ выдан пользователю {user_id} на 30 дней")
        await bot.send_message(user_id, "🎉 Ваша подписка активирована! Премиум-страны теперь доступны.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
