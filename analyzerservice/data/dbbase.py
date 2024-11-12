from sqlalchemy import Date, String, Integer, Float, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from analyzerservice.config import PGUSERNAME, PGPASSWORD, PGHOST, PGPORT, PGDATABASE
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Настройка асинхронного движка и сессии для работы с PostgreSQL
asyncio_engine = create_async_engine(f"postgresql+psycopg://{PGUSERNAME}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}")
async_session = async_sessionmaker(asyncio_engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовый класс для моделей SQLAlchemy.

    Объединяет AsyncAttrs и DeclarativeBase для поддержки асинхронных операций
    и декларативного стиля определения моделей.

    Args:
        Методы и свойства, доступные для всех моделей, наследующих от Base.
    """
    pass


class Product(Base):
    """
    Модель данных для представления информации о продукте.

    Атрибуты:
        product_id: Уникальный идентификатор продукта (первичный ключ).
        date_sell: Дата продажи.
        name: Название продукта.
        quantity: Количество проданных единиц.
        price: Цена за единицу.
        category: Категория продукта.
    """
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_sell: Mapped[Date] = mapped_column(Date)
    name: Mapped[str] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    category: Mapped[str] = mapped_column(String)


class Analysis(Base):
    """
    Модель данных для представления анализа, проведенного LLM.

    Атрибуты:
        analysis_id: Уникальный идентификатор анализа (первичный ключ, автоинкремент).
        date_sell: Дата, к которой относится анализ.
        ai_analysis: Текст анализа, сгенерированный LLM.
    """
    __tablename__ = "analysis"

    analysis_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date_sell: Mapped[Date] = mapped_column(Date)
    ai_analysis: Mapped[str | None] = mapped_column(Text, nullable=True)


async def async_main() -> None:
    """
    Асинхронная функция для создания таблиц в базе данных.

    Вызывается один раз при запуске приложения для инициализации базы данных.

    Создаёт все таблицы, если они ещё не существуют, основываясь на моделях.
    """
    async with asyncio_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
