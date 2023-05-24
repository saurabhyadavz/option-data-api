import typing
import time
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.models.models import *
from backend.utils import utils

async def get_spot_data(symbol: str, from_date: datetime, to_date: datetime,
                        session: AsyncSession) -> List[IndexSpotModel]:
    table_name = utils.get_spot_table_name(symbol, "1minute")
    from_date = datetime.combine(from_date, datetime.min.time())
    to_date = datetime.combine(to_date, datetime.max.time())
    spot_model = get_spot_model(table_name)
    statement = select(spot_model).where(spot_model.date >= from_date,
                                         spot_model.date <= to_date).order_by(spot_model.date)
    async with session.begin():
        await session.execute("BEGIN IMMEDIATE")
        result = await session.execute(statement)
        await session.commit()
    return result.scalars().all()

async def get_options_data(symbol: str, from_date: datetime, to_date: datetime,
                           session: AsyncSession) -> List[IndexOptionsModel]:
    from_date = datetime.combine(from_date, datetime.min.time())
    to_date = datetime.combine(to_date, datetime.max.time())
    contract_year, index = utils.get_index_contract_year(symbol)
    table_name = f"{index}_{contract_year}"
    option_model = get_option_model(table_name)
    statement = select(option_model).where(option_model.date >= from_date,
                                           option_model.date <= to_date,
                                           option_model.symbol == symbol).order_by(option_model.date)
    result = await session.execute(statement)
    return result.scalars().all()

async def get_options_data_by_symbol(index: str, symbol: str, session: AsyncSession) -> List[IndexOptionsModel]:
    year_range = range(2016, 2022)
    table_names = [f"{index.lower()}_{year}" for year in year_range]
    present_tables = []
    for table_name in table_names:
        option_model = get_option_model(table_name)
        result = await session.execute(select(option_model).filter(option_model.symbol == symbol).limit(1))
        if result.fetchone() is not None:
            present_tables.append(table_name)
    results = []
    for table_name in present_tables:
        option_model = get_option_model(table_name)
        statement = select(option_model).where(option_model.symbol == symbol).order_by(option_model.date)
        result = await session.execute(statement)
        results.extend(result.scalars().all())
    results.sort(key=lambda x: x.date)
    return results
