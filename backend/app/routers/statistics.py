from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime, timedelta
from typing import List

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

    query = db.query(Transaction).filter(
        Transaction.user_id == 1,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
    )

    income = query.filter(Transaction.type == TransactionType.income).with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    expense = query.filter(Transaction.type == TransactionType.expense).with_entities(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).scalar()

    count = query.count()

    return MonthlyStats(
        balance=float(income) - float(expense),
        income=float(income),
        expense=float(expense),
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

    results = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label('amount'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == 1,
        Transaction.type == type,
        extract('year', Transaction.date) == year,
        extract('month', Transaction.date) == month
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
        if r.type == TransactionType.expense:
            expense_data[date_str] = float(r.amount)
        else:
            income_data[date_str] = float(r.amount)

    return {
        "dates": date_list,
        "expense": list(expense_data.values()),
        "income": list(income_data.values())
    }
