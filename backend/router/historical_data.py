import time
import typing
from datetime import datetime
from typing import Union, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.schemas import schemas
from starlette import status
from backend.crud import historical_data_crud
from backend.db.database import get_session

router = APIRouter()


@router.get("/{symbol}/{from_date}/{to_date}",
            response_model=Union[schemas.ResponseSchema[List[schemas.IndexSpotSchema]],
                                 schemas.ResponseSchema[List[schemas.IndexOptionsSchema]]])
async def get_historical_data(symbol: str, from_date: Union[str, datetime], to_date: Union[str, datetime],
                              spot: bool = True, session: AsyncSession = Depends(get_session)):
    date_string_format = "%Y-%m-%d"
    from_date_datetime = datetime.strptime(from_date, date_string_format) if type(from_date) == str else from_date
    to_date_datetime = datetime.strptime(to_date, date_string_format) if type(to_date) == str else to_date
    try:
        if spot:
            spot_data = await historical_data_crud.get_spot_data(symbol, from_date_datetime,
                                                                 to_date_datetime, session)
            if spot_data:
                return schemas.ResponseSchema[List[schemas.IndexSpotSchema]](data=spot_data)
            else:
                return schemas.ResponseSchema[List[schemas.IndexSpotSchema]](message="Data not found")
        else:
            options_data = await historical_data_crud.get_options_data(symbol, from_date_datetime,
                                                                       to_date_datetime, session)
            if options_data:
                return schemas.ResponseSchema[List[schemas.IndexOptionsSchema]](data=options_data)
            return schemas.ResponseSchema[List[schemas.IndexOptionsSchema]](message="Data not found")

    except Exception as e:
        error_message = f"An error occurred while getting historical data: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))

@router.get("/options_data/{index}/{symbol}/")
async def get_options_data_by_symbol(index: str, symbol: str, session: AsyncSession = Depends(get_session)):
    try:
        data = await historical_data_crud.get_options_data_by_symbol(index, symbol, session)
        if data:
            return schemas.ResponseSchema[List[schemas.IndexOptionsSchema]](data=data)
        return schemas.ResponseSchema[List[schemas.IndexOptionsSchema]](message="Data not found")
    except Exception as e:
        error_message = f"An error occurred while fetching historical data: {str(e)}"
        print(error_message)
        return schemas.ResponseBase(message=str(e))

