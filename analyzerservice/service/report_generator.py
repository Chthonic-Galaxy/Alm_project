from datetime import date
import logging

from analyzerservice.data import report_generator  # Импортируем под новым именем

# Настройка логирования
logger = logging.getLogger(__name__)

async def construct_prompt_by_date(target_date: date) -> str:
    """
    Формирует промпт для LLM на основе данных о продажах за указанную дату.

    Args:
        target_date (date): Дата, для которой требуется сформировать промпт.

    Returns:
        str: Промпт для LLM в виде строки.
    """
    logger.info(f"Формирование промпта для даты {target_date}.")
    prompt = await report_generator.construct_prompt_by_date(target_date)
    logger.info(f"Промпт для даты {target_date} успешно сформирован.")
    return prompt


async def set_ai_analysis(date: date, analysis: str) -> None:
    """
    Сохраняет анализ, полученный от LLM, в базу данных.

    Args:
        date (date): Дата, к которой относится анализ.
        analysis (str): Текст анализа от LLM.
    """
    logger.info(f"Сохранение анализа для даты {date}.")
    await report_generator.set_ai_analysis(date, analysis)
    logger.info(f"Анализ для даты {date} успешно сохранён.")
