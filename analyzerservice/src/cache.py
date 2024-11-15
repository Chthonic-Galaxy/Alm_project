from __future__ import annotations

import json
from datetime import datetime
import hashlib
from typing import Optional, Tuple
import logging
from redis import Redis
from redis.exceptions import RedisError

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class ReportCache:
    """
    Система кэширования отчётов с использованием Redis.

    Attributes:
        redis (Redis): Клиент Redis для операций с кэшем.
        default_ttl (int): Время жизни кэша по умолчанию в секундах.
    """
    
    def __init__(
        self, 
        redis_url: str = 'redis://redis:6379/0',
        default_ttl: int = 24 * 60 * 60
    ) -> None:
        """
        Инициализация экземпляра ReportCache.

        Args:
            redis_url (str): URL для подключения к Redis.
            default_ttl (int): Время жизни кэша по умолчанию в секундах.
        """
        self.redis: Redis = Redis.from_url(redis_url, decode_responses=True)
        self.default_ttl: int = default_ttl
    
    def _generate_cache_key(self, prompt: str, date: datetime.date) -> str:
        """
        Генерирует уникальный ключ кэша на основе промпта и даты.

        Args:
            prompt (str): Текст промпта.
            date (datetime.date): Целевая дата.

        Returns:
            str: Уникальный ключ кэша.
        """
        composite = f"{prompt}:{date.isoformat()}"
        return f"report_cache:{hashlib.sha256(composite.encode()).hexdigest()}"
    
    async def get_cached_report(
        self, 
        prompt: str, 
        date: datetime.date
    ) -> Tuple[Optional[str], bool]:
        """
        Получает закэшированный отчёт, если он существует.

        Args:
            prompt (str): Текст промпта.
            date (datetime.date): Целевая дата.

        Returns:
            Tuple[Optional[str], bool]: Кортеж (закэшированный_отчёт, признак_получения_из_кэша).
        """
        try:
            cache_key = self._generate_cache_key(prompt, date)
            cached_data = self.redis.get(cache_key)
            
            if cached_data:
                logger.info(f"Найден кэш для даты {date}.")
                return json.loads(cached_data), True
            
            logger.info(f"Кэш не найден для даты {date}.")
            return None, False
            
        except RedisError as e:
            logger.warning(f"Ошибка Redis при получении кэша: {e}")
            return None, False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при получении кэша: {e}")
            return None, False

    async def cache_report(
        self, 
        prompt: str, 
        date: datetime.date, 
        report: str,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Кэширует сгенерированный отчёт.

        Args:
            prompt (str): Текст промпта.
            date (datetime.date): Целевая дата.
            report (str): Текст сгенерированного отчёта.
            ttl (Optional[int]): Опциональное время жизни кэша в секундах.

        Returns:
            bool: Признак успешного кэширования.
        """
        try:
            cache_key = self._generate_cache_key(prompt, date)
            ttl = ttl or self.default_ttl
            
            success = self.redis.setex(
                cache_key,
                ttl,
                json.dumps(report)
            )
            
            if success:
                logger.info(f"Успешно закэширован отчёт для даты {date}.")
            else:
                logger.warning(f"Не удалось закэшировать отчёт для даты {date}.")
                
            return bool(success)
            
        except RedisError as e:
            logger.warning(f"Ошибка Redis при кэшировании: {e}")
            return False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при кэшировании: {e}")
            return False

    async def invalidate_cache(self, prompt: str, date: datetime.date) -> bool:
        """
        Инвалидирует закэшированный отчёт.

        Args:
            prompt (str): Текст промпта.
            date (datetime.date): Целевая дата.

        Returns:
            bool: Признак успешной инвалидации.
        """
        try:
            cache_key = self._generate_cache_key(prompt, date)
            success = self.redis.delete(cache_key)
            
            if success:
                logger.info(f"Кэш для даты {date} успешно удалён.")
            else:
                logger.warning(f"Не удалось удалить кэш для даты {date}.")
                
            return bool(success)
        except RedisError as e:
            logger.warning(f"Ошибка Redis при инвалидации кэша: {e}")
            return False
        except Exception as e:
            logger.error(f"Непредвиденная ошибка при инвалидации кэша: {e}")
            return False
