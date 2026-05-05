from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

app = FastAPI()

# ======================
# CORS (CLAVE)
# ======================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================
# MODELOS
# ======================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    asset = Column(String)
    type = Column(String)
    result = Column(String)


Base.metadata.create_all(bind=engine)

# ======================
# SCHEMAS
# ======================

class UserCreate(BaseModel):
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class TradeCreate(BaseModel):
    user_id: int
    asset: str
    type: str
    result: str


# ======================
# DB
# ======================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ======================
# ENDPOINTS
# ======================

@app.get("/")
def home():
    return {"msg": "Orion Journal funcionando 🚀"}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    new_user = User(email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "Usuario creado", "user_id": new_user.id}


@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email,
        User.password == data.password
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {"msg": "Login correcto", "user_id": user.id}


@app.post("/trades")
def create_trade(trade: TradeCreate, db: Session = Depends(get_db)):
    new_trade = Trade(
        user_id=trade.user_id,
        asset=trade.asset,
        type=trade.type,
        result=trade.result
    )

    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)

    return {"msg": "Trade guardado"}


@app.get("/trades/{user_id}")
def get_trades(user_id: int, db: Session = Depends(get_db)):
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    return trades
