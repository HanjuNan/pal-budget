# -*- coding: utf-8 -*-
"""
初始化示例数据脚本
运行: python init_data.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from datetime import date, timedelta
import random

from app.database import SessionLocal, engine, Base
from app.models import User, Transaction, TransactionType, TransactionSource

# 创建表
Base.metadata.create_all(bind=engine)

# 示例数据
expense_categories = [
    ('餐饮', [15, 25, 35, 50, 80]),
    ('交通', [5, 10, 15, 30, 50]),
    ('购物', [50, 100, 200, 300, 500]),
    ('娱乐', [30, 50, 100, 150, 200]),
    ('住房', [1500, 2000, 2500, 3000]),
    ('医疗', [50, 100, 200, 500]),
    ('教育', [100, 200, 500, 1000]),
    ('通讯', [50, 100, 150, 200]),
]

income_categories = [
    ('工资', [8000, 10000, 12000, 15000]),
    ('奖金', [1000, 2000, 5000]),
    ('兼职', [500, 1000, 2000, 3000]),
    ('投资', [100, 500, 1000, 2000]),
]

descriptions = {
    '餐饮': ['午餐', '晚餐', '外卖', '咖啡', '奶茶', '水果'],
    '交通': ['地铁', '公交', '打车', '共享单车', '加油'],
    '购物': ['超市购物', '日用品', '衣服', '数码产品', '零食'],
    '娱乐': ['电影票', '游戏', 'KTV', '演唱会', '旅游'],
    '住房': ['房租', '水电费', '物业费', '燃气费'],
    '医疗': ['看病', '买药', '体检'],
    '教育': ['书籍', '网课', '培训班'],
    '通讯': ['话费', '网费', '会员'],
    '工资': ['月薪'],
    '奖金': ['季度奖', '年终奖', '绩效奖'],
    '兼职': ['私活', '稿费', '咨询费'],
    '投资': ['股票收益', '基金分红', '利息'],
}


def init_data():
    db = SessionLocal()

    try:
        # 清空现有数据
        db.query(Transaction).delete()
        db.query(User).delete()
        db.commit()

        # 创建用户
        user = User(
            username='demo',
            nickname='记账小达人'
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"[OK] Created user: {user.nickname}")

        # 生成最近30天的交易数据
        today = date.today()
        transactions = []

        for i in range(30):
            current_date = today - timedelta(days=i)

            # 每天随机生成1-5笔支出
            num_expenses = random.randint(1, 5)
            for _ in range(num_expenses):
                category, amounts = random.choice(expense_categories)
                amount = random.choice(amounts) + random.uniform(-5, 5)
                desc_list = descriptions.get(category, [''])

                transactions.append(Transaction(
                    user_id=user.id,
                    type=TransactionType.expense,
                    amount=round(amount, 2),
                    category=category,
                    description=random.choice(desc_list),
                    date=current_date,
                    source=random.choice([TransactionSource.manual, TransactionSource.voice])
                ))

            # 每周生成1-2笔收入
            if i % 7 == 0:
                category, amounts = random.choice(income_categories)
                amount = random.choice(amounts) + random.uniform(-100, 100)
                desc_list = descriptions.get(category, [''])

                transactions.append(Transaction(
                    user_id=user.id,
                    type=TransactionType.income,
                    amount=round(amount, 2),
                    category=category,
                    description=random.choice(desc_list),
                    date=current_date,
                    source=TransactionSource.manual
                ))

        # 批量插入
        db.add_all(transactions)
        db.commit()

        print(f"[OK] Generated {len(transactions)} transactions")

        # 统计
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.income)
        total_expense = sum(t.amount for t in transactions if t.type == TransactionType.expense)

        print(f"\n=== Statistics ===")
        print(f"Total Income:  {total_income:,.2f}")
        print(f"Total Expense: {total_expense:,.2f}")
        print(f"Balance:       {total_income - total_expense:,.2f}")

        print("\n[DONE] Sample data initialized!")

    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    init_data()
