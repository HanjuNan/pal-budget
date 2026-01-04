from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.routers import transactions, statistics, ai, user
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="可爱记账 API",
    description="一个可爱的记账应用后端服务",
    version="1.0.0"
)


# 禁用缓存中间件
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response


app.add_middleware(NoCacheMiddleware)

# CORS 配置 - 允许所有来源以支持移动端和云端部署
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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
