import telebot
from telebot import types
import random
import sqlite3
from datetime import datetime
from webserver import keep_alive

# 🔐 Твой токен Telegram-бота
bot = telebot.TeleBot("7856074080:AAE9HoPWWVGGPlWiySZoKlMFVE5VPb5SvVU")

# 🌐 Запуск Flask-сервера для Render
keep_alive()

# 📦 Подключение к базе данных
conn = sqlite3.connect('leads.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS leads (
        user_id INTEGER PRIMARY KEY,
        language TEXT,
        timestamp TEXT
    )
''')
conn.commit()

user_language = {}

# 📲 Генерация сигнала
def generate_number():
    r = random.random()
    if r < 0.70:
        return round(random.uniform(0.52, 20.0), 2)
    elif r < 0.95:
        return round(random.uniform(20.1, 99.9), 2)
    else:
        return round(random.uniform(100.0, 999.9), 1)

# 🚀 Старт команды
@bot.message_handler(commands=['start'])
def start(message):
    send_language_selection(message.chat.id)

def send_language_selection(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("🇬🇧 English"), types.KeyboardButton("🇮🇳 हिंदी"))
    bot.send_message(
        chat_id,
        "Please choose your language:\nकृपया अपनी भाषा चुनें:",
        reply_markup=markup
    )

# 🌐 Выбор языка
@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇮🇳 हिंदी"])
def choose_language(message):
    lang = "en" if "English" in message.text else "hi"
    chat_id = message.chat.id
    user_language[chat_id] = lang

    now = datetime.utcnow().isoformat()
    cursor.execute("INSERT OR REPLACE INTO leads (user_id, language, timestamp) VALUES (?, ?, ?)",
                   (chat_id, lang, now))
    conn.commit()

    btn_signal = "🎯 Get Signal" if lang == "en" else "🎯 सिग्नल प्राप्त करें"
    btn_change = "🔄 Change Language" if lang == "en" else "🔄 भाषा बदलें"
    intro_msg = "Click the button below to get your signal:" if lang == "en" else "नीचे दिए गए बटन पर क्लिक करें:"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(btn_signal))
    markup.add(types.KeyboardButton(btn_change))
    bot.send_message(chat_id, intro_msg, reply_markup=markup)

# 🔘 Обработка кнопок
@bot.message_handler(func=lambda m: m.text in [
    "🎯 Get Signal", "🎯 सिग्नल प्राप्त करें", "🔄 Change Language", "🔄 भाषा बदलें"])
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text
    lang = user_language.get(chat_id, "en")

    if text in ["🔄 Change Language", "🔄 भाषा बदलें"]:
        send_language_selection(chat_id)
        return

    number = generate_number()
    signal_text = f"Your signal: {number}" if lang == "en" else f"आपका सिग्नल: {number}"
    bot.send_message(chat_id, signal_text)

print("🚀 Бот успешно запущен!")
bot.polling(none_stop=True)
