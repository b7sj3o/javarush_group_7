from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from util import load_prompt

def talk_keyboard():

    keyboard = [
        [
            InlineKeyboardButton("Курт Кобейн", callback_data="talk_cobain"),
            InlineKeyboardButton("Єлизавета II", callback_data="talk_queen"),
        ],
        [
            InlineKeyboardButton("Джон Толкін", callback_data="talk_tolkien"),
            InlineKeyboardButton("Фрідріх Ніцше", callback_data="talk_nietzsche"),
        ],
        [
            InlineKeyboardButton("Стівен Гокінг", callback_data="talk_hawking"),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)