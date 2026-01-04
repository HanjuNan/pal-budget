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
        # 创建默认用户，显式设置id=1以确保PostgreSQL兼容性
        from sqlalchemy import text
        # 先尝试插入id=1的用户
        try:
            user = User(id=1, username="default", nickname="记账小达人")
            db.add(user)
            db.commit()
            db.refresh(user)
            # 重置PostgreSQL序列以避免冲突
            try:
                db.execute(text("SELECT setval(pg_get_serial_sequence('myschema.users', 'id'), COALESCE((SELECT MAX(id) FROM myschema.users), 1))"))
                db.commit()
            except:
                pass  # SQLite不支持此操作，忽略
        except Exception as e:
            db.rollback()
            # 如果插入失败，可能是id冲突，尝试获取任意用户
            user = db.query(User).first()
            if not user:
                raise HTTPException(status_code=500, detail="无法创建用户")
    return user


@router.get("/stats")
async def get_user_stats(db: Session = Depends(get_db)):
    """获取用户统计信息"""
    # 尝试获取用户，用于计算记账天数
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        # 尝试获取任意用户
        user = db.query(User).first()

    # 计算记账天数
    days = 0
    if user and user.created_at:
        days = (datetime.now() - user.created_at).days

    # 使用与statistics.py完全相同的查询模式
    # 统计总记录数
    total_records = db.query(func.count(Transaction.id)).filter(
        Transaction.user_id == 1
    ).scalar() or 0

    # 统计总收入 - 使用字符串值比较
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == 1,
        Transaction.type == 'income'
    ).scalar()
    total_income = float(total_income) if total_income else 0.0

    # 统计总支出 - 使用字符串值比较
    total_expense = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == 1,
        Transaction.type == 'expense'
    ).scalar()
    total_expense = float(total_expense) if total_expense else 0.0

    return {
        "days": days,
        "total_records": total_records,
        "total_income": total_income,
        "total_expense": total_expense
    }
