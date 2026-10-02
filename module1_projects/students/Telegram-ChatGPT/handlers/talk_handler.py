from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler
from telegram.constants import ChatAction
from util import send_image, send_text, load_prompt, send_html
from gpt import ChatGptService
from credentials import config

# Стани діалогу
SELECT_PERSON, TALKING = range(2)

async def talk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'talk')
    buttons = {
        'talk_cobain': 'Курт Кобейн 🎸',
        'talk_hawking': 'Стівен Гокінг 🌌',
        'talk_nietzsche': 'Фрідріх Ніцше 🏛️',
        'talk_queen': 'Королева Єлизавета II 👑',
        'talk_tolkien': 'Дж.Р.Р. Толкін 💍️'
    }
    keyboard = [[InlineKeyboardButton(text, callback_data=code)] for code, text in buttons.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Оберіть особистість для розмови:", reply_markup=reply_markup)
    return SELECT_PERSON

async def talk_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    person_key = query.data  # наприклад, 'talk_cobain'
    prompt = load_prompt(person_key)  # шукає talk_cobain.txt у prompts

    chat_gpt = ChatGptService(config.OPENAI_TOKEN)
    chat_gpt.set_prompt(prompt)
    context.user_data["gpt_talk"] = chat_gpt

    # Визначаємо ім'я для гарного повідомлення
    names = {
        'talk_cobain': 'Курт Кобейн', 'talk_hawking': 'Стівен Гокінг',
        'talk_nietzsche': 'Фрідріх Ніцше', 'talk_queen': 'Королева Єлизавета II',
        'talk_tolkien': 'Дж.Р.Р. Толкін'
    }
    await send_image(update, context, person_key)
    await query.edit_message_text(f"Ви зараз спілкуєтесь з: {names.get(person_key)}. Що ви хочете запитати?")

    return TALKING

async def talk_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    chat_gpt: ChatGptService = context.user_data["gpt_talk"]
    response = await chat_gpt.add_message(update.message.text)

    keyboard = [[InlineKeyboardButton("Закінчити ❌", callback_data='stop')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(response, reply_markup=reply_markup)

async def stop_talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
    await send_text(update, context, "Діалог завершено.")
    # Тут можна викликати функцію start або просто завершити
    from handlers.common import start
    await start(update, context)
    return ConversationHandler.END

def get_talk_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('talk', talk_command)],
        states={
            SELECT_PERSON: [CallbackQueryHandler(talk_choice, pattern='^talk_')],
            TALKING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, talk_message_handler),
                CallbackQueryHandler(stop_talk, pattern='^stop$')
            ]
        },
        fallbacks=[CommandHandler('start', stop_talk)]
    )