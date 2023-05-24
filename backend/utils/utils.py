import re
from typing import Union

SPOT = ("NIFTY", "BANKNIFTY")

def get_spot_table_name(symbol: str, interval: str) -> Union[str, None]:
    try:
        symbol = symbol.replace(" ", "")
        table_name = ""
        if symbol in SPOT and "minute" in interval:
            time_interval = interval.split("minute")[0]
            table_name = f"{symbol.upper()}_SPOT_{time_interval}_MIN"
        elif symbol in SPOT and "day" in interval:
            table_name = f"{symbol.upper()}_SPOT_DAILY"
        return table_name
    except TypeError as e:
        print(f"Incorrect interval format(expected: 1minute, 5minute,"
              f" 10minute, 15minute, 30minute, 60minute, day) or symbol(expected: NIFTY, BANKNIFTY): {e}")
        return None


def get_index_contract_year(symbol: str) -> (str, str):
    try:
        pattern = r'^(BANK)?NIFTY.*(?:PE|CE)$'
        index = "NIFTY"
        if re.match(pattern, symbol):
            if "BANKNIFTY" in symbol:
                index = "BANKNIFTY"
            date_comp = symbol.replace(index, '')[:5]
            year = "20" + date_comp[:2]
            return year, index.lower()
    except TypeError as e:
        print(f"Incorrect contract: {e}")
        return "", ""
