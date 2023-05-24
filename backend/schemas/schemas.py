from typing import TypeVar, Generic, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date

from pydantic.generics import GenericModel

T = TypeVar("T")


class ResponseBase(GenericModel, Generic[T]):
    message: str = ""
    meta: Optional[Dict[str, Any]] = {}
    data: Optional[T] = None


class ResponseSchema(ResponseBase[T], Generic[T]):
    message: str = "success"
    data: Optional[T] = None


class IndexSpotSchema(BaseModel):
    id: int
    date: datetime
    open: float
    high: float
    low: float
    close: float


class IndexOptionsSchema(BaseModel):
    index: Optional[int]
    date: datetime
    symbol: str
    open: float
    high: float
    close: float
    low: float
    volume: int
    oi: int


class HighLowSchema(BaseModel):
    highest_high: str
    lowest_low: str


class ExpiryInfoSchema(BaseModel):
    index: Optional[int]
    expiry_comp: str
    expiry_date: date


class OptionsStrikeSchema(BaseModel):
    strike: str
    option_type: str


class TradingDaysSchema(BaseModel):
    Date: date
