"""课时 + 完成提交路由组 — /api/lessons/*"""

import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from backend.db import connection as db
from backend.core.deps import get_current_user
from backend.core.achievements import check_achievements
from backend.schemas.requests import CompleteLessonIn

router = APIRouter(prefix="/api/lessons", tags=["课时"])


@router.get("/{lesson_id}")
def get_lesson(lesson_id: int, username: str = Depends(get_current_user)):
    lesson = db.fetchone("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    if not lesson:
        raise HTTPException(status_code=404, detail="课时不存在")

    content = json.loads(lesson["content_json"])
    return {
        "lesson": {k: v for k, v in dict(lesson).items() if k != "content_json"},
        "content": content,
    }


@router.post("/{lesson_id}/complete")
def complete_lesson(
    lesson_id: int,
    data: CompleteLessonIn,
    username: str = Depends(get_current_user),
):
    user = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
    lesson = db.fetchone("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    if not lesson:
        raise HTTPException(status_code=404, detail="课时不存在")

    # 1. UPSERT user_progress
    existing = db.fetchone(
        "SELECT id FROM user_progress WHERE user_id=? AND lesson_id=?",
        (user["id"], lesson_id),
    )
    if existing:
        db.execute(
            "UPDATE user_progress SET completed=1, score=?, attempts=attempts+1, "
            "last_accessed=CURRENT_TIMESTAMP WHERE id=?",
            (data.score, existing["id"]),
        )
    else:
        db.execute(
            "INSERT INTO user_progress (user_id, lesson_id, completed, score, attempts) "
            "VALUES (?,?,1,?,1)",
            (user["id"], lesson_id, data.score),
        )

    # 2. UPSERT daily_stats（今日）
    today = datetime.now().date().isoformat()
    stat = db.fetchone(
        "SELECT id FROM daily_stats WHERE user_id=? AND date=?", (user["id"], today)
    )
    if stat:
        db.execute(
            "UPDATE daily_stats SET lessons_completed=lessons_completed+1, "
            "minutes_spent=minutes_spent+? WHERE id=?",
            (data.minutes_spent, stat["id"]),
        )
    else:
        db.execute(
            "INSERT INTO daily_stats (user_id, date, lessons_completed, minutes_spent) "
            "VALUES (?,?,1,?)",
            (user["id"], today, data.minutes_spent),
        )

    # 3. 成就检查
    newly_unlocked = check_achievements(user["id"], data.score)

    return {
        "ok": True,
        "score": data.score,
        "newly_unlocked": newly_unlocked,
    }
