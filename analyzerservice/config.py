import os
import logging
from dotenv import find_dotenv, load_dotenv

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Настройка логирования
logger = logging.getLogger(__name__)

# Загрузка .env файла
load_dotenv(find_dotenv())

# Получение переменных окружения
GEMINI_API = os.getenv("GEMINI_API")
PGUSERNAME = os.getenv("PGUSERNAME")
PGPASSWORD = os.getenv("PGPASSWORD")
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")

# Проверка наличия обязательных переменных окружения
required_env_vars = [
    "GEMINI_API", "PGUSERNAME", "PGPASSWORD", "PGHOST", "PGPORT", "PGDATABASE"
]
missing_env_vars = [var for var in required_env_vars if not globals().get(var)]

if missing_env_vars:
    error_message = f"Отсутствуют обязательные переменные окружения: {', '.join(missing_env_vars)}"
    logger.critical(error_message)
    raise ValueError(error_message)

# Конфигурация Gemini AI
try:
    # Настройка API Gemini
    genai.configure(api_key=GEMINI_API)
    generation_config = {
        "temperature": 1.0,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
        "response_mime_type": "text/plain",
    }

    # Настройки безопасности для Gemini
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    }

    # Инициализация модели
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=(
            "Ты должен отвечать только на Русском языке.\n"
            "Когда проводишь математические расчёты то пиши их шаг за шагом.\n"
            "Ты лучший аналитик."
        ),
        generation_config=generation_config,
        safety_settings=safety_settings
    )

except Exception as e:
    logger.critical(f"Ошибка при настройке Gemini AI: {e}", exc_info=True)
    raise
