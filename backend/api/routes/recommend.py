"""个性化推荐路由组 — /api/recommend"""

from fastapi import APIRouter, Depends

from backend.db import connection as db
from backend.core.deps import get_current_user
from backend.schemas.requests import RecommendIn

router = APIRouter(prefix="/api/recommend", tags=["个性化推荐"])


@router.post("")
def recommend(data: RecommendIn, username: str = Depends(get_current_user)):
    """基于未完成进度推荐下一课 + 基于最低分推荐薄弱复习课。"""
    user = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
    language = data.language_code

    # 下一课：该语言下第一个未完成 lesson
    next_rows = db.fetchall(
        """SELECT l.*, c.level, c.title AS course_title
           FROM lessons l
           JOIN courses c ON c.id=l.course_id AND c.language_code=?
           LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=?
           WHERE up.completed IS NULL OR up.completed=0
           ORDER BY l.order_index
           LIMIT 1""",
        (language, user["id"]),
    )
    if not next_rows:
        return {
            "message": "太棒了！该语言下你已完成所有课程 🎉",
            "next": None,
            "review": None,
        }

    # 薄弱复习课：已完成课时中分数最低的
    review_rows = db.fetchall(
        """SELECT l.*, c.level, c.title AS course_title, up.score, up.attempts
           FROM lessons l
           JOIN courses c ON c.id=l.course_id AND c.language_code=?
           JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=? AND up.completed=1
           ORDER BY up.score ASC
           LIMIT 1""",
        (language, user["id"]),
    )

    return {
        "next": next_rows[0],
        "review": review_rows[0] if review_rows else None,
        "message": "基于你的进度，这里是我们推荐的下一步练习",
    }
