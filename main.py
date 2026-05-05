from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from fastapi.middleware.cors import CORSMiddleware
import os

# =========================
# DB CONFIG (RENDER FIX)
# =========================
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# =========================
# MODELOS
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)

    trades = relationship("Trade", back_populates="owner")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    asset = Column(String)
    direction = Column(String)
    result = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="trades")


Base.metadata.create_all(bind=engine)

# =========================
# APP
# =========================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# DB DEP
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# ROUTES
# =========================

@app.get("/")
def home():
    return {"msg": "Orion Journal funcionando 🚀"}


# =========================
# AUTH
# =========================
@app.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    new_user = User(email=email, password=password)
    db.add(new_user)
    db.commit()
    return {"msg": "Usuario creado"}


@app.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email, User.password == password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {"user_id": user.id}


# =========================
# TRADES
# =========================
@app.post("/trades")
def create_trade(asset: str, direction: str, result: str, user_id: int, db: Session = Depends(get_db)):
    trade = Trade(
        asset=asset,
        direction=direction,
        result=result,
        user_id=user_id
    )
    db.add(trade)
    db.commit()
    return {"msg": "Trade guardado"}


@app.get("/trades/{user_id}")
def get_trades(user_id: int, db: Session = Depends(get_db)):
    return db.query(Trade).filter(Trade.user_id == user_id).all()
