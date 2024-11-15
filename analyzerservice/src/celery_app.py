from __future__ import annotations

import asyncio
from datetime import datetime
import logging
from typing import Optional

from celery import Celery
from google.api_core.exceptions import ResourceExhausted

from analyzerservice.service import report_generator as service
from analyzerservice.config import model
from .cache import ReportCache

# Настройка Celery
celery_app = Celery(__name__, broker='redis://redis:6379/0', backend='redis://redis:6379/0')
cache = ReportCache()

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@celery_app.task(name="generate_report")
def generate_report_task(target_date_str: str) -> str:
    """
    Celery задача для генерации отчёта с использованием LLM и кэширования.

    Args:
        target_date_str (str): Дата в формате ISO строки.

    Returns:
        str: Текст сгенерированного отчёта или сообщение об ошибке.
    """
    try:
        target_date = datetime.fromisoformat(target_date_str).date()
    except ValueError:
        logger.error(f"Неверный формат даты: {target_date_str}")
        return "Неверный формат даты"

    async def run_analysis() -> str:
        """
        Выполняет анализ данных для указанной даты, включая генерацию и кэширование отчёта.

        Returns:
            str: Сгенерированный отчёт или сообщение об ошибке.
        """
        try:
            # Формирование промпта
            prompt = await service.construct_prompt_by_date(target_date)
            if prompt is None:
                logger.error(f"Не удалось сформировать промпт для даты: {target_date}")
                return "Не удалось сформировать промпт"

            # Проверка наличия отчёта в кэше
            cached_report, is_cached = await cache.get_cached_report(prompt, target_date)
            if is_cached:
                logger.info(f"Возвращён закэшированный отчёт для даты: {target_date}")
                return cached_report

            # Генерация отчёта с помощью AI модели
            response = await model.generate_content_async(prompt)
            report_text = response.text
            
            # Кэширование отчёта
            cache_success = await cache.cache_report(prompt, target_date, report_text, ttl=24 * 60 * 60)
            if not cache_success:
                logger.warning(f"Не удалось закэшировать отчёт для даты: {target_date}")
            
            # Сохранение анализа в базе данных
            await service.set_ai_analysis(target_date, report_text)
            return report_text
            
        except ResourceExhausted:
            logger.exception("Ошибка генерации отчёта: Превышен лимит запросов к AI")
            return "Ошибка генерации отчёта: Превышен лимит запросов к AI"
        except Exception as e:
            logger.exception(f"Ошибка генерации отчёта: {e}")
            return f"Ошибка генерации отчёта: {e}"

    # Настройка цикла событий для выполнения асинхронного анализа
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(run_analysis())
