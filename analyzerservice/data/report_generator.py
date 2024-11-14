from datetime import date
from collections import Counter
import logging

from sqlalchemy import select

from .dbbase import async_session
from .dbbase import Product, Analysis

logger = logging.getLogger(__name__)

async def construct_prompt_by_date(target_date: date) -> str:
    """
    Формирует промпт для LLM на основе данных о продажах за указанную дату.

    Args:
        target_date: Дата, для которой нужно сформировать промпт.

    Returns:
        Строку с промптом для LLM.  Если данных за указанную дату нет,
        возвращает строку с сообщением об отсутствии данных.
    """
    async with async_session() as session:
        result = await session.scalars(select(Product).where(Product.date_sell == target_date))

        products = result.all()

        if not products:
            logger.info(f"Нет данных за {target_date}.")
            return f"No data found for {target_date}"


        date_sell = products[0].date_sell
        total_revenue = sum(product.price * product.quantity for product in products)
        top_products = [{"Имя": product.name, "Цена": product.price, "Категория": product.category, "Продано": product.quantity}\
            for product in sorted(products, key=lambda p: p.quantity, reverse=True)[:3]]

        category_counts = Counter(product.category for product in products)
        categories = [f"{category}: {count}" for category, count in category_counts.items()]

        prompt = f"""Проанализируй данные о продажах за {date_sell}:
1. Общая выручка: {total_revenue}
2. Топ-3 товара по продажам: {top_products}
3. Распределение по категориям: {categories}

Составь краткий аналитический отчет с выводами и рекомендациями."""
        return prompt


async def set_ai_analysis(date: date, analysis: str) -> None:
    """
    Сохраняет анализ, полученный от LLM, в базу данных.

    Args:
        date: Дата, к которой относится анализ.
        analysis: Текст анализа, полученный от LLM.
    """
    async with async_session() as session:
        result = Analysis(
            date_sell=date,
            ai_analysis=analysis
        )
        session.add(result)
        await session.commit()
