from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import csv
import io

from app.database import get_db
from app.models import Transaction, TransactionType
from app.schemas import TransactionCreate, TransactionUpdate, TransactionResponse

router = APIRouter()


@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """创建新交易记录"""
    db_transaction = Transaction(
        user_id=1,  # TODO: 从认证中获取
        **transaction.model_dump()
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 50,
    type: TransactionType = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """获取交易记录列表"""
    query = db.query(Transaction).filter(Transaction.user_id == 1)

    if type:
        query = query.filter(Transaction.type == type)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.order_by(Transaction.date.desc(), Transaction.id.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """获取单个交易记录"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == 1
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="交易记录不存在")
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """更新交易记录"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == 1
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    update_data = transaction_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """删除交易记录"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == 1
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="交易记录不存在")

    db.delete(transaction)
    db.commit()
    return {"message": "删除成功"}


@router.get("/export/csv")
async def export_transactions_csv(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """导出交易记录为CSV"""
    query = db.query(Transaction).filter(Transaction.user_id == 1)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.order_by(Transaction.date.desc(), Transaction.id.desc()).all()

    # 创建CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow(['日期', '类型', '分类', '金额', '备注', '来源'])

    # 写入数据
    for t in transactions:
        # 使用字符串比较以确保PostgreSQL兼容性
        type_str = t.type.value if hasattr(t.type, 'value') else t.type
        type_name = '收入' if type_str == 'income' else '支出'
        source_map = {'manual': '手动', 'voice': '语音', 'photo': '拍照', 'ai': 'AI'}
        source_value = t.source.value if hasattr(t.source, 'value') else t.source
        source_name = source_map.get(source_value, source_value) if t.source else '-'

        writer.writerow([
            t.date.strftime('%Y-%m-%d'),
            type_name,
            t.category,
            f'{t.amount:.2f}',
            t.description or '-',
            source_name
        ])

    output.seek(0)

    # 添加BOM以支持Excel打开中文
    bom = '\ufeff'
    content = bom + output.getvalue()

    return StreamingResponse(
        io.BytesIO(content.encode('utf-8')),
        media_type='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=transactions.csv'
        }
    )
