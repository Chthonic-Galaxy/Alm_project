from analyzerservice.data import data_loader as data
from analyzerservice.model.schemas import ProductSchema
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

async def get_xml_data(response: bytes) -> dict:
    """
    Обрабатывает XML данные и сохраняет информацию о продуктах в базу данных.

    Args:
        response (bytes): XML данные в виде байтовой строки.

    Returns:
        dict: Словарь с результатом операции, например, количеством обработанных записей.
    """
    logger.info("Начало обработки XML данных.")
    result = await data.get_xml_data(response)
    logger.info("XML данные успешно обработаны.")
    return result


async def get_all() -> list[ProductSchema]:
    """
    Получает все записи о продуктах из базы данных.

    Returns:
        list[ProductSchema]: Список всех продуктов из базы данных.
    """
    logger.info("Запрос всех продуктов из базы данных.")
    products = await data.get_all()
    logger.info(f"Получено {len(products)} продуктов из базы данных.")
    return products


async def delete_product(product_id: int) -> None:
    """
    Удаляет продукт из базы данных по его ID.

    Args:
        product_id (int): Идентификатор продукта для удаления.
    """
    logger.info(f"Попытка удалить продукт с ID: {product_id}.")
    await data.delete_product(product_id)
    logger.info(f"Продукт с ID {product_id} успешно удалён.")
