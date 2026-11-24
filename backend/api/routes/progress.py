"""进度 + 成就路由组 — /api/progress + /api/achievements"""

from fastapi import APIRouter, Depends, Query

from backend.db import connection as db
from backend.core.deps import get_current_user
from backend.core.achievements import compute_streak

router = APIRouter(tags=["进度与成就"])


@router.get("/api/progress")
def get_progress(
    language: str | None = Query(default=None),
    username: str = Depends(get_current_user),
):
    user = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
    sql = """SELECT c.*,
                    COUNT(l.id) AS total_lessons,
                    SUM(CASE WHEN up.completed=1 THEN 1 ELSE 0 END) AS completed_lessons
             FROM courses c
             JOIN lessons l ON l.course_id=c.id
             LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=? """
    args = [user["id"]]
    if language:
        sql += " WHERE c.language_code=?"
        args.append(language)
    sql += " GROUP BY c.id ORDER BY c.language_code, c.level"

    courses = db.fetchall(sql, args)
    overall_total = sum(c["total_lessons"] for c in courses)
    overall_done = sum(c["completed_lessons"] for c in courses)

    return {
        "courses": courses,
        "overall": {
            "total": overall_total,
            "completed": overall_done,
            "percent": round(overall_done / overall_total * 100, 1)
            if overall_total else 0,
        },
        "streak_days": compute_streak(user["id"]),
    }


@router.get("/api/achievements")
def get_achievements(username: str = Depends(get_current_user)):
    user = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
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
    return all_ach
