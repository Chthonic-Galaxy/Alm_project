from datetime import datetime
import xml.etree.ElementTree as ET
import logging

from fastapi import HTTPException
from sqlalchemy import select

from .dbbase import async_session
from .dbbase import Product
from analyzerservice.model.schemas import ProductSchema
from analyzerservice.errors import Missing

logger = logging.getLogger(__name__)

async def get_xml_data(response: bytes) -> ProductSchema:
    """
    Извлекает данные о продуктах из XML и сохраняет их в базу данных.

    Args:
        response (bytes): XML данные в виде байтовой строки.

    Returns:
        Словарь с сообщением об успешном сохранении данных.
    """
    try:
        # Парсинг XML данных
        xml_data = ET.fromstring(response)
        date = datetime.strptime(xml_data.attrib.get('date'), '%Y-%m-%d').date()

        for product in xml_data.iter('product'):
            try:
                # Извлечение данных о продукте
                quantity = int(product.find('quantity').text)
                price = float(product.find('price').text)
                product_schema = ProductSchema(
                    date_sell=date,
                    name=product.find('name').text,
                    quantity=quantity,
                    price=price,
                    category=product.find('category').text
                )
                # Сохранение данных в базу
                await set_product(product_schema)
            except ValueError as e:
                logger.exception(f"Ошибка преобразования данных продукта: {e}")
                raise HTTPException(status_code=400, detail=f"Плохой запрос: {e}") from e

        return product_schema
    except ET.ParseError as e:
        raise
    except Exception as e:
        logger.exception(f"Непредвиденная ошибка: {e}") # логирование непредвиденной ошибки
        raise


async def set_product(product_schema: ProductSchema) -> None:
    """
    Сохраняет данные о продукте в базу данных.

    Args:
        product_schema (ProductSchema): Данные о продукте для сохранения.
    """
    async with async_session() as session:
        product = Product(
            date_sell=product_schema.date_sell,
            name=product_schema.name,
            quantity=product_schema.quantity,
            price=product_schema.price,
            category=product_schema.category
        )
        session.add(product)
        await session.commit()
        logger.info(f"Продукт {product_schema.name} успешно сохранён в базе.")


async def get_all() -> list[ProductSchema]:
    """
    Возвращает все продукты из базы данных как Pydantic модели.

    Returns:
        list[ProductSchema]: Список Pydantic моделей, представляющих продукты.
    """
    async with async_session() as session:
        result = await session.scalars(select(Product))
        products = result.all()
        return [ProductSchema.model_validate(product) for product in products]
    
async def delete_product(product_id):
    async with async_session() as session:
        result = await session.scalar(select(Product).where(Product.product_id==product_id))

        if not result:
            raise Missing(msg=f"Id {product_id} not found")
        else:
            await session.delete(result)
            await session.commit()
