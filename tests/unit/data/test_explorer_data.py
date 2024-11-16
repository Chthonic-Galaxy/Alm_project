import pytest_asyncio
import pytest
import os
from analyzerservice.model.schemas import ProductSchema
from analyzerservice.data import data_loader
from analyzerservice.errors import Missing
from analyzerservice.data.dbbase import async_session, Product
from sqlalchemy import select

os.environ["EXPLORER_UNIT_TEST"] = "true"

@pytest_asyncio.fixture
async def fakes() -> list[ProductSchema]:
    return await data_loader.get_all()

@pytest.mark.asyncio
async def test_delete_product(fakes):
    initial_count = len(fakes)
    
    if not fakes:
        pytest.skip("No products found in the database.")
        
    product_id_to_delete = fakes[0].product_id
    await data_loader.delete_product(product_id_to_delete)
    
    async with async_session() as session:
        remaining_products = await session.scalars(select(Product))
        assert len(remaining_products.all()) == initial_count - 1

@pytest.mark.asyncio
async def test_delete_product_missing():
    with pytest.raises(Missing) as exc_info:
        await data_loader.delete_product(0)
    assert exc_info.value.msg == "Id 0 not found"