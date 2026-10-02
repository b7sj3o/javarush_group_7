import logging
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, filters, PicklePersistence

from credentials import config
# Імпортуємо наші хендлери з папки handlers
from handlers.common import start, random_fact
from handlers.gpt_handler import get_gpt_handler
from handlers.talk_handler import get_talk_handler
from handlers.quiz_handler import get_quiz_handler
from handlers.image_handler import get_image_to_text_handler
from handlers.recommendation_handler import get_recommendation_handler, start_recommendation

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    # Створення додатку
    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .concurrent_updates(True)
        .persistence(PicklePersistence(filepath="user_data.pickle")) #Стан бота (де зупинився конкретний юзер)
        .build()
    )

    # Базові команди
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('random', random_fact))

    app.add_handler(CallbackQueryHandler(random_fact, pattern='^random_more$'))
    app.add_handler(CallbackQueryHandler(start, pattern='^start$'))  # Кнопка Закінчити

    # Модульні хендлери (ConversationHandlers)
    app.add_handler(get_gpt_handler())
    app.add_handler(get_talk_handler())
    app.add_handler(get_quiz_handler())
    app.add_handler(get_image_to_text_handler())
    app.add_handler(get_recommendation_handler())

    logger.info("Бот запущений...")
    app.run_polling()

if __name__ == "__main__":
    main()