import os
from dotenv import load_dotenv
from telegram.ext import Updater

load_dotenv()

class Config:
    token = os.getenv("BOT_TOKEN")
    admin_password = os.getenv("LOGIN_PASSWORD")
    openai_token = os.getenv("OPENAI_TOKEN")


config = Config()