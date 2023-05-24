import typing
import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta, time
from typing import Union, List
import requests

month_names = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
month_number = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "O", "N", "D")

@st.cache_data
def get_resample_time(time_frame: str) -> str:
    resample_time = {
        "1min": "1T",
        "5min": "5T",
        "10min": "10T",
        "15min": "15T",
        "30min": "30T",
        "60min": "60T"
    }
    return resample_time.get(time_frame, '')

@st.cache_data
def get_month_abbreviation(month_num: int) -> str:
    month_str_mapping = {
        1: 'JAN',
        2: 'FEB',
        3: 'MAR',
        4: 'APR',
        5: 'MAY',
        6: 'JUN',
        7: 'JUL',
        8: 'AUG',
        9: 'SEP',
        10: 'OCT',
        11: 'NOV',
        12: 'DEC'
    }
    return month_str_mapping.get(month_num, '')

@st.cache_data
def get_month_integer(month_num: str) -> int | None:
    month_integer_mapping = {
        'JAN': 1,
        'FEB': 2,
        'MAR': 3,
        'APR': 4,
        'MAY': 5,
        'JUN': 6,
        'JUL': 7,
        'AUG': 8,
        'SEP': 9,
        'OCT': 10,
        'NOV': 11,
        'DEC': 12
    }

    return month_integer_mapping.get(month_num, None)

@st.cache_data(show_spinner=False)
def get_key(d, val):
    for k, v in d.items():
        if v == val:
            return k
    return None

@st.cache_data(show_spinner=False)
def get_value(d, k):
    if k in d:
        return d[k]
    else:
        return None

@st.cache_data
def get_last_two_digits_of_year(year: int) -> int:
    return year % 100

@st.cache_data
def convert_to_two_digit_string(num: int) -> str:
    num_str = str(num)
    if len(num_str) < 2:
        num_str = "0" + num_str
    return num_str

@st.cache_data
def get_month_format_from_num(month: int) -> Union[str, int]:
    if month > 9:
        if month == 10:
            return "O"
        elif month == 11:
            return "N"
        else:
            return "D"
    return month

@st.cache_data
def get_month_format_from_str(month: str) -> int:
    if month == "O" or month == "N" or month == "D":
        if month == "O":
            return 10
        elif month == "N":
            return 11
        else:
            return 12
    return int(month)

@st.cache_data
def check_holiday(curr_date: date) -> bool:
    try:
        response = requests.get(f"http://127.0.0.1:8000/nse/holiday/{curr_date}/")
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"Error: {e}")

@st.cache_data
def get_closet_expiry(curr_date: date) -> Union[None, date]:
    first_date = date(curr_date.year, curr_date.month, 1)
    closest_expiry_date = None
    while curr_date >= first_date:
        if not check_holiday(curr_date):
            closest_expiry_date = curr_date
            break
        curr_date -= timedelta(days=1)
    return closest_expiry_date

@st.cache_data
def get_last_thursday_of_month(year: int, month: int) -> date:
    last_day = date(year, month, 1)
    while last_day.month == month:
        last_day += timedelta(days=1)
    last_day -= timedelta(days=1)
    days_to_thursday = (last_day.weekday() - 3) % 7
    last_thursday = last_day - timedelta(days=days_to_thursday)
    return last_thursday

@st.cache_data
def generate_options_contract(index: str, expiry_date: Union[date, str], strike: str, option_type: str) -> str:
    date_string_format = "%Y-%m-%d"
    expiry_date = datetime.strptime(expiry_date, date_string_format).date() if type(expiry_date) == str else expiry_date
    contract = ""
    year = expiry_date.year
    month = expiry_date.month
    day = expiry_date.day
    last_thursday_of_month = get_last_thursday_of_month(year, month)
    month_expiry_date = get_closet_expiry(last_thursday_of_month)
    year_format = get_last_two_digits_of_year(year)
    if month_expiry_date == expiry_date:
        month_abbr = get_month_abbreviation(month)
        contract = f"{index}{year_format}{month_abbr}{strike}{option_type}"
    else:
        month_format = get_month_format_from_num(month)
        day_format = convert_to_two_digit_string(day)
        contract = f"{index}{year_format}{month_format}{day_format}{strike}{option_type}"
    return contract

@st.cache_data(show_spinner=False)
def get_option_data(symbol: str, start_date: date, end_date: date) -> List[typing.Any]:
    try:
        url = f"http://127.0.0.1:8000/instruments/historical/{symbol}/{start_date}/{end_date}/"
        response = requests.get(url, params={"spot": "False"})
        response = response.json()
        if response["message"] == "success":
            return response["data"]
        return []
    except requests.exceptions.HTTPError as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(show_spinner=False)
def get_options_df(symbol: str, start_date: date, end_date: date) -> Union[pd.DataFrame, None]:
    data = get_option_data(symbol, start_date, end_date)
    if data:
        df = pd.DataFrame(data)
        df.drop("index", axis=1, inplace=True)
        df.drop("symbol", axis=1, inplace=True)
        df.drop("oi", axis=1, inplace=True)
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        return None

@st.cache_data(show_spinner=False)
def get_strike_from_contract(index: str, contract: str) -> Union[None, int]:
    if index == "NIFTY":
        return int(contract[10:-2])
    elif index == "BANKNIFTY":
        return int(contract[14:-2])
    return None

@st.cache_data(show_spinner=False)
def get_unique_symbols_between_dates(index: str, start_date: date, end_date: date) -> List[str]:
    try:
        url = f"http://127.0.0.1:8000/nse/get_unique_option_symbols/{index}/{start_date}/{end_date}/"
        response = requests.get(url)
        response = response.json()
        if response["message"] == "success":
            return response["data"]
        return []
    except requests.exceptions.HTTPError as e:
        st.error(f"Error while getting unique symbols: {e}")
        return []

@st.cache_data(show_spinner=False)
def get_unique_options_strike(index: str, expiry_format: str, start_date: date, end_date: date) -> list[int]:
    unique_symbols = get_unique_symbols_between_dates(index, start_date, end_date)
    strikes = []
    for symbol in unique_symbols:
        if expiry_format in symbol:
            strike = get_strike_from_contract(index, symbol)
            if strike:
                strikes.append(strike)
    unique_strikes = sorted(list(set(strikes)))
    return unique_strikes

@st.cache_data(show_spinner=False)
def get_expiry_date_from_symbol(index: str, symbol: str) -> List[typing.Any]:
    try:
        symbol = symbol.split(index.upper())
        expiry_str = symbol[1][:5]
        year = int(expiry_str[0:2]) + 2000
        month, day = None, None
        if expiry_str[2:] in month_names:
            month = get_month_integer(expiry_str[2:])
            last_thursday_of_month = get_last_thursday_of_month(year, month)
            day = get_closet_expiry(last_thursday_of_month).day
        elif expiry_str[2] in month_number:
            month = get_month_format_from_str(expiry_str[2])
            day = int(expiry_str[-2:])
        expiry_date = date(year, month, day)
        return [expiry_str, expiry_date]
    except TypeError as e:
        st.error(f"error occurred on {symbol} {expiry_str}: {e}")
        return []
    except ValueError as e:
        st.error(f"Invalid date entered: {e}  {expiry_str} {month} {day}")
        return []

@st.cache_data(show_spinner=False)
def get_expiry_between_dates(index: str, start_date: date, end_date: date) -> typing.Dict[date, str]:
    unique_symbols = get_unique_symbols_between_dates(index, start_date, end_date)
    expiry_date_map = {}
    for symbol in unique_symbols:
        expiry_list = get_expiry_date_from_symbol(index, symbol)
        if expiry_list:
            dt_str = expiry_list[1].strftime("%Y-%m-%d")
            expiry_date_map[dt_str] = expiry_list[0]
    return expiry_date_map

@st.cache_data(show_spinner=False)
def resample_ohlc_df(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    try:
        df["day"] = df.apply(lambda x: x.date.date(), axis=1)
        df.set_index("date", inplace=True)
        day_groups = df.groupby("day")
        resampled_dfs = []
        for day, day_df in day_groups:
            resampled_df = day_df.resample(timeframe, origin="start").agg({
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last"
            })
            resampled_df.reset_index(inplace=True)
            resampled_dfs.append(resampled_df)
        combined_df = pd.concat(resampled_dfs, ignore_index=True)
        combined_df.set_index("date", inplace=True)
        return combined_df
    except Exception as e:
        print(f"Error occurred while resampling ohlc df: {str(e)}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def get_spot_data(symbol: str, start_date: date, end_date: date) -> List[typing.Any]:
    try:
        url = f"http://127.0.0.1:8000/instruments/historical/{symbol}/1minute/{start_date}/{end_date}/"
        response = requests.get(url, params={"spot": "true"})
        data = response.json()
        return data
    except requests.exceptions.HTTPError as e:
        st.error(f"Error: {e}")
        return []

@st.cache_data(show_spinner=False)
def get_spot_df(symbol: str, start_date: date, end_date: date) -> Union[pd.DataFrame, None]:
    data = get_spot_data(symbol, start_date, end_date)
    if data:
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        return None


# def dump_expiry():
#     unique_symbols = get_unique_symbols_between_dates("BANKNIFTY", date(2016, 1, 1), date(2021, 12, 30))
#     # st.write(unique_symbols)
#     expiry_dates_dict = {}
#     for symbol in unique_symbols:
#         expiry_str, expiry_date = get_expiry_date_from_symbol("BANKNIFTY", symbol)
#         if expiry_str is not None:
#             expiry_dates_dict[expiry_str.strip()] = expiry_date
#
#     df = pd.DataFrame(list(expiry_dates_dict.items()), columns=['expiry_str', 'expiry_date'])
#     df['expiry_date'] = pd.to_datetime(df['expiry_date'])
#     df['expiry_date'] = df['expiry_date'].dt.date
#     df.to_csv("/Users/saurabh/Downloads/bnf_expiry.csv", index=False)
#     return df


