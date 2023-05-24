from datetime import datetime, date
from typing import Union, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.crud import nse_utils_crud
from backend.db.database import get_session
from backend.schemas import schemas

router = APIRouter()


@router.get("/holiday/{dt}/", response_model=bool)
async def check_holiday(dt: str, session: AsyncSession = Depends(get_session)):
    date_string_format = "%Y-%m-%d"
    dt = datetime.strptime(dt, date_string_format).date()
    try:
        data = await nse_utils_crud.get_nse_holiday(dt, session)
        return data
    except Exception as e:
        error_message = f"An error occurred while getting nse holiday: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=e)


@router.get("/day_high_low/{symbol}/{dt}/")
async def get_day_high_low(symbol: str, dt: str, session: AsyncSession = Depends(get_session)):
    try:
        date_string_format = "%Y-%m-%d"
        dt = datetime.strptime(dt, date_string_format).date()
        data = await nse_utils_crud.get_day_high_low(symbol, dt, session)
        return schemas.ResponseSchema[schemas.HighLowSchema](data=data)
    except Exception as e:
        error_message = f"An error occurred while getting days high low: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))


@router.get("/get_unique_option_symbols/{index}/{start_date}/{end_date}")
async def get_unique_option_symbols_between_dates(index: str, start_date: Union[date, str],
                                                  end_date: Union[date, str],
                                                  session: AsyncSession = Depends(get_session)):
    try:
        date_string_format = "%Y-%m-%d"
        start_date = datetime.strptime(start_date, date_string_format) if type(start_date) == str else start_date
        end_date = datetime.strptime(end_date, date_string_format) if type(end_date) == str else end_date
        data = await nse_utils_crud.get_unique_option_symbols_between_dates(index, start_date, end_date, session)
        return schemas.ResponseBase(data=data, message="success")
    except Exception as e:
        error_message = f"An error occurred while getting unique option symbols: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))


@router.get("/get_expiry/{index}")
async def get_expiry_info(index: str, session: AsyncSession = Depends(get_session)):
    try:
        data = await nse_utils_crud.get_expiry_info(index, session)
        return schemas.ResponseSchema[List[schemas.ExpiryInfoSchema]](data=data)
    except Exception as e:
        error_message = f"An error occurred while getting expiry info: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))


@router.get("/get_strikes/{index}/{expiry_date}/")
async def get_strikes_from_expiry_date(index: str, expiry_date: str, session: AsyncSession = Depends(get_session)):
    try:
        data = await nse_utils_crud.get_strikes_from_expiry_date(index, expiry_date, session)
        return schemas.ResponseSchema[List[schemas.OptionsStrikeSchema]](data=data)
    except Exception as e:
        error_message = f"An error occurred while getting expiry info: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))


@router.get("/get_trading_days/")
async def get_trading_days(session: AsyncSession = Depends(get_session)):
    try:
        data = await nse_utils_crud.get_trading_days(session)
        return schemas.ResponseSchema[List[schemas.TradingDaysSchema]](data=data)
    except Exception as e:
        error_message = f"An error occurred while getting expiry info: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))
