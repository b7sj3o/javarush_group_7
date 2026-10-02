from telegram import Update, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from gpt import ChatGptService


from config import config
from keyboards import REPLY_KEYBOARD


async def start_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт, друже", reply_markup=REPLY_KEYBOARD)

async def answer_button_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ви натиснули кнопку 1")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = context.args[0] if context.args else None

    if not password:
        await update.message.reply_text("Введіть пароль")
        return
    if password == config.admin_password:
        await update.message.reply_text("Доступ надано")
        context.user_data["is_admin"] = True
    else:
        await update.message.reply_text("Не вірний пароль")

async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("is_admin", False):
        await answer_chat_info(update, context, ">>>")
    else:
        await update.message.reply_text("Потрібен доступ")

async def answer_chat_info(update: Update, context: ContextTypes.DEFAULT_TYPE, prefix: str = ""):
    chat = update.effective_chat
    info = f"{prefix} Chat ID: {chat.id}, Type: {chat.type}"
    await context.bot.send_message(chat_id=chat.id, text=info)



if __name__ == '__main__':
    application = ApplicationBuilder().token(config.token).build()

    application.add_handler(CommandHandler("start", start_func))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("get_data", get_data))

    application.add_handler(MessageHandler(filters.Text("Кнопка 1"), answer_button_1))

    print("Бота запущено...")
    application.run_polling()