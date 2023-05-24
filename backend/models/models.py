from datetime import date, datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class IndexOptionsModel(SQLModel):
    __tablename__ = "banknifty_2016"
    index: Optional[int] = Field(primary_key=True)
    date: datetime
    symbol: str
    open: float
    high: float
    close: float
    low: float
    volume: int
    oi: int
    strike: str
    option_stype: str
    expiry_date: str


class IndexSpotModel(SQLModel, table=True):
    __tablename__ = "BANKNIFTY_SPOT_1_MIN"
    id: int = Field(default=None, primary_key=True)
    date: datetime
    open: float
    high: float
    close: float
    low: float


class NseHoliday(SQLModel, table=True):
    __tablename__ = "nse_holiday"
    id: int = Field(default=None, primary_key=True)
    date: date


class ExpiryInfoModel(SQLModel, table=True):
    __tablename__ = "bnf_expiry_info"
    index: Optional[int] = Field(primary_key=True)
    expiry_comp: str
    expiry_date: date


class TradingDaysModel(SQLModel, table=True):
    __tablename__ = "trading_days"
    Date: date = Field(primary_key=True)


def get_option_model(tablename):
    class OptionModel(SQLModel, table=True):
        __tablename__ = tablename
        __table_args__ = {'extend_existing': True}
        index: Optional[int] = Field(primary_key=True)
        date: datetime
        symbol: str
        open: float
        high: float
        close: float
        low: float
        volume: int
        oi: int
        strike: str
        option_type: str
        expiry_date: str

    return OptionModel


def get_spot_model(tablename):
    class SpotModel(SQLModel, table=True):
        __tablename__ = tablename
        __table_args__ = {'extend_existing': True}
        id: int = Field(default=None, primary_key=True)
        date: datetime
        open: float
        high: float
        close: float
        low: float

    return SpotModel


def get_expiry_info_model(index):
    tablename = "bnf_expiry_info"
    if index == "NIFTY":
        tablename = "nf_expiry_info"
    class ExpiryInfo(SQLModel, table=True):
        __tablename__ = tablename
        __table_args__ = {'extend_existing': True}
        index: Optional[int] = Field(primary_key=True)
        expiry_comp: str
        expiry_date: date

    return ExpiryInfo
