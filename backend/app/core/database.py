import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# В реальном проекте лучше использовать переменные окружения через pydantic-settings
# Формат: postgresql://пользователь:пароль@хост:порт/имя_базы
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:root@localhost:5432/smart_city_db"
)

# Создаем движок SQLAlchemy для PostgreSQL
# Для Postgres параметр check_same_thread не нужен (в отличие от SQLite)
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Максимальное количество постоянных подключений в пуле
    max_overflow=10,       # Сколько дополнительных подключений можно открыть при пиках
    pool_pre_ping=True     # Проверяет живое ли соединение перед отправкой запроса (предотвращает 500 ошибки)
)

Base = declarative_base()