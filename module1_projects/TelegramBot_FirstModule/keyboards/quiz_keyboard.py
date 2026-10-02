from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup, KeyboardButton

def quiz_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🌍 Географія", callback_data="quiz_geo"),
            InlineKeyboardButton("📜 Історія", callback_data="quiz_history")
        ],
        [
            InlineKeyboardButton("🔬 Наука", callback_data="quiz_science"),
            InlineKeyboardButton("🎬 Фільми", callback_data="quiz_movies")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

def quiz_r_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("➡️ Ще питання", callback_data="quiz_next"),
            InlineKeyboardButton("🔄 Змінити тему", callback_data="quiz_change"),
        ],
        [
            InlineKeyboardButton("❌ Завершити", callback_data="quiz_end")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)