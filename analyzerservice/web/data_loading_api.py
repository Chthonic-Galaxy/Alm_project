import logging
import httpx
import xml.etree.ElementTree as ET

from fastapi import APIRouter, Form, HTTPException
from analyzerservice.service import data_loader as service
from analyzerservice.model.schemas import ProductSchema
from analyzerservice.errors import Missing

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создание роутера с префиксом
router = APIRouter(prefix="/explorer")

@router.post("/xml/get-xml", status_code=201)
async def get_xml_from_url(url: str = Form(..., description='https://www.w3schools.com/xml/plant_catalog.xml')) -> ProductSchema:
    """
    Получает XML данные по указанному URL и возвращает их.

    Args:
        url (str): URL адрес XML документа.

    Returns:
        ProductSchema: Объект с данными, полученными из XML.

    Raises:
        HTTPException: В случае ошибки HTTP запроса (например, 404 Not Found).
        HTTPException: В случае ошибки парсинга XML, с указанием строки и столбца ошибки.
        HTTPException: В случае любой другой непредвиденной ошибки.
    """
    try:
        logger.info(f"Запрос XML данных с URL: {url}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
        
        logger.info(f"Успешно получен ответ от {url}")
        try:
            data = await service.get_xml_data(response.content)
            logger.info(f"Данные успешно извлечены из XML по URL: {url}")
            return data
        except ET.ParseError as e:
            line_number, column_number = e.position
            error_message = f"Ошибка парсинга XML: {e} в строке {line_number}, столбце {column_number}"
            logger.error(error_message)
            raise HTTPException(status_code=400, detail=error_message) from e

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP ошибка при запросе {url}: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP Error: {e}")
    except httpx.ConnectError as e:
        logger.error(f"Ошибка соединения при запросе {url}: {e}")
        raise HTTPException(status_code=504, detail=f"Connection Error: {e}")


@router.get("/")
async def get_all() -> list[ProductSchema]:
    """
    Возвращает все данные из базы данных Product.

    Returns:
        list[ProductSchema]: Список всех данных из базы.
    """
    logger.info("Получение всех данных из базы данных.")
    data = await service.get_all()
    logger.info(f"Успешно получены {len(data)} записи.")
    return data

@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int) -> None:
    """
    Удаляет продукт по его идентификатору.

    Args:
        product_id (int): Идентификатор продукта.

    Raises:
        HTTPException: Если продукт не найден или произошла другая ошибка.
    """
    try:
        logger.info(f"Удаление продукта с ID: {product_id}")
        await service.delete_product(product_id)
        logger.info(f"Продукт с ID {product_id} успешно удалён.")
    except Missing as e:
        logger.warning(f"Продукт с ID {product_id} не найден: {e.msg}")
        raise HTTPException(status_code=404, detail=e.msg)
