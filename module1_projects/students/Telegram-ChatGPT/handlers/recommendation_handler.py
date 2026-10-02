from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from telegram.constants import ChatAction
from gpt import ChatGptService
from credentials import config
from util import send_text_buttons, load_message

# Стан діалогу
SELECT_CATEGORY, SELECT_GENRE, SHOW_RECOMMENDATIONS = range(3)


async def start_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['disliked_items'] = []

    categories = {
        "rec_movies": "Фільми 🎬",
        "rec_books": "Книги 📚",
        "rec_music": "Музика 🎵"
    }

    # Використовуємо редагування, якщо це перехід по кнопці
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        # Створюємо клавіатуру вручну для edit_message_text
        keyboard = [[InlineKeyboardButton(v, callback_data=k)] for k, v in categories.items()]
        await query.edit_message_text("Що саме ви хочете обрати?", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await send_text_buttons(update, context, "Що саме ви хочете обрати?", categories)

    return SELECT_CATEGORY


async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    category_code = query.data
    context.user_data['rec_category_code'] = category_code
    # Розширений список жанрів для кожної категорії
    genres = {
        "rec_movies": {
            "gen_action": "Екшн 💥",
            "gen_comedy": "Комедія 😂",
            "gen_drama": "Драма 🎭",
            "gen_scifi": "Фантастика 🚀",
            "gen_horror": "Жахи 👻",
            "gen_thriller": "Трилер 🔪",
            "gen_animation": "Мультфільми 🐣"
        },
        "rec_books": {
            "gen_detective": "Детектив 🕵️‍♂️",
            "gen_fantasy": "Фентезі 🧙‍♂️",
            "gen_history": "Історія 📜",
            "gen_classic": "Класика 📖",
            "gen_psychology": "Психологія 🧠",
            "gen_biography": "Біографія 👤",
            "gen_scifi_book": "Наукова фантастика 🪐"
        },
        "rec_music": {
            "gen_rock": "Рок 🎸",
            "gen_pop": "Поп 🎤",
            "gen_jazz": "Джаз 🎷",
            "gen_classical_m": "Класика 🎻",
            "gen_hiphop": "Хіп-хоп 🎧",
            "gen_electronic": "Електроніка 🎹",
            "gen_blues": "Блюз 🎷"
        }
    }

    current_genres = genres.get(category_code, {})
    # Створюємо кнопки (по 2 в ряд для компактності)
    keyboard = []
    temp_row = []
    for k, v in current_genres.items():
        temp_row.append(InlineKeyboardButton(v, callback_data=k))
        if len(temp_row) == 2:
            keyboard.append(temp_row)
            temp_row = []
    if temp_row:
        keyboard.append(temp_row)
    keyboard.append([InlineKeyboardButton("⬅️ Назад до вибору", callback_data='recommend')])

    # ЗАМІСТЬ нового повідомлення — редагуємо старе
    await query.edit_message_text("Оберіть жанр:", reply_markup=InlineKeyboardMarkup(keyboard))
    return SELECT_GENRE


async def get_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Словник для конвертації кодів у зрозумілі назви
    all_genres = {
        "gen_action": "Екшн", "gen_comedy": "Комедія", "gen_drama": "Драма", "gen_scifi": "Фантастика",
        "gen_horror": "Жахи", "gen_thriller": "Трилер", "gen_animation": "Анімація",
        "gen_detective": "Детектив", "gen_fantasy": "Фентезі", "gen_history": "Історія",
        "gen_classic": "Класична література", "gen_psychology": "Психологія",
        "gen_biography": "Біографія", "gen_scifi_book": "Наукова фантастика",
        "gen_rock": "Рок", "gen_pop": "Поп", "gen_jazz": "Джаз", "gen_classical_m": "Класична музика",
        "gen_hiphop": "Хіп-хоп", "gen_electronic": "Електронна музика", "gen_blues": "Блюз"
    }

    # Перевіряємо: якщо натиснуто кнопку жанру, зберігаємо його.
    # Якщо натиснуто "Не подобається", беремо вже збережений жанр.
    if query.data in all_genres:
        context.user_data['rec_genre_name'] = all_genres[query.data]

    # Отримуємо назву жанру з пам'яті (якщо її там немає — ставимо "будь-який")
    genre_name = context.user_data.get('rec_genre_name', "будь-який")

    category_names = {"rec_movies": "фільм", "rec_books": "книгу", "rec_music": "музичний альбом"}
    cat_code = context.user_data.get('rec_category_code')

    # Візуальний фідбек, що бот думає
    await query.edit_message_text(f"⏳ Шукаю цікавий {category_names.get(cat_code)} у жанрі {genre_name}...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    disliked = ", ".join(context.user_data.get('disliked_items', []))
    prompt = f"Порекомендуй один цікавий {category_names.get(cat_code)} у жанрі {genre_name}."
    if disliked:
        prompt += f" Не рекомендуй: {disliked}."
    prompt += " Напиши назву та короткий опис українською мовою."

    ai_service = ChatGptService(config.OPENAI_TOKEN)
    response = await ai_service.add_message(prompt)
    # Зберігаємо назву для списку ігнорування (перший рядок відповіді)
    context.user_data['last_recommendation'] = response.split('\n')[0]

    buttons = [
        [InlineKeyboardButton("Не подобається 👎 (інший варіант)", callback_data='rec_dislike')],
        [InlineKeyboardButton("Змінити жанр/категорію 🔄", callback_data='recommend')],
        [InlineKeyboardButton("Завершити ❌", callback_data='start')]
    ]

    # Редагуємо повідомлення, замінюючи текст "Підбираю..." на результат
    await query.edit_message_text(text=response, reply_markup=InlineKeyboardMarkup(buttons))
    return SHOW_RECOMMENDATIONS

async def handle_dislike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    last_item = context.user_data.get('last_recommendation')
    if last_item:
        context.user_data['disliked_items'].append(last_item)

    # Повторний виклик рекомендації з тими ж параметрами
    return await get_recommendations(update, context)


# У файлі handlers/recommendation_handler.py

async def stop_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функція для повного виходу з режиму рекомендацій"""
    query = update.callback_query
    if query:
        await query.answer()

    # Очищаємо дані режиму перед виходом
    context.user_data.pop('disliked_items', None)
    context.user_data.pop('rec_category_code', None)

    # Викликаємо головне меню з common.py
    from handlers.common import start
    await start(update, context)
    return ConversationHandler.END


def get_recommendation_handler():
    return ConversationHandler(
        entry_points=[
            CommandHandler("recommend", start_recommendation),
            # Важливо: додаємо обробку кнопки для ПЕРШОГО входу
            CallbackQueryHandler(start_recommendation, pattern='^recommend$')
        ],
        states={
            SELECT_CATEGORY: [
                # Обробляємо вибір категорії
                CallbackQueryHandler(handle_category, pattern='^rec_')
            ],
            SELECT_GENRE: [
                # Обробляємо вибір жанру або повернення назад
                CallbackQueryHandler(get_recommendations, pattern='^gen_'),
                CallbackQueryHandler(start_recommendation, pattern='^start$')
            ],
            SHOW_RECOMMENDATIONS: [
                CallbackQueryHandler(handle_dislike, pattern='^rec_dislike$'),
                # Повернення до вибору жанрів (скидання на початок)
                CallbackQueryHandler(start_recommendation, pattern='^recommend$'),
                # Кнопка завершення
                CallbackQueryHandler(stop_recommendation, pattern='^start$')
            ]
        },
        fallbacks=[
            # Якщо щось пішло не так або натиснуто /start
            CommandHandler('start', stop_recommendation),
            CallbackQueryHandler(stop_recommendation, pattern='^start$')
        ],
        # Дозволяє почати нову розмову, навіть якщо стара не була закрита
        allow_reentry=True
    )