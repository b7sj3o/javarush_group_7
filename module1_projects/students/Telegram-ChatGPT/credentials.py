from os import getenv
from dotenv import load_dotenv
# pydantic_settings

load_dotenv()

class Config:
    BOT_TOKEN: str = getenv('BOT_TOKEN')
    OPENAI_TOKEN: str = getenv("GPT_TOKEN")

config = Config()