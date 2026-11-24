"""应用全局配置 — 单一事实源"""

import os

# ---------- 路径 ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "linguahub.db")

# ---------- 运行 ----------
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# ---------- 安全 ----------
# 当前为演示级别的简单哈希 + 内存 Token 存储
# 生产应升级：bcrypt / JWT + Redis
PASSWORD_HASH_ALGO = "sha256"
TOKEN_BYTES = 24  # secrets.token_hex 入参

# ---------- CORS ----------
# 开发期全部放开；生产需改为具体域名白名单
CORS_ORIGINS = ["*"]
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# ---------- 成就系统常量 ----------
# condition_type 枚举
COND_TYPE_LESSONS_COMPLETED = "lessons_completed"
COND_TYPE_STREAK_DAYS = "streak_days"
COND_TYPE_PERFECT_SCORE = "perfect_score"
COND_TYPE_POST_COUNT = "post_count"

# ---------- 课程常量 ----------
LESSON_TYPES = ("vocab", "grammar", "speaking", "listening")
LANGUAGE_CODES = ("en", "ja", "ko")
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
