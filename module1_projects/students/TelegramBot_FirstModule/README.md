Телеграм-бот, який використовує ChatGPT API для створення діалогів, квізів та спілкування з користувачем.

Бот підтримує такі команди:

- /gpt — діалог з ChatGPT
- /random — розказує випадковий цікавий факт
- /talk — просте спілкування з ботом через кнопки
- /quiz — квіз з різними темами (географія, історія, наука, фільми)
- /movie — підбирає фільми за жанром і побажаннями

Бот інтегрований в груповий телеграм чат.


### **Встановлення**

1. Клонувати репозиторій
git clone https://github.com/Xopo6puu/TelegramBot_FirstModule
2. Перейти в папку проєкту
cd FSN_Project
3. Створити віртуальне середовище
python -m venv .venv
4. Активувати середовище
Windows:
.venv\Scripts\activate
5. Встановити залежності
pip install -r requirements.txt


### **Налаштування**

Створіть файл config.py та додайте:
OPENAI_TOKEN = "your_openai_api_key"
TELEGRAM_TOKEN = "your_telegram_bot_token"

### **Запуск**

python bot.py