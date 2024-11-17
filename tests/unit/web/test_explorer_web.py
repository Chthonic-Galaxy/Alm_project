import pytest_asyncio
import pytest
import os

from datetime import date

from fastapi import HTTPException
from sqlalchemy import select

from analyzerservice.model.schemas import ProductSchema
from analyzerservice.web import data_loading_api
from analyzerservice.data.dbbase import async_session, Product


os.environ["EXPLORER_UNIT_TEST"] = "true"

@pytest.fixture
def fake_url_valid():
    return 'http://127.0.0.1:5500/analyzerservice/fake/valid.xml'

@pytest.fixture
def fake_url_invalid():
    return 'http://127.0.0.1:5500/analyzerservice/fake/invalid.xml'

@pytest.fixture
def expected_product():
    product = ProductSchema(
        product_id=None,
        date_sell= date(year=2024, month=1, day=1),
        name='Product A',
        quantity=100,
        price=1500.00,
        category='Electronics'
    )
    return product

@pytest_asyncio.fixture
async def fakes() -> list[ProductSchema]:
    return await data_loading_api.get_all()

@pytest.mark.asyncio
async def test_get_xml_from_url(fake_url_valid, expected_product):
    product = await data_loading_api.get_xml_from_url(fake_url_valid)
    assert product == expected_product

@pytest.mark.asyncio
async def test_get_xml_from_url_invalid_url():
    with pytest.raises(HTTPException) as e:
        await data_loading_api.get_xml_from_url('http://invalid-url.com')

    assert e.value.status_code == 504
    assert "Connection Error" in e.value.detail

@pytest.mark.asyncio
async def test_get_xml_from_url_invalid_xml(fake_url_invalid):
    with pytest.raises(HTTPException) as e:
        await data_loading_api.get_xml_from_url(fake_url_invalid)

    assert e.value.status_code == 400
    assert "Ошибка парсинга XML" in e.value.detail

    assert e.value.status_code == 400
    assert "Ошибка парсинга XML" in e.value.detail

@pytest.mark.asyncio
async def test_delete_product(fakes):
    initial_count = len(fakes)
    
    if not fakes:
        pytest.skip("No products found in the database.")
        
    product_id_to_delete = fakes[0].product_id
    await data_loading_api.delete_product(product_id_to_delete)
    
    async with async_session() as session:
        remaining_products = await session.scalars(select(Product))
        assert len(remaining_products.all()) == initial_count - 1

@pytest.mark.asyncio
async def test_delete_product_missing():
    with pytest.raises(HTTPException) as e:
        await data_loading_api.delete_product(0)
    assert e.value.status_code == 404
    assert "Id 0 not found" in e.value.detail
