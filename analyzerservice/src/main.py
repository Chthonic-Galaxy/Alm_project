import uvicorn
import asyncio
import logging
import sys

from fastapi import FastAPI
from contextlib import asynccontextmanager

from analyzerservice.web import data_loading_api, report_generation_api
from analyzerservice.data.dbbase import async_main

@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_main()
    logger.info("База данных инициализирована.")
    yield
    pass

# Создание FastAPI приложения
app = FastAPI(
    title="XML Parser & AI Analyzer Service",
    description="Сервис для парсинга XML данных о продажах и генерации аналитических отчетов с помощью LLM.",
    version="1.0.0",
    lifespan=lifespan
)

# Подключение маршрутов
app.include_router(data_loading_api.router)
app.include_router(report_generation_api.router)

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(processName)s %(threadName)s %(levelname)s [%(name)s: %(message)s]")

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler("/var/log/info.log")
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

logger.info("API запущено и готово к работе.")

if __name__ == "__main__":
    """
    Главная точка входа в приложение.

    Этот скрипт:
    1. Инициализирует FastAPI приложение с подключенными маршрутами.
    2. Настраивает логирование для записи событий в консоль и файл.
    3. Выполняет `async_main()` для подготовки базы данных.
    4. Запускает Uvicorn сервер для обслуживания API.
    """
    uvicorn.run("analyzerservice.src.main:app", reload=True, log_level="info")
