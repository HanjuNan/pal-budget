import os
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base

# PostgreSQL 时使用 myschema，SQLite 不需要 schema
SCHEMA = "myschema" if os.environ.get("DATABASE_URL") else None


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class TransactionSource(str, enum.Enum):
    manual = "manual"
    voice = "voice"
    photo = "photo"
    ai = "ai"


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    nickname = Column(String(50), default="记账小达人")
    avatar_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    icon = Column(String(50))
    type = Column(Enum(TransactionType))
    color = Column(String(20))


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"schema": SCHEMA} if SCHEMA else {}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(f"{SCHEMA}.users.id" if SCHEMA else "users.id"))
    type = Column(Enum(TransactionType))
    amount = Column(Float)
    category = Column(String(50))
    description = Column(String(255), nullable=True)
    date = Column(Date)
    source = Column(Enum(TransactionSource), default=TransactionSource.manual)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")
