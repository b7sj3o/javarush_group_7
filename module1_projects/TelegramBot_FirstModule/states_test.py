from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from gpt import ChatGptService
from credentials import config

MOVIE_GENRE, USER_DESIRES = 1, 2


async def start_select_movie_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Який жанр фільму ти б хотів побачити?")
    return MOVIE_GENRE


async def handle_genre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genre = update.message.text.strip()
    context.user_data["genre"] = genre
    await update.message.reply_text("Введи інші побажання щодо фільму")
    return USER_DESIRES

async def handle_desires(update: Update, context: ContextTypes.DEFAULT_TYPE):
    desires = update.message.text.strip()
    # context.user_data["desires"] = desires
    await update.message.reply_text("Підбираю фільм...")
    ai_service = ChatGptService(config.OPENAI_TOKEN)
    prompt = f"""
    Порадь 3 фільми.
    
    Жанр: {context.user_data["genre"]}
    Побажання: {desires}
    
    Формат:
    1. Назва (рік) — короткий опис
    2. Назва (рік) — короткий опис
    3. Назва (рік) — короткий опис
    """
    ai_service.set_prompt(prompt)
    text = await ai_service.send_message_list()
    await update.message.reply_text(text)

    return ConversationHandler.END


def get_movie_conversation_handler() -> ConversationHandler:
    """Повертає ConversationHandler для сценарію профілю."""
    return ConversationHandler(
        entry_points=[
            CommandHandler("movie", start_select_movie_flow),
        ],
        states={
            MOVIE_GENRE: [
                MessageHandler(filters.TEXT, handle_genre),
            ],
            USER_DESIRES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_desires),
            ],
        },
        fallbacks=[]
    )
