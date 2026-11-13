from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Де лежать задачі: RabbitMQ. Для Redis досить замінити рядок на redis://127.0.0.1:6379/0
    broker_url: str = "amqp://guest:guest@127.0.0.1:5672//"
    # Де лежать результати задач і статуси
    result_backend: str = "redis://127.0.0.1:6379/1"

    # За замовчуванням Mailpit з docker-compose. Для Gmail: smtp.gmail.com, 587, starttls, app password
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 1025
    smtp_starttls: bool = False
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = "shop@example.com"

    email_delay: float = 5  # імітація повільного поштового сервера, секунди


settings = Settings()
