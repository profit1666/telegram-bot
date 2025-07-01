import telebot
from telebot import types
import random
import sqlite3
from datetime import datetime
from webserver import keep_alive

bot = telebot.TeleBot("7856074080:AAE9HoPWWVGGPlWiySZoKlMFVE5VPb5SvVU")
keep_alive()

# 📦 База данных
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
coef_history = []

# 🎰 Генерация коэффициента
def generate_number():
    r = random.random()
    if r < 0.70:
        return round(random.uniform(0.52, 20.0), 2)
    elif r < 0.95:
        return round(random.uniform(20.1, 99.9), 2)
    else:
        return round(random.uniform(100.0, 999.9), 1)

# 🔮 Прогноз следующего коэффициента
def predict_next():
    if len(coef_history) < 5:
        return round(random.uniform(2.0, 10.0), 2)
    avg = sum(coef_history[-5:]) / 5
    return round(avg * random.uniform(0.85, 1.15), 2)

# 🎓 Совет игроку
def generate_advice(lang):
    if len(coef_history) < 5:
        return "📌 Not enough data for advice." if lang == "en" else "📌 सलाह देने के लिए पर्याप्त डेटा नहीं है।"
    avg = sum(coef_history[-5:]) / 5
    if avg < 5.0:
        return "📉 Low signals lately. A spike is possible — consider entering!" if lang == "en" else "📉 हाल के सिग्नल कम रहे हैं — अगले में वृद्धि हो सकती है!"
    elif avg > 50.0:
        return "⚠️ High values recently. Risk of drop — better to wait." if lang == "en" else "⚠️ हाल ही में सिग्नल अधिक रहे हैं — प्रतीक्षा करना बेहतर होगा।"
    else:
        return "📊 Average signals. Consider a small deposit." if lang == "en" else "📊 सिग्नल सामान्य हैं — थोड़ी राशि से प्रयास करें।"

# 🚀 Старт
@bot.message_handler(commands=['start'])
def start(message):
    send_language_selection(message.chat.id)

def send_language_selection(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("🇬🇧 English"), types.KeyboardButton("🇮🇳 हिंदी"))
    bot.send_message(chat_id, "Please choose your language:\nकृपया अपनी भाषा चुनें:", reply_markup=markup)

# 🌍 Выбор языка
@bot.message_handler(func=lambda m: m.text in ["🇬🇧 English", "🇮🇳 हिंदी"])
def choose_language(message):
    lang = "en" if "English" in message.text else "hi"
    chat_id = message.chat.id
    user_language[chat_id] = lang

    now = datetime.utcnow().isoformat()
    cursor.execute("INSERT OR REPLACE INTO leads (user_id, language, timestamp) VALUES (?, ?, ?)",
                   (chat_id, lang, now))
    conn.commit()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🎯 Get Signal" if lang == "en" else "🎯 सिग्नल प्राप्त करें"))
    markup.add("🔮 Predict", "📊 History", "🎓 Advice")
    markup.add(types.KeyboardButton("🔄 Change Language" if lang == "en" else "🔄 भाषा बदलें"))
    bot.send_message(chat_id, "Welcome! Ready to explore signals." if lang == "en" else "स्वागत है! सिग्नल देखने के लिए तैयार हैं।", reply_markup=markup)

# 📲 Обработка кнопок
@bot.message_handler(func=lambda m: m.text in [
    "🎯 Get Signal", "🎯 सिग्नल प्राप्त करें", "🔄 Change Language", "🔄 भाषा बदलें", "🔮 Predict", "📊 History", "🎓 Advice"])
def handle_buttons
