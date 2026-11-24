"""仪表盘聚合路由 — /api/dashboard（一站式概览）"""

from fastapi import APIRouter, Depends

from backend.db import connection as db
from backend.core.deps import get_current_user
from backend.core.achievements import compute_streak

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("")
def dashboard(username: str = Depends(get_current_user)):
    """聚合多个子 API 结果，减少前端请求次数。"""
    user = db.fetchone(
        "SELECT id, username, target_language FROM users WHERE username=?",
        (username,),
    )

    language = user["target_language"]

    # 1. 进度（复用 progress 路由的核心 SQL）
    sql = """SELECT c.*,
                    COUNT(l.id) AS total_lessons,
                    SUM(CASE WHEN up.completed=1 THEN 1 ELSE 0 END) AS completed_lessons
             FROM courses c
             JOIN lessons l ON l.course_id=c.id
             LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=?
             WHERE c.language_code=?
             GROUP BY c.id ORDER BY c.level"""
    courses = db.fetchall(sql, (user["id"], language))
    overall_total = sum(c["total_lessons"] for c in courses)
    overall_done = sum(c["completed_lessons"] for c in courses)

    progress = {
        "courses": courses,
        "overall": {
            "total": overall_total,
            "completed": overall_done,
            "percent": round(overall_done / overall_total * 100, 1)
            if overall_total else 0,
        },
        "streak_days": compute_streak(user["id"]),
    }

    # 2. 成就
    all_ach = db.fetchall("SELECT * FROM achievements ORDER BY id")
    unlocked_ids = {
        r["achievement_id"]
        for r in db.fetchall(
            "SELECT achievement_id FROM user_achievements WHERE user_id=?",
            (user["id"],),
        )
    }
    for a in all_ach:
        a["unlocked"] = a["id"] in unlocked_ids

    achievements = {
        "unlocked": len(unlocked_ids),
        "total": len(all_ach),
        "list": all_ach,
    }

    # 3. 推荐（下一课 + 薄弱复习）
    next_rows = db.fetchall(
        """SELECT l.*, c.level, c.title AS course_title
           FROM lessons l
           JOIN courses c ON c.id=l.course_id AND c.language_code=?
           LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=?
           WHERE up.completed IS NULL OR up.completed=0
           ORDER BY l.order_index LIMIT 1""",
        (language, user["id"]),
    )
    review_rows = db.fetchall(
        """SELECT l.*, c.level, c.title AS course_title, up.score, up.attempts
           FROM lessons l
           JOIN courses c ON c.id=l.course_id AND c.language_code=?
           JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=? AND up.completed=1
           ORDER BY up.score ASC LIMIT 1""",
        (language, user["id"]),
    )
    recommend = {
        "next": next_rows[0] if next_rows else None,
        "review": review_rows[0] if review_rows else None,
    }

    # 4. 最近社区动态（5 条）
    recent_posts = db.fetchall(
        """SELECT p.*, u.username
           FROM community_posts p JOIN users u ON u.id=p.user_id
           ORDER BY p.created_at DESC LIMIT 5"""
    )

    return {
        "user": dict(user),
        "progress": progress,
        "achievements": achievements,
        "recommend": recommend,
        "streak_days": progress["streak_days"],
        "recent_posts": recent_posts,
    }
