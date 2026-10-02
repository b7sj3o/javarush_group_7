from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


REPLY_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("Кнопка 1")], [KeyboardButton("Кнопка 2")],
        [KeyboardButton("Прибрати клавіатуру")]
    ],
    resize_keyboard=True
)
