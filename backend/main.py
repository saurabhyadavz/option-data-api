import os
import sys
python_path = os.path.dirname((os.path.dirname(__file__)))
sys.path.append(python_path)

from fastapi import FastAPI
from backend.router import historical_data, nse_utils

app = FastAPI()

app.include_router(historical_data.router, prefix="/instruments/historical", tags=["Historical Data"])
app.include_router(nse_utils.router, prefix="/nse", tags=["NSE Utility"])
