from telegram import ReplyKeyboardMarkup, KeyboardButton

def gpt_keyboard():
    keyboard = [
        [KeyboardButton("🔄 Ще відповідь")],
        [KeyboardButton("❌ Вийти з GPT")]
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )