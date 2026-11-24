"""路由聚合 — 所有子 router 集中注册在这里

main.py 只需要 `app.include_router(router)` 一行。
"""

from fastapi import APIRouter

from backend.api.routes.auth import router as auth_router
from backend.api.routes.courses import router as courses_router
from backend.api.routes.lessons import router as lessons_router
from backend.api.routes.progress import router as progress_router
from backend.api.routes.recommend import router as recommend_router
from backend.api.routes.community import router as community_router
from backend.api.routes.dashboard import router as dashboard_router

router = APIRouter()

# 按模块注册（路由自身已带 prefix，此处不再重复）
router.include_router(auth_router)
router.include_router(courses_router)
router.include_router(lessons_router)
router.include_router(progress_router)
router.include_router(recommend_router)
router.include_router(community_router)
router.include_router(dashboard_router)
