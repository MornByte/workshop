"""语言 + 课程相关路由组 — /api/languages + /api/courses/*"""

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import connection as db
from backend.core.deps import get_current_user

router = APIRouter(tags=["语言与课程"])


@router.get("/api/languages")
def list_languages():
    return db.fetchall("SELECT * FROM languages ORDER BY id")


@router.get("/api/courses")
def list_courses(language: str | None = Query(default=None)):
    sql = "SELECT * FROM courses"
    args = ()
    if language:
        sql += " WHERE language_code=?"
        args = (language,)
    sql += " ORDER BY language_code, level"
    return db.fetchall(sql, args)


@router.get("/api/courses/{course_id}")
def get_course(course_id: int, username: str = Depends(get_current_user)):
    course = db.fetchone("SELECT * FROM courses WHERE id=?", (course_id,))
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    user = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
    lessons = db.fetchall(
        """SELECT l.*,
                  COALESCE(up.completed, 0) AS completed,
                  COALESCE(up.score, 0) AS score,
                  up.last_accessed
           FROM lessons l
           LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=?
           WHERE l.course_id=?
           ORDER BY l.order_index""",
        (user["id"], course_id),
    )
    return {"course": dict(course), "lessons": lessons}
