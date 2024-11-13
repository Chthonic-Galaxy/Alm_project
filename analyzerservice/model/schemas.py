from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProductSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True) #  Добавляем from_attributes

    product_id: Optional[int] = None
    date_sell: date = date.today()
    name: str = ''
    quantity: int = 0
    price: float = 0
    category: str = ''


class AnalysisSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Добавляем from_attributes

    analysis_id: int
    date_sell: date
    ai_analysis: Optional[str] = None
