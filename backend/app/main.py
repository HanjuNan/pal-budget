from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import transactions, statistics, ai, user
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="可爱记账 API",
    description="一个可爱的记账应用后端服务",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["交易"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["统计"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI服务"])


@app.get("/")
async def root():
    return {"message": "欢迎使用可爱记账 API 🐷"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
