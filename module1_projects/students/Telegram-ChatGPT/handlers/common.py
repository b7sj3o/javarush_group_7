from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ChatAction
from util import load_message, send_image, send_text, show_main_menu, load_prompt
from gpt import ChatGptService
from credentials import config


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Очищаємо режим при поверненні в головне меню
    context.user_data["mode"] = "main"

    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)

    # Викликаємо меню з util.py
    await show_main_menu(update, context, {
        'start': 'Головне меню 🏠',
        'random': 'Цікавий факт 🧠',
        'gpt': 'Питання до GPT 🤖',
        'talk': 'Поговорити з зіркою 👤',
        'image': 'Розпізнати фото 📸',
        'recommend': 'Рекомендації ⭐️',
        'quiz': 'Квіз ❓'
    })

async def random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Якщо це натискання кнопки — прибираємо "годинничок"
    if update.callback_query:
        await update.callback_query.answer()

    # Анімація друкування
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # Надсилаємо зображення
    await send_image(update, context, 'random')

    # Надсилаємо повідомлення про очікування (універсальним способом - завжди працює)
    loading_message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Шукаю щось цікаве для вас... 🔎"
    )

    # Запит до GPT
    prompt = load_prompt("random")
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    chat_gpt.set_prompt(prompt)

    # Отримуємо відповідь
    response_text = await chat_gpt.send_message_list()

    # Кнопки
    keyboard = [
        [InlineKeyboardButton("Хочу ще факт ✨", callback_data='random_more')],
        [InlineKeyboardButton("Закінчити ❌", callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Редагуємо повідомлення очікування на результат від GPT
    await loading_message.edit_text(
        text=response_text,
        reply_markup=reply_markup
    )