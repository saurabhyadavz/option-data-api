from datetime import date, time
from typing import Any, List
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from backend.models.models import *
from backend.schemas.schemas import OptionsStrikeSchema
from backend.utils import utils


async def get_nse_holiday(dt: date, session: AsyncSession) -> bool:
    statement = select(NseHoliday).where(NseHoliday.date == dt)
    result = await session.execute(statement)
    if result.first():
        return True
    return False


async def get_day_high_low(symbol: str, dt: date, session: AsyncSession) -> tuple[Any, Any] | None | dict[Any, Any]:
    start_date = datetime.combine(dt, time(hour=9, minute=15))
    end_date = datetime.combine(dt, time(hour=15, minute=30))
    table_name = utils.get_spot_table_name(symbol, "1minute")
    option_model = get_option_model(table_name)
    statement = (select(func.max(option_model.high).label("highest_high"),
                        func.min(option_model.low).label("lowest_low")).
                 where(option_model.date >= start_date, option_model.date <= end_date))
    result = await session.execute(statement)
    return result.first()


async def get_unique_option_symbols_between_dates(index: str, start_date: date,
                                                  end_date: date, session: AsyncSession) -> list[str]:
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    start_year = start_date.year
    end_year = end_date.year
    table_names = [f"{index.lower()}_{year}" for year in range(start_year, end_year + 1)]
    all_result = []
    for table_name in table_names:
        option_model = get_option_model(table_name)
        statement = (
            select(option_model.symbol)
            .distinct()
            .where(option_model.date >= start_datetime, option_model.date <= end_datetime)
        )
        result = await session.execute(statement)
        for row in result:
            all_result.append(row["symbol"])
    return all_result


async def get_expiry_info(index: str, session: AsyncSession) -> List[ExpiryInfoModel]:
    expiry_info_model = get_expiry_info_model(index)
    statement = select(expiry_info_model)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_trading_days(session: AsyncSession) -> List[TradingDaysModel]:
    statement = select(TradingDaysModel)
    result = await session.execute(statement)
    return result.scalars().all()


async def get_strikes_from_expiry_date(index: str, expiry_date: str, session: AsyncSession) -> List[
    OptionsStrikeSchema]:
    year_range = range(2016, 2023)
    table_names = [f"{index.lower()}_{year}" for year in year_range]
    present_tables = []
    for table_name in table_names:
        option_model = get_option_model(table_name)
        result = await session.execute(select(option_model).filter(option_model.expiry_date == expiry_date).limit(1))
        if result.fetchone() is not None:
            present_tables.append(table_name)
    results = []
    for table_name in present_tables:
        option_model = get_option_model(table_name)
        statement = select(option_model.strike, option_model.option_type).where(
            option_model.expiry_date == expiry_date).distinct()
        result = await session.execute(statement)
        results.extend([OptionsStrikeSchema(strike=r[0], option_type=r[1]) for r in result.fetchall()])
    return results
