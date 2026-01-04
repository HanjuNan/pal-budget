from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date, datetime, timedelta
from typing import List
from calendar import monthrange

from app.database import get_db
from app.models import Transaction, TransactionType
from app.schemas import MonthlyStats, CategoryStats

router = APIRouter()


@router.get("/monthly", response_model=MonthlyStats)
async def get_monthly_stats(
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db)
):
    """获取月度统计"""
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month

    # 计算月份的开始和结束日期
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)

    # 查询收入 - 使用字符串值比较以确保PostgreSQL兼容性
    income_result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == 1,
        Transaction.type == 'income',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar()
    income = float(income_result) if income_result else 0.0

    # 查询支出 - 使用字符串值比较以确保PostgreSQL兼容性
    expense_result = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == 1,
        Transaction.type == 'expense',
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar()
    expense = float(expense_result) if expense_result else 0.0

    # 查询交易数量
    count = db.query(func.count(Transaction.id)).filter(
        Transaction.user_id == 1,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0

    return MonthlyStats(
        balance=income - expense,
        income=income,
        expense=expense,
        transaction_count=count
    )


@router.get("/category", response_model=List[CategoryStats])
async def get_category_stats(
    type: TransactionType = TransactionType.expense,
    year: int = None,
    month: int = None,
    db: Session = Depends(get_db)
):
    """获取分类统计"""
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month

    # 计算月份的开始和结束日期
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)

    # 使用字符串值比较以确保PostgreSQL兼容性
    type_value = type.value if hasattr(type, 'value') else type

    results = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('amount'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == 1,
        Transaction.type == type_value,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(Transaction.category).all()

    total = sum(r.amount for r in results) if results else 0

    return [
        CategoryStats(
            category=r.category,
            amount=float(r.amount),
            percentage=round(float(r.amount) / total * 100, 1) if total > 0 else 0,
            count=r.count
        )
        for r in results
    ]


@router.get("/trend")
async def get_trend_stats(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """获取趋势统计（近N天）"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    results = db.query(
        Transaction.date,
        Transaction.type,
        func.sum(Transaction.amount).label('amount')
    ).filter(
        Transaction.user_id == 1,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(Transaction.date, Transaction.type).all()

    # 构建日期列表
    date_list = []
    current = start_date
    while current <= end_date:
        date_list.append(current.strftime('%m/%d'))
        current += timedelta(days=1)

    # 初始化数据
    expense_data = {d: 0 for d in date_list}
    income_data = {d: 0 for d in date_list}

    for r in results:
        date_str = r.date.strftime('%m/%d')
        if r.type == 'expense' or (hasattr(r.type, 'value') and r.type.value == 'expense'):
            expense_data[date_str] = float(r.amount)
        else:
            income_data[date_str] = float(r.amount)

    return {
        "dates": date_list,
        "expense": list(expense_data.values()),
        "income": list(income_data.values())
    }
