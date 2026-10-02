from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler
from telegram.constants import ChatAction
from util import send_image, Dialog, load_prompt, load_message, get_quiz_keyboard, \
    get_answer_keyboard, get_quiz_score_text
from gpt import ChatGptService
from credentials import config
from db import get_leaderboard, save_score, get_user_data

# СТАНИ ДЛЯ CONVERSATION HANDLER
SELECT_TOPIC, ANSWERING = range(2)


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Початок квізу або зміна теми"""
    user_id = update.effective_user.id
    query = update.callback_query

    # Ініціалізація або оновлення даних з БД
    saved_data = get_user_data(user_id)
    if saved_data:
        context.user_data['total_correct'] = saved_data.get('total', 0)
        context.user_data['achievements'] = saved_data.get('achievements', [])
        # завантажуємо розбиття балів по темах
        context.user_data['scores_by_topic'] = saved_data.get('scores', {})
    else:
        context.user_data['total_correct'] = 0
        context.user_data['achievements'] = []
        context.user_data['scores_by_topic'] = {}

    context.user_data['quiz_score'] = 0

    # Генерація кнопок тем (використовуємо словник з Dialog)
    buttons = [[InlineKeyboardButton(text, callback_data=code)] for code, text in Dialog.QUIZ_TOPICS.items()]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Якщо це зміна теми (через кнопку) — не шлемо картинку і вступ
    if query:
        await query.answer()
        await query.edit_message_text("Оберіть нову тему для квізу 👇", reply_markup=reply_markup)
    else:
        # Якщо команда /quiz — повний вивід
        text = load_message(Dialog.QUIZ_MSG)
        await send_image(update, context, 'quiz')
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=reply_markup)

    return SELECT_TOPIC

async def start_quiz_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Генерація питання на основі обраної теми"""
    query = update.callback_query
    await query.answer()

    data = query.data
    # Визначаємо команду для GPT (quiz_prog, quiz_geo тощо)
    if data == 'quiz_more':
        gpt_command = context.user_data.get('last_gpt_command', 'quiz_more')
    else:
        gpt_command = data
        context.user_data['quiz_topic'] = data
        context.user_data['last_gpt_command'] = data

    # ініціалізуємо список, якщо його немає ---
    if 'used_questions' not in context.user_data:
        context.user_data['used_questions'] = []

    # Ініціалізація GPT з промптом
    chat_gpt = ChatGptService(config.OPENAI_TOKEN)

    # Додаємо до вашого промпту список використаних питань, щоб не повторювались
    used = context.user_data.get('used_questions', [])
    history_constraint = f"\n\nВАЖЛИВО: Не повторюй ці питання: {', '.join(used[-10:])}" if used else ""

    chat_gpt.set_prompt(load_prompt(Dialog.QUIZ_PROMPT) + history_constraint)
    context.user_data['gpt_quiz'] = chat_gpt

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    # Відправляємо саме технічне слово (напр. quiz_geo), як прописано у промпті
    # Також додаємо інформацію про рівень, якщо він > 5
    total_correct = context.user_data.get('total_correct', 0)
    user_level = (total_correct // 5) + 1

    final_request = gpt_command
    if user_level > 5:
        final_request += f" (мій рівень {user_level})"

    question = await chat_gpt.add_message(final_request)

    # Зберігаємо питання для історії та відображення
    context.user_data['used_questions'].append(question.split('\n')[0][:50])
    context.user_data['last_question_text'] = question

    # Відображаємо кольорові кнопки ТІЛЬКИ для біології
    keyboard = get_answer_keyboard() if context.user_data.get('quiz_topic') == "quiz_biology" else None

    await query.edit_message_text(question, reply_markup=keyboard)
    return ANSWERING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка відповіді та розрахунок балів"""
    query = update.callback_query
    if query:
        await query.answer()
        # Прибираємо клавіатуру з повідомлення, на яке натиснули,
        # щоб не було повторних натискань
        await query.edit_message_reply_markup(reply_markup=None)
        user_answer = query.data.replace('ans_', '')
    else:
        user_answer = update.message.text

    chat_gpt = context.user_data.get('gpt_quiz')
    user_name = update.effective_user.first_name
    topic_key = context.user_data.get('quiz_topic')

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    result = await chat_gpt.add_message(user_answer)

    new_award = None
    if "Правильно!" in result:
        # Бали за поточну сесію
        context.user_data['quiz_score'] = context.user_data.get('quiz_score', 0) + 1
        # Глобальні бали (для рівня)
        current_total = context.user_data.get('total_correct', 0) + 1
        context.user_data['total_correct'] = current_total

        # Оновлюємо розбиття балів по темах у локальній пам'яті
        scores = context.user_data.get('scores_by_topic', {})
        scores[topic_key] = scores.get(topic_key, 0) + 1
        context.user_data['scores_by_topic'] = scores

        # Зберігаємо в БД
        new_award = save_score(update.effective_user.id, user_name, topic_key, current_total)

    # Формуємо компактний рядок прогресу в один рядок через util.py
    scores_info = get_quiz_score_text(context.user_data.get('scores_by_topic', {}))

    total = context.user_data.get('total_correct', 0)
    response_text = Dialog.QUIZ_RESULT_TEMPLATE.format(
        name=user_name,
        result=result,
        topic_score=context.user_data['quiz_score'],
        level=(total // 5) + 1,
        total=total,
        achievements=", ".join(context.user_data.get('achievements', [])) or "Початківець 🌱",
        new_award=f"\n\n🏆 **Нове досягнення: {new_award}**" if new_award else ""
    )

    # Додаємо компактний прогрес в кінець
    response_text += f"\n\n{scores_info}"

    context.user_data['last_question_full_text'] = response_text
    keyboard = get_quiz_keyboard()

    if query:
        await query.edit_message_text(response_text, reply_markup=keyboard)
    else:
        await update.message.reply_text(response_text, reply_markup=keyboard)
    return ANSWERING

async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Таблиця лідерів з розбиттям по темах"""
    query = update.callback_query
    await query.answer()

    leaders = get_leaderboard()
    text = "🏆 **Топ знавців:**\n\n"

    for i, l in enumerate(leaders, 1):
        # Формуємо рядок з балами по кожній темі конкретного гравця
        topic_stats = []
        for t_key, t_val in l.get('scores', {}).items():
            t_name = Dialog.QUIZ_TOPICS.get(t_key, "Інше")
            topic_stats.append(f"{t_name}: {t_val}")

        text += f"{i}. {l['name']} (Рівень {l['level']})\n"
        text += f"   └ Всього: {l['total']} | {', '.join(topic_stats)}\n\n"

    await query.edit_message_text(text, reply_markup=get_quiz_keyboard(show_back=True))

async def back_to_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Повернення з лідерборду"""
    query = update.callback_query
    await query.answer()

    text = context.user_data.get('last_question_full_text') or context.user_data.get('last_question_text')
    topic = context.user_data.get('quiz_topic')

    if text == context.user_data.get('last_question_text'):
        keyboard = get_answer_keyboard() if topic == "quiz_biology" else None
    else:
        keyboard = get_quiz_keyboard()

    await query.edit_message_text(text or "Продовжуємо!", reply_markup=keyboard)

async def quiz_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробник усіх натискань кнопок у режимі квізу"""
    data = update.callback_query.data

    if data.startswith('ans_'):
        return await handle_answer(update, context)
    if data == 'quiz_more':
        return await start_quiz_topic(update, context)
    if data == 'quiz_change':
        return await quiz_command(update, context)
    if data == 'quiz_leaderboard':
        return await show_leaderboard(update, context)
    if data == 'quiz_back_to_q':
        return await back_to_question(update, context)
    if data == 'quiz_stop':
        # Виклик головного меню при завершенні
        await update.callback_query.edit_message_text("Гру завершено! Повертаємось у меню... 👋")
        from handlers.common import start
        await start(update, context)
        return ConversationHandler.END

def get_quiz_handler():
    """Налаштування ConversationHandler"""
    # Створюємо рядок для pattern типу "^quiz_(prog|math|biology|geo)$"
    topics_pattern = f"^({'|'.join(Dialog.QUIZ_TOPICS.keys())})$"
    return ConversationHandler(
        entry_points=[CommandHandler('quiz', quiz_command),
                      CallbackQueryHandler(quiz_command, pattern='^quiz$')],
        states={
            SELECT_TOPIC: [
                # pattern оновлюється сам, якщо додати тему в Dialog
                CallbackQueryHandler(start_quiz_topic, pattern=topics_pattern)
            ],
            ANSWERING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer),
                # Додаємо обробку кнопки "Назад", якщо вона натиснута під час гри
                CallbackQueryHandler(quiz_callback_handler, pattern='^quiz_.*|^ans_.*')]
        },
        fallbacks=[CommandHandler('start', quiz_command)],
        allow_reentry=True
    )