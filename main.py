from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os
import psycopg2

app = FastAPI()

# ============================
# CONEXIÓN A LA DB
# ============================

DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Crear tabla si no existe
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
    cursor.execute("SELECT * FROM trades ORDER BY id DESC")
    rows = cursor.fetchall()

    resultado = []
    for row in rows:
        resultado.append({
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
            "apalancamiento": row[10],
            "fecha": str(row[11])
        })

    return resultado
