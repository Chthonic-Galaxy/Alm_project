from datetime import datetime
import xml.etree.ElementTree as ET
import logging
from typing import List, Dict

from ..data import data_loader as data  # Импортируем под новым именем

logger = logging.getLogger(__name__)

async def get_xml_data(response: bytes) -> Dict[str, str]:
    """
    Извлекает данные о продуктах из XML, преобразует их и передает для сохранения в базу данных.

    Args:
        response: XML данные в виде байтовой строки.

    Returns:
        Словарь с сообщением об успешном сохранении данных или об ошибке.
    """
    try:
        # Парсим XML
        xml_data = ET.fromstring(response)
        date = datetime.strptime(xml_data.attrib.get('date'), '%Y-%m-%d').date()

        for product in xml_data.iter('product'):
            try:
                # Сохраняем каждый продукт в базе данных
                await data.set_product(
                    product_id=int(product.find('id').text),  # Преобразование типов здесь
                    date_sell=date,
                    name=product.find('name').text,
                    quantity=int(product.find('quantity').text),  # Преобразование типов здесь
                    price=float(product.find('price').text),  # Преобразование типов здесь
                    category=product.find('category').text
                )
            except ValueError as e:
                logger.error(f"Ошибка преобразования данных продукта: {e}")
            except Exception as e:
                logger.error(f"Ошибка обработки продукта: {e}")

        return {"message": "Data saved successfully."}
    
    except ET.ParseError as e:
        logger.error(f"Ошибка парсинга XML: {e}")
        return {"error": f"Ошибка парсинга XML: {e}"}
    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return {"error": "Произошла непредвиденная ошибка."}

async def get_all() -> List[Dict]:
    """
    Возвращает все продукты из базы данных.

    Returns:
        Список всех продуктов.
    """
    return await data.get_all()
