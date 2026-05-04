from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime

app = FastAPI()

# ============================
# MODELO
# ============================

class Trade(BaseModel):
    activo: str
    tipo: str
    direccion: str
    temporalidad: str
    entry: float
    tp: float
    sl: float
    capital: float
    riesgo: float
    apalancamiento: float

# ============================
# BASE TEMPORAL (memoria)
# ============================

trades = []

# ============================
# ENDPOINTS
# ============================

@app.get("/")
def home():
    return {"msg": "Orion Journal funcionando 🚀"}

@app.post("/trade")
def crear_trade(trade: Trade):
    data = trade.dict()
    data["fecha"] = str(datetime.utcnow())
    trades.append(data)
    return {"msg": "Trade guardado"}

@app.get("/trades")
def obtener_trades():
    return trades
