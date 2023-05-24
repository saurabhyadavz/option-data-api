import typing
import pandas as pd
from typing import List
import requests
from datetime import date

def get_spot_data(symbol: str, start_date: date, end_date: date) -> List[typing.Any]:
    try:
        print("SENT REQUEST")
        url = f"http://127.0.0.1:8000/instruments/historical/{symbol}/1minute/{start_date}/{end_date}/"
        response = requests.get(url, params={"spot": "true"})
        print("GOT RESPONSE")
        data = response.json()
        # with open("/Users/saurabh/PycharmProjects/optiondata-api/backtest/data.txt", "w") as file:
        #     file.write(str(data))
        # print("DATA WRITTEN")
        return data
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        return []


def get_spot_df(symbol: str, start_date: date, end_date: date) -> typing.Union[pd.DataFrame, None]:
    data = get_spot_data(symbol, start_date, end_date)
    if data:
        df = pd.DataFrame(data)
        print(f"DATA IS PRESENT")
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        return None

