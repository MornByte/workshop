"""LinguaHub · 语汇 — 多语种在线教育平台

FastAPI 后端入口。模块化结构：
  backend/config.py              — 全局配置
  backend/db/                    — 数据库层（连接/DDL/内容生成）
  backend/core/                  — 核心（安全/依赖/成就服务）
  backend/schemas/               — Pydantic 模型
  backend/api/routes/            — 按业务模块拆分的路由
  backend/api/router.py          — 路由聚合
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import CORS_ORIGINS, CORS_METHODS, CORS_HEADERS
from backend.db.schema import init_db
from backend.api.router import router

# ---------- FastAPI 应用 ----------
app = FastAPI(
    title="LinguaHub API",
    description="沉浸式多语种在线教育平台 — 英语 / 日语 / 韩语",
    version="3.0.0",
)

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)

# ---------- 启动钩子：建表 + 填充种子 ----------
@app.on_event("startup")
def on_startup():
    init_db()


# ---------- 注册全部路由 ----------
app.include_router(router)


# ---------- 便捷启动 ----------
if __name__ == "__main__":
    import uvicorn
    from backend.config import HOST, PORT
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
