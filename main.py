from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os
import psycopg2

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

conn = None
cursor = None

# ============================
# INICIALIZAR DB SEGURO
# ============================

try:
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
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
        apalancamiento FLOAT,
        fecha TIMESTAMP
    )
    """)
    conn.commit()

except Exception as e:
    print("Error conectando a DB:", e)

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
# ENDPOINTS
# ============================

@app.get("/")
def home():
    return {"msg": "Orion Journal funcionando 🚀 con DB"}

@app.post("/trade")
def crear_trade(trade: Trade):
    if cursor is None:
        return {"error": "DB no conectada"}

    cursor.execute("""
    INSERT INTO trades (activo, tipo, direccion, temporalidad, entry, tp, sl, capital, riesgo, apalancamiento, fecha)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        trade.apalancamiento,
        datetime.utcnow()
    ))
    conn.commit()

    return {"msg": "Trade guardado en DB"}

@app.get("/trades")
def obtener_trades():
    if cursor is None:
        return {"error": "DB no conectada"}

    cursor.execute("SELECT * FROM trades ORDER BY id DESC")
    rows = cursor.fetchall()

    return [
        {
            "id": r[0],
            "activo": r[1],
            "tipo": r[2],
            "direccion": r[3],
            "temporalidad": r[4],
            "entry": r[5],
            "tp": r[6],
            "sl": r[7],
            "capital": r[8],
            "riesgo": r[9],
            "apalancamiento": r[10],
            "fecha": str(r[11])
        }
        for r in rows
    ]
