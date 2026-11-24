"""认证核心 — 密码哈希 + Token 签发/存储

⚠️ 演示级实现：SHA-256 + 内存 dict Token
生产升级路线：
    密码 → bcrypt / argon2
    Token → JWT（无状态签名）或 Redis（带 TTL 的 Session）
"""

import hashlib
import secrets
from typing import Dict

from backend.config import TOKEN_BYTES, PASSWORD_HASH_ALGO

# 全局 Token → username 映射
# 进程重启即清空；如需持久化请迁移 Redis
active_tokens: Dict[str, str] = {}


def hash_password(password: str) -> str:
    """对明文密码做单向哈希。"""
    if PASSWORD_HASH_ALGO == "sha256":
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
    # 预留 bcrypt 扩展点
    raise ValueError(f"未知哈希算法: {PASSWORD_HASH_ALGO}")


def verify_password(password: str, password_hash: str) -> bool:
    """校验密码（当前为比较哈希值）。"""
    return hash_password(password) == password_hash


def issue_token(username: str) -> str:
    """签发一个新的 Bearer Token 并绑定到 username。"""
    token = secrets.token_hex(TOKEN_BYTES)
    active_tokens[token] = username
    return token


def revoke_token(token: str) -> None:
    """使指定 Token 失效（登出）。"""
    active_tokens.pop(token, None)


def resolve_token(token: str) -> str | None:
    """Token → username；无效 Token 返回 None。"""
    return active_tokens.get(token)
