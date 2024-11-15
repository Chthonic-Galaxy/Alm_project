from __future__ import annotations

from datetime import date
import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Query

from analyzerservice.src.celery_app import generate_report_task, cache
from analyzerservice.service import report_generator as service

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создание роутера с префиксом
router = APIRouter(prefix="/report-generator")

@router.post("/", status_code=201, response_model=Dict[str, Any])
async def trigger_report_generation(
    target_date: date,
    force_refresh: bool = Query(
        False, 
        description="Принудительная регенерация отчёта с игнорированием кэша"
    )
) -> Dict[str, Any]:
    """
    Запускает асинхронную задачу генерации отчёта для указанной даты.

    Args:
        target_date (date): Дата, для которой необходимо сгенерировать отчёт.
        force_refresh (bool): Принудительное игнорирование кэша, если True.

    Returns:
        Dict[str, Any]: Словарь с информацией о запуске задачи:
                        - сообщение,
                        - идентификатор задачи,
                        - признак игнорирования кэша.

    Raises:
        HTTPException: В случае ошибки запуска задачи или других проблем.
    """
    try:
        logger.info(f"Запуск генерации отчёта для даты {target_date}. Force refresh: {force_refresh}")
        
        # Если задан флаг игнорирования кэша, инвалидируем его.
        if force_refresh:
            logger.info(f"Принудительное игнорирование кэша для даты {target_date}")
            prompt = await service.construct_prompt_by_date(target_date)
            if prompt:
                await cache.invalidate_cache(prompt, target_date)
                logger.info(f"Кэш для даты {target_date} успешно инвалидирован.")
            else:
                logger.warning(f"Не удалось сформировать промпт для даты {target_date}, кэш не инвалидирован.")

        # Запуск асинхронной задачи через Celery
        task = generate_report_task.delay(target_date.isoformat())
        logger.info(f"Задача на генерацию отчёта для даты {target_date} запущена. Task ID: {task.id}")
        
        return {
            "message": "Запуск анализа начат",
            "task_id": task.id,
            "cache_ignored": force_refresh
        }
    except Exception as e:
        logger.exception(f"Ошибка при запуске задачи для даты {target_date}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка при запуске задачи: {e}"
        )
