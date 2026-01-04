from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app.models import User, Transaction
from app.schemas import UserCreate, UserResponse

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db)):
    """获取当前用户信息"""
    # TODO: 从认证中获取用户ID
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        # 创建默认用户
        user = User(username="default", nickname="记账小达人")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/stats")
async def get_user_stats(db: Session = Depends(get_db)):
    """获取用户统计信息"""
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        return {
            "days": 0,
            "total_records": 0,
            "total_income": 0,
            "total_expense": 0
        }

    # 计算记账天数
    days = (datetime.now() - user.created_at).days if user.created_at else 0

    # 统计总记录数 - 使用子查询确保PostgreSQL兼容性
    total_records = db.query(Transaction).filter(
        Transaction.user_id == 1
    ).count()

    # 统计总收入 - 使用字符串值比较以确保PostgreSQL兼容性
    income_query = db.query(Transaction).filter(
        Transaction.user_id == 1,
        Transaction.type == 'income'
    ).all()
    total_income = sum(t.amount for t in income_query) if income_query else 0

    # 统计总支出
    expense_query = db.query(Transaction).filter(
        Transaction.user_id == 1,
        Transaction.type == 'expense'
    ).all()
    total_expense = sum(t.amount for t in expense_query) if expense_query else 0

    return {
        "days": days,
        "total_records": total_records,
        "total_income": float(total_income),
        "total_expense": float(total_expense)
    }
