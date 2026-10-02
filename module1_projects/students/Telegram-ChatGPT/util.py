import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, \
    BotCommand, MenuButtonCommands, BotCommandScopeChat, MenuButtonDefault
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

# конвертує об'єкт user в рядок
def dialog_user_info_to_str(user_data) -> str:
    mapper = {'language_from': 'Мова оригіналу', 'language_to': 'Мова перекладу',
              'text_to_translate': 'Текст для перекладу'}
    return '\n'.join(map(lambda k, v: (mapper[k], v), user_data.items()))

# надсилає в чат текстове повідомлення
async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    if text.count('_') % 2 != 0:
        message = f"Рядок '{text}' є невалідним з точки зору markdown. Скористайтеся методом send_html()"
        print(message)
        return await update.message.reply_text(message)

    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text,
                                          parse_mode=ParseMode.MARKDOWN)

# надсилає в чат html повідомлення
async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE,
                    text: str) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(chat_id=update.effective_chat.id,
                                          text=text, parse_mode=ParseMode.HTML)

# надсилає в чат текстове повідомлення, та додає до нього кнопки
async def send_text_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE,
                            text: str, buttons: dict) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return await context.bot.send_message(
        update.effective_message.chat_id,
        text=text, reply_markup=reply_markup,
        message_thread_id=update.effective_message.message_thread_id)

# надсилає в чат фото
async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE,
                     name: str) -> Message:
    with open(f'resources/images/{name}.jpg', 'rb') as image:
        return await context.bot.send_photo(chat_id=update.effective_chat.id,
                                            photo=image)

# відображає команду та головне меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(command_list, scope=BotCommandScopeChat(
        chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(),
                                           chat_id=update.effective_chat.id)

# видаляємо команди для конкретного чату
async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands(
        scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(),
                                           chat_id=update.effective_chat.id)

# завантажує повідомлення з папки /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()


# завантажує промпт з папки /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r",
              encoding="utf8") as file:
        return file.read()

async def default_callback_handler(update: Update,
                                   context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    query = update.callback_query.data
    await send_html(update, context, f'You have pressed button with {query} callback')

def get_quiz_keyboard(show_back=False):
    buttons = [
        [InlineKeyboardButton("Ще питання ✨", callback_data="quiz_more")],
        [InlineKeyboardButton("Змінити тему 🔄", callback_data="quiz_change")],
        [InlineKeyboardButton("🏆 Таблиця лідерів", callback_data="quiz_leaderboard")],
        [InlineKeyboardButton("Завершити ❌", callback_data="quiz_stop")]
    ]
    if show_back:
        buttons.insert(0, [InlineKeyboardButton("⬅️ Назад до питання", callback_data="quiz_back_to_q")])

    return InlineKeyboardMarkup(buttons)

def get_answer_keyboard():
    """Створює клавіатуру з варіантами відповідей A, B, C, D з унікальними емодзі"""
    buttons = [
        [
            InlineKeyboardButton("🔴 A", callback_data="ans_A"),  # Червоний круг
            InlineKeyboardButton("🟩 B", callback_data="ans_B")  # Зелений квадрат
        ],
        [
            InlineKeyboardButton("🔷 C", callback_data="ans_C"),  # Синій ромб
            InlineKeyboardButton("⭐ D", callback_data="ans_D")  # Жовта зірка
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def get_quiz_score_text(scores_dict):
    """Формує компактний рядок із балами по темах в один рядок"""
    if not scores_dict:
        return "📊 Прогрес: 0"

    items = []
    for code, score in scores_dict.items():
        # Отримуємо назву теми з емодзі (наприклад, "Математика 📐")
        topic_name = Dialog.QUIZ_TOPICS.get(code, "Інше")
        items.append(f"{topic_name}: {score}")

    # Поєднуємо через роздільник для компактності
    return "📊 " + " | ".join(items)

class Dialog:
    # Назви файлів (без розширення .txt, бо функції його додають)
    HELLO_MSG = "main"
    QUIZ_MSG = "quiz"
    QUIZ_IMG = "quiz"
    QUIZ_PROMPT = "quiz"
    GPT_PROMPT = "gpt"

    # Виносимо теми квізу
    QUIZ_TOPICS = {
        "quiz_prog": "Програмування 🐍",
        "quiz_math": "Математика 📐",
        "quiz_biology": "Біологія 🌿",
        "quiz_geo": "Географія 🌍"
    }

    # Словник досягнень квіз: кількість балів -> Назва
    QUIZ_ACHIEVEMENTS = {
        1: "Перші кроки 🌱",
        10: "Знавець 📚",
        25: "Магістр квізів 🎓",
        50: "Легенда інтелекту 🔥"
    }

    # Динамічний шаблон, який НЕ МОЖНА просто прочитати з файлу,
    # бо в нього треба вставляти змінні (ім'я, очки, досягнення)
    QUIZ_RESULT_TEMPLATE = (
        "✨ {name}, {result}\n\n"
        "📈 За сесію: +1 (У темі: {topic_score})\n"
        "🆙 Рівень: {level} (Всього: {total})\n"
        "🎖 {achievements}\n"
        "{new_award}"
    )