"""社区交流路由组 — /api/community/*"""

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.db import connection as db
from backend.core.deps import get_current_user
from backend.core.achievements import check_achievements
from backend.schemas.requests import PostIn

router = APIRouter(prefix="/api/community", tags=["社区"])


@router.get("")
def list_posts(limit: int = Query(default=20)):
    return db.fetchall(
        """SELECT p.*, u.username, u.target_language
           FROM community_posts p
           JOIN users u ON u.id=p.user_id
           ORDER BY p.created_at DESC LIMIT ?""",
        (limit,),
    )


@router.post("")
def create_post(data: PostIn, username: str = Depends(get_current_user)):
    user = db.fetchone("SELECT id FROM users WHERE username=?", (username,))
    pid = db.execute(
        "INSERT INTO community_posts (user_id, content, category) VALUES (?,?,?)",
        (user["id"], data.content, data.category),
    )
    # 发帖后检查 community 类成就
    check_achievements(user["id"], score=0)
    return {"id": pid, "ok": True}


@router.post("/{post_id}/like")
def like_post(post_id: int):
    db.execute(
        "UPDATE community_posts SET likes=likes+1 WHERE id=?", (post_id,)
    )
    return {"ok": True}
