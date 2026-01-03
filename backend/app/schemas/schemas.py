from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from enum import Enum


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class TransactionSource(str, Enum):
    manual = "manual"
    voice = "voice"
    photo = "photo"
    ai = "ai"


class TransactionBase(BaseModel):
    type: TransactionType
    amount: float
    category: str
    description: Optional[str] = None
    date: date
    source: TransactionSource = TransactionSource.manual


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[date] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = "记账小达人"


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class MonthlyStats(BaseModel):
    balance: float
    income: float
    expense: float
    transaction_count: int


class CategoryStats(BaseModel):
    category: str
    amount: float
    percentage: float
    count: int
