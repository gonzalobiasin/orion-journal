from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

# -------- CONEXIÓN A LA BASE DE DATOS --------
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    activo TEXT,
    tipo TEXT,
    direccion TEXT,
    temporalidad TEXT,
    entry FLOAT,
    tp FLOAT,
    sl FLOAT,
    capital FLOAT,
    riesgo FLOAT,
    apalancamiento FLOAT
)
""")
conn.commit()

# -------- MODELO --------
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

# -------- RUTA FRONTEND --------
@app.get("/")
def home():
    return FileResponse("index.html")

# -------- GUARDAR TRADE --------
@app.post("/trade")
def crear_trade(trade: Trade):
    cursor.execute("""
    INSERT INTO trades (activo, tipo, direccion, temporalidad, entry, tp, sl, capital, riesgo, apalancamiento)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        trade.activo,
        trade.tipo,
        trade.direccion,
        trade.temporalidad,
        trade.entry,
        trade.tp,
        trade.sl,
        trade.capital,
        trade.riesgo,
        trade.apalancamiento
    ))
    conn.commit()
    return {"msg": "Trade guardado"}

# -------- VER TRADES --------
@app.get("/trades")
def obtener_trades():
    cursor.execute("SELECT * FROM trades")
    rows = cursor.fetchall()

    trades = []
    for row in rows:
        trades.append({
            "id": row[0],
            "activo": row[1],
            "tipo": row[2],
            "direccion": row[3],
            "temporalidad": row[4],
            "entry": row[5],
            "tp": row[6],
            "sl": row[7],
            "capital": row[8],
            "riesgo": row[9],
            "apalancamiento": row[10]
        })

    return trades
