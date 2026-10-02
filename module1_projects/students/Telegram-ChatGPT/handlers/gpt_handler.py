from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from telegram.constants import ChatAction
from util import send_image, send_text, load_prompt
from gpt import ChatGptService
from credentials import config

# Стан для діалогу з GPT
GPT_CHAT = 1


async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вхідна точка: надсилає картинку та готує промпт"""
    await send_image(update, context, 'gpt')
    await send_text(update, context, "Напиши своє запитання до ChatGPT 👇")

    # Ініціалізація сервісу
    prompt = load_prompt("gpt")
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    chat_gpt.set_prompt(prompt)

    # Зберігаємо об'єкт у пам'яті для цього користувача
    context.user_data["gpt_service"] = chat_gpt

    return GPT_CHAT


async def gpt_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробляє кожне текстове повідомлення від користувача"""
    # Ефект друкування
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    chat_gpt: ChatGptService = context.user_data.get("gpt_service")

    # Якщо сервіс не ініціалізовано (наприклад, після перезавантаження), виходимо
    if not chat_gpt:
        await send_text(update, context, "Ой, щось пішло не так. Почніть режим заново: /gpt")
        return ConversationHandler.END

    # Отримуємо відповідь від chatgpt
    response = await chat_gpt.add_message(update.message.text)

    # Додаємо кнопку для виходу з режиму
    keyboard = [[InlineKeyboardButton("Завершити діалог ❌", callback_data='stop_gpt')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, reply_markup=reply_markup)
    return GPT_CHAT


async def stop_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вихід з режиму GPT та повернення в головне меню"""
    if update.callback_query:
        await update.callback_query.answer()

    from handlers.common import start
    await start(update, context)
    return ConversationHandler.END


def get_gpt_handler():
    """Повертає сконфігурований ConversationHandler для GPT"""
    return ConversationHandler(
        entry_points=[CommandHandler('gpt', gpt_command)],
        states={
            GPT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_chat_message),
                CallbackQueryHandler(stop_gpt, pattern='^stop_gpt$')
            ]
        },
        fallbacks=[CommandHandler('start', stop_gpt)]
    )