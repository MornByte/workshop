"""认证相关路由组 — /api/auth/*"""

from fastapi import APIRouter, Depends, HTTPException

from backend.core import security as auth
from backend.db import connection as db
from backend.core.deps import get_current_user
from backend.schemas.requests import RegisterIn, LoginIn

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register")
def register(data: RegisterIn):
    existing = db.fetchone("SELECT id FROM users WHERE username=?", (data.username,))
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    db.execute(
        "INSERT INTO users (username, password_hash, email, target_language) "
        "VALUES (?,?,?,?)",
        (
            data.username,
            auth.hash_password(data.password),
            data.email,
            data.target_language,
        ),
    )
    return {"ok": True, "message": "注册成功"}


@router.post("/login")
def login(data: LoginIn):
    user = db.fetchone(
        "SELECT id, username, password_hash, target_language FROM users WHERE username=?",
        (data.username,),
    )
    if not user or not auth.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = auth.issue_token(user["username"])
    return {
        "ok": True,
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "target_language": user["target_language"],
        },
    }


@router.post("/logout")
def logout(username: str = Depends(get_current_user)):
    """Token 已在 get_current_user 中校验；登出时从内存存储移除。"""
    from backend.core import security
    # 遍历找到对应 token 并删除（演示实现，生产应 Redis）
    for token, uname in list(security.active_tokens.items()):
        if uname == username:
            security.revoke_token(token)
    return {"ok": True}


@router.get("/me")
def me(username: str = Depends(get_current_user)):
    user = db.fetchone(
        "SELECT id, username, email, target_language, created_at FROM users WHERE username=?",
        (username,),
    )
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    progress = db.fetchall(
        """SELECT COUNT(*) AS c, COALESCE(SUM(score),0) AS total_score
           FROM user_progress WHERE user_id=? AND completed=1""",
        (user["id"],),
    )
    ach_rows = db.fetchall(
        """SELECT a.* FROM achievements a
           JOIN user_achievements ua ON ua.achievement_id=a.id
           WHERE ua.user_id=?""",
        (user["id"],),
    )
    return {
        "user": dict(user),
        "stats": {
            "completed_lessons": progress[0]["c"] if progress else 0,
            "total_score": progress[0]["total_score"] if progress else 0,
            "achievements_count": len(ach_rows),
        },
    }
