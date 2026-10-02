from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from gpt import ChatGptService
from credentials import config

WAIT_PHOTO = 1


async def start_image_to_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Якщо виклик через кнопку
    if update.callback_query:
        await update.callback_query.answer()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Надішліть фото для аналізу. 📸")
    else:
        await update.message.reply_text("Надішліть фото для аналізу. 📸")
    return WAIT_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    mime = "image/jpeg"

    msg = await update.message.reply_text("Аналізую зображення...🔍")
    ai = ChatGptService(config.OPENAI_TOKEN)
    # GPT описує, що знаходиться на зображенні
    description = await ai.analyze_image(image_bytes, mime_type=mime)
    # Передаємо відповідь користувачеві
    await msg.edit_text(description)
    # Повертаємо кнопки головного меню після аналізу
    from handlers.common import start
    await start(update, context)
    return ConversationHandler.END

def get_image_to_text_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("image", start_image_to_text)],
        states={
            WAIT_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[],
    )