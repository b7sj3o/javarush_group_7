from telegram import Update, BotCommand, BotCommandScopeChat, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters
import asyncio
import logging

from gpt import ChatGptService
from states_test import get_movie_conversation_handler
from util import (load_message, send_text, send_image, show_main_menu,
                  default_callback_handler, load_prompt, load_instructions)
from credentials import config
from keyboards.gpt_keyboard import gpt_keyboard
from keyboards.talk_keyboard import talk_keyboard
from keyboards.quiz_keyboard import quiz_keyboard, quiz_r_keyboard
# from handlers.conversation_handlers import (
#     gpt_handler,
#     talk_handler,
#     quiz_handler
# )
#



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Головне меню',
        'random': 'Дізнатися випадковий цікавий факт 🧠',
        'gpt': 'Задати питання чату GPT 🤖',
        'talk': 'Поговорити з відомою особистістю 👤',
        'quiz': 'Взяти участь у квізі ❓',
        'movie': 'Рекомендації щодо фільмів та книг'

    })

async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = load_prompt("random")
    message = await update.message.reply_text("Зачекайте декілька секунд...")

    chat_gpt = ChatGptService(config.OPENAI_TOKEN)

    chat_gpt.set_prompt(prompt)
    response_text = await chat_gpt.send_message_list()
    await message.edit_text(response_text)

GPT_DIALOG = 1

async def gpt(update, context):
    await send_image(update, context, "gpt")
    message = load_message("gpt")
    await update.message.reply_text(
        message,
        reply_markup=gpt_keyboard()
    )
    return GPT_DIALOG

async def gpt_dialog(update, context):
    text = update.message.text
    if text == "❌ Вийти з GPT":
        await update.message.reply_text(
            "Діалог завершено",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    prompt = load_prompt("gpt")
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    answer = await chat_gpt.send_question(prompt, text)
    await update.message.reply_text(answer)
    return GPT_DIALOG

async def cancel(update, context):
    await send_text(update, context, "Діалог завершено")
    return ConversationHandler.END

TALK_DIALOG = 1

async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, "talk")
    message = load_message("talk")
    await update.message.reply_text(
        message,
        reply_markup=talk_keyboard()
    )
    return TALK_DIALOG

async def talk_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["talk_prompt"] = query.data
    await query.message.reply_text("Можеш задати питання.")
    return TALK_DIALOG

async def talk_dialog(update, context):
    text = update.message.text
    prompt_name = context.user_data.get("talk_prompt")
    if not prompt_name:
        await update.message.reply_text("Спочатку оберіть особистість.")
        return TALK_DIALOG
    prompt = load_prompt(prompt_name)
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    answer = await chat_gpt.send_question(prompt, text)
    await update.message.reply_text(answer)
    return TALK_DIALOG


QUIZ_THEME = 1
QUIZ_ANSWER = 2

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, "quiz")
    message = load_message("quiz")
    await send_text(update, context, message)
    await update.message.reply_text(
        "Обери тему, на яку будеш грати:",
        reply_markup=quiz_keyboard()
    )
    context.user_data["score"] = 0
    return QUIZ_THEME

async def quiz_theme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    theme = query.data.replace("quiz_", "")
    context.user_data["quiz_theme"] = theme
    prompt = f"""
    Задай одне питання для квізу на тему {theme}.
    Питання повинно бути коротким.
    Формат:
    Питання
    A)
    B)
    C)
    D)
    НЕ пиши правильну відповідь.
    """
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    question = await chat_gpt.send_question(prompt, "Згенеруй питання")
    context.user_data["quiz_question"] = question
    await query.message.edit_text(question)
    return QUIZ_ANSWER

async def quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text
    question = context.user_data["quiz_question"]
    prompt = f"""
    Питання: {question}
    Користувач відповів: {user_answer}
    Скажи чи правильна відповідь: так або ні.
    """
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    result = await chat_gpt.send_question(prompt, user_answer)
    if result.lower().startswith("так"):
        context.user_data["score"] += 1
    score = context.user_data["score"]
    await update.message.reply_text(
        f"{result}\n\n🏆 Рахунок: {score}",
        reply_markup=quiz_r_keyboard()
    )
    return QUIZ_ANSWER

async def quiz_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    theme = context.user_data["quiz_theme"]
    prompt = f"Задай нове питання для квізу на тему {theme}"
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    question = await chat_gpt.send_question(prompt, "Нове питання")
    context.user_data["quiz_question"] = question
    await query.message.reply_text(question)
    return QUIZ_ANSWER

async def quiz_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.edit_text(
        "Обери тему квізу:",
        reply_markup=quiz_keyboard()
    )
    return QUIZ_THEME


async def handle_chat_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    DOCS = load_instructions()
    if not update.message or not update.message.text:
        return
    if update.message.from_user.is_bot: # перевіряємо що повідомлення не від іншого бота
        return
    text = update.message.text.lower()
    bot_username = context.bot.username.lower() # --- 1. перевірка згадки бота ---
    if f"@{bot_username}" in text:
        should_answer = True
    else:
        keywords = ["baf", "crm", "логін", "доступ", "система"] # --- 2. перевірка ключових слів ---
        if any(word in text for word in keywords):
            should_answer = True
        else:
            should_answer = False
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    if not should_answer:
        return
    prompt = load_prompt("work_assistant") + f"\n\nІнструкції компанії:\n{DOCS}"
    answer = await chat_gpt.send_question(prompt, text)
    await asyncio.sleep(3)
    await update.message.reply_text(answer)


gpt_handler = ConversationHandler(
    entry_points=[CommandHandler("gpt", gpt)],
    states={
        GPT_DIALOG: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_dialog)
        ]
    },
    fallbacks=[
        CommandHandler("cancel", cancel)
    ],
)

talk_handler = ConversationHandler(
    entry_points=[CommandHandler("talk", talk)],
    states={
        TALK_DIALOG: [
            CallbackQueryHandler(talk_button, pattern="^talk_"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, talk_dialog),
        ]
    },
    fallbacks=[],
    per_chat=True,
    per_user=True,
    per_message=False
)

quiz_handler = ConversationHandler(
    entry_points=[CommandHandler("quiz", quiz)],
    states={
        QUIZ_THEME: [
            CallbackQueryHandler(quiz_theme, pattern="^quiz_(geo|history|science|movies)$"),
        ],

        QUIZ_ANSWER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_answer),
            CallbackQueryHandler(quiz_next, pattern="^quiz_next$"),
            CallbackQueryHandler(quiz_change, pattern="^quiz_change$"),
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel, pattern="^quiz_end$")
    ],
)

async def error_handler(update, context):
    logging.error("Виникло виключення під час опрацювання оновлення (update):", exc_info=context.error)



def main():
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    # обробники команди:
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('random', random))

    app.add_handler(quiz_handler)
    app.add_handler(gpt_handler)
    app.add_handler(talk_handler)
    app.add_handler(get_movie_conversation_handler())

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_chat_message), group=1)

    app.add_error_handler(error_handler)

    print("Bot started...")
    app.run_polling()

if __name__ == '__main__':
    main()