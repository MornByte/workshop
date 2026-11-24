"""
LinguaHub · 语汇 — 多语种在线教育平台后端
技术栈：FastAPI + SQLite + 原生 JS 前端
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from contextlib import closing
import sqlite3
import hashlib
import secrets
import json
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# ============================================================
# FastAPI 应用初始化
# ============================================================
app = FastAPI(title="LinguaHub API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "linguahub.db"

# 简单 Token 存储（生产环境应换用 JWT + Redis）
active_tokens: Dict[str, str] = {}  # token -> username
security = HTTPBearer(auto_error=False)


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """从请求头取出 Bearer Token，返回用户名；无 Token 则抛 401。"""
    if not credentials or credentials.credentials not in active_tokens:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return active_tokens[credentials.credentials]


def hash_password(password: str) -> str:
    """简单密码哈希（生产环境应使用 bcrypt）。"""
    return hashlib.sha256(password.encode()).hexdigest()


# ============================================================
# 数据库初始化
# ============================================================
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    target_language TEXT DEFAULT 'en',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS languages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,      -- 'en' | 'ja' | 'ko'
    name TEXT NOT NULL,             -- 中文显示名
    native_name TEXT NOT NULL,      -- 母语名称
    flag TEXT,                      -- emoji 国旗
    description TEXT
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language_code TEXT NOT NULL,
    level TEXT NOT NULL,            -- A1 A2 B1 B2 C1
    title TEXT NOT NULL,
    subtitle TEXT,
    icon TEXT,
    color TEXT,
    total_lessons INTEGER DEFAULT 0,
    UNIQUE(language_code, level)
);

CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    lesson_type TEXT NOT NULL,      -- vocab | grammar | speaking | listening
    order_index INTEGER NOT NULL,
    duration_min INTEGER DEFAULT 15,
    content_json TEXT NOT NULL,     -- 题目/对话等内容
    FOREIGN KEY(course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    completed INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    last_accessed TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    condition_type TEXT NOT NULL,   -- lessons_completed | streak_days | score_total | post_count
    condition_value INTEGER NOT NULL,
    reward_points INTEGER DEFAULT 50
);

CREATE TABLE IF NOT EXISTS user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, achievement_id)
);

CREATE TABLE IF NOT EXISTS community_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    likes INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    lessons_completed INTEGER DEFAULT 0,
    minutes_spent INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);
"""


def init_db():
    """初始化数据库表结构并填充种子数据。"""
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.executescript(SCHEMA)

            # === 语种种子 ===
            conn.executemany(
                "INSERT OR IGNORE INTO languages (code, name, native_name, flag, description) VALUES (?,?,?,?,?)",
                [
                    ("en", "英语", "English", "🇬🇧", "全球通用的国际语言，商务与旅行必备"),
                    ("ja", "日语", "日本語", "🇯🇵", "入门友好的亚洲语言，敬语系统独特"),
                    ("ko", "韩语", "한국어", "🇰🇷", "拼音化书写易于上手，潮流文化带动学习需求"),
                ],
            )

            # === 课程种子 ===
            conn.executemany(
                "INSERT OR IGNORE INTO courses (language_code, level, title, subtitle, icon, color, total_lessons) VALUES (?,?,?,?,?,?,?)",
                [
                    ("en", "A1", "英语入门 A1", "日常问候与基础句型", "🌱", "#16c79a", 12),
                    ("en", "B1", "英语进阶 B1", "流利对话与中级语法", "🌿", "#1a9e7f", 12),
                    ("en", "C1", "英语精通 C1", "地道表达与高级词汇", "🌳", "#0f6b54", 12),
                    ("ja", "A1", "日语入门 A1", "五十音与基础寒暄", "🌸", "#f5a623", 12),
                    ("ja", "B1", "日语进阶 B1", "N4-N3 核心语法", "🎎", "#e08e0b", 12),
                    ("ja", "C1", "日语精通 C1", "敬语与地道表达", "🏯", "#a86a00", 12),
                    ("ko", "A1", "韩语入门 A1", "韩文字母与问候", "🥣", "#ff6b6b", 12),
                    ("ko", "B1", "韩语进阶 B1", "中级语法与日常对话", "🍜", "#e04848", 12),
                    ("ko", "C1", "韩语精通 C1", "敬语与文化表达", "🏛️", "#a02828", 12),
                ],
            )

            # === 成就种子 ===
            conn.executemany(
                "INSERT OR IGNORE INTO achievements (code, name, description, icon, condition_type, condition_value, reward_points) VALUES (?,?,?,?,?,?,?)",
                [
                    ("first_step", "迈出第一步", "完成第一课", "🎯", "lessons_completed", 1, 30),
                    ("starter", "初级学员", "完成 5 节课", "📚", "lessons_completed", 5, 60),
                    ("dedicated", "勤勉学者", "完成 20 节课", "🎓", "lessons_completed", 20, 120),
                    ("master", "语言大师", "完成 50 节课", "🏆", "lessons_completed", 50, 250),
                    ("streak3", "三日坚持", "连续学习 3 天", "🔥", "streak_days", 3, 50),
                    ("streak7", "七日魔法", "连续学习 7 天", "⭐", "streak_days", 7, 150),
                    ("streak30", "月度达人", "连续学习 30 天", "💎", "streak_days", 30, 500),
                    ("perfect", "完美主义", "单次课程满分", "💯", "perfect_score", 100, 80),
                    ("community", "社区活跃", "发布 3 条动态", "💬", "post_count", 3, 40),
                ],
            )

            # === 为每门课程生成 12 节 lesson ===
            course_ids = [row[0] for row in conn.execute("SELECT id FROM courses").fetchall()]
            lesson_templates = [
                ("vocab", "核心词汇", 12),
                ("grammar", "语法精讲", 15),
                ("speaking", "口语跟读", 10),
                ("listening", "听力训练", 15),
            ]
            for cid in course_ids:
                existing = conn.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?", (cid,)).fetchone()[0]
                if existing > 0:
                    continue
                idx = 1
                for ltype, label, mins in lesson_templates:
                    for i in range(1, 4):
                        conn.execute(
                            "INSERT INTO lessons (course_id, title, lesson_type, order_index, duration_min, content_json) VALUES (?,?,?,?,?,?)",
                            (cid, f"{label} · 第 {i} 课", ltype, idx, mins, json.dumps(build_lesson_content(ltype, idx))),
                        )
                        idx += 1


def build_lesson_content(lesson_type: str, index: int) -> Dict[str, Any]:
    """根据 lesson_type 生成示例题目 JSON。前端可以替换成真实题目库。"""
    if lesson_type == "vocab":
        words = [
            {"word": "Hello", "translation": "你好", "example": "Hello, nice to meet you."},
            {"word": "Goodbye", "translation": "再见", "example": "Goodbye, see you tomorrow!"},
            {"word": "Thank you", "translation": "谢谢", "example": "Thank you for your help."},
            {"word": "Sorry", "translation": "对不起", "example": "Sorry, I'm late."},
            {"word": "Please", "translation": "请", "example": "Please sit down."},
            {"word": "Yes", "translation": "是的", "example": "Yes, I agree."},
            {"word": "No", "translation": "不", "example": "No, thank you."},
            {"word": "Help", "translation": "帮助", "example": "Can you help me?"},
            {"word": "Love", "translation": "爱", "example": "I love learning languages."},
            {"word": "Study", "translation": "学习", "example": "I study every day."},
        ]
        return {"questions": [{"type": "word-card", **w} for w in words]}

    if lesson_type == "grammar":
        questions = [
            {"type": "fill-blank", "prompt": "I ___ a student.", "options": ["am", "is", "are", "be"], "answer": 0},
            {"type": "fill-blank", "prompt": "She ___ to school every day.", "options": ["go", "goes", "going", "went"], "answer": 1},
            {"type": "fill-blank", "prompt": "They ___ playing football now.", "options": ["is", "are", "was", "were"], "answer": 1},
            {"type": "fill-blank", "prompt": "Yesterday I ___ pizza.", "options": ["eat", "eats", "ate", "eaten"], "answer": 2},
            {"type": "fill-blank", "prompt": "___ you speak English?", "options": ["Do", "Does", "Is", "Can"], "answer": 0},
        ]
        return {"questions": questions}

    if lesson_type == "speaking":
        sentences = [
            {"sentence": "Hello, how are you?", "translation": "你好，最近怎么样？"},
            {"sentence": "I'm fine, thank you.", "translation": "我很好，谢谢。"},
            {"sentence": "What is your name?", "translation": "你叫什么名字？"},
            {"sentence": "My name is Alex.", "translation": "我叫 Alex。"},
            {"sentence": "Where are you from?", "translation": "你来自哪里？"},
        ]
        return {"questions": [{"type": "speaking", **s} for s in sentences]}

    if lesson_type == "listening":
        audios = [
            {"type": "listening", "transcript": "Good morning! How can I help you today?", "q": "说话者在做什么？", "options": ["问候服务", "讲故事", "道歉", "告别"], "answer": 0},
            {"type": "listening", "transcript": "Could you please speak more slowly?", "q": "说话者的请求是？", "options": ["请慢说", "请大声", "请翻译", "请重复"], "answer": 0},
            {"type": "listening", "transcript": "Let's meet at the café at three o'clock.", "q": "约定时间是？", "options": ["三点", "两点", "四点", "不明确"], "answer": 0},
        ]
        return {"questions": audios}

    return {"questions": []}


init_db()

# ============================================================
# Pydantic Schemas
# ============================================================
class RegisterIn(BaseModel):
    username: str = Field(min_length=2, max_length=30)
    password: str = Field(min_length=4)
    email: Optional[str] = None
    target_language: Optional[str] = "en"


class LoginIn(BaseModel):
    username: str
    password: str


class CompleteLessonIn(BaseModel):
    lesson_id: int
    score: int = 0
    minutes_spent: int = 15


class PostIn(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    category: Optional[str] = "general"


class RecommendIn(BaseModel):
    language_code: str


# ============================================================
# 工具函数
# ============================================================
def fetchone(query: str, args=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, args).fetchone()


def fetchall(query: str, args=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(query, args).fetchall()]


def execute(query: str, args=()):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            return conn.execute(query, args).lastrowid


# ============================================================
# 认证 API
# ============================================================
@app.post("/api/auth/register")
def register(data: RegisterIn):
    existing = fetchone("SELECT id FROM users WHERE username=?", (data.username,))
    if existing:
        raise HTTPException(400, "用户名已被注册")
    execute(
        "INSERT INTO users (username, password_hash, email, target_language) VALUES (?,?,?,?)",
        (data.username, hash_password(data.password), data.email, data.target_language),
    )
    return {"ok": True, "message": "注册成功"}


@app.post("/api/auth/login")
def login(data: LoginIn):
    user = fetchone("SELECT id, username, password_hash, target_language FROM users WHERE username=?", (data.username,))
    if not user or user["password_hash"] != hash_password(data.password):
        raise HTTPException(401, "用户名或密码错误")
    token = secrets.token_hex(24)
    active_tokens[token] = user["username"]
    return {
        "ok": True,
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "target_language": user["target_language"],
        },
    }


@app.post("/api/auth/logout")
def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if credentials and credentials.credentials in active_tokens:
        del active_tokens[credentials.credentials]
    return {"ok": True}


@app.get("/api/auth/me")
def me(username: str = Depends(get_current_user)):
    row = fetchone("SELECT id, username, email, target_language, created_at FROM users WHERE username=?", (username,))
    if not row:
        raise HTTPException(404, "用户不存在")
    progress = fetchall(
        """SELECT COUNT(*) AS c, COALESCE(SUM(score),0) AS total_score 
           FROM user_progress WHERE user_id=? AND completed=1""",
        (row["id"],),
    )
    achievements = fetchall(
        """SELECT a.* FROM achievements a 
           JOIN user_achievements ua ON ua.achievement_id=a.id 
           WHERE ua.user_id=?""",
        (row["id"],),
    )
    return {
        "user": dict(row),
        "stats": {
            "completed_lessons": progress[0]["c"] if progress else 0,
            "total_score": progress[0]["total_score"] if progress else 0,
            "achievements_count": len(achievements),
        },
    }


# ============================================================
# 语言 / 课程 API
# ============================================================
@app.get("/api/languages")
def list_languages():
    return fetchall("SELECT * FROM languages ORDER BY id")


@app.get("/api/courses")
def list_courses(language: str = None):
    sql = "SELECT * FROM courses"
    args = ()
    if language:
        sql += " WHERE language_code=?"
        args = (language,)
    sql += " ORDER BY language_code, level"
    return fetchall(sql, args)


@app.get("/api/courses/{course_id}")
def get_course(course_id: int, username: str = Depends(get_current_user)):
    course = fetchone("SELECT * FROM courses WHERE id=?", (course_id,))
    if not course:
        raise HTTPException(404, "课程不存在")
    user = fetchone("SELECT id FROM users WHERE username=?", (username,))
    lessons = fetchall(
        """SELECT l.*, 
                  COALESCE(up.completed,0) AS completed, 
                  COALESCE(up.score,0) AS score,
                  up.last_accessed
           FROM lessons l
           LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=?
           WHERE l.course_id=?
           ORDER BY l.order_index""",
        (user["id"], course_id),
    )
    return {"course": dict(course), "lessons": lessons}


@app.get("/api/lessons/{lesson_id}")
def get_lesson(lesson_id: int, username: str = Depends(get_current_user)):
    lesson = fetchone("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    if not lesson:
        raise HTTPException(404, "课时不存在")
    content = json.loads(lesson["content_json"])
    return {"lesson": {k: v for k, v in dict(lesson).items() if k != "content_json"}, "content": content}


@app.post("/api/lessons/{lesson_id}/complete")
def complete_lesson(lesson_id: int, data: CompleteLessonIn, username: str = Depends(get_current_user)):
    user = fetchone("SELECT id FROM users WHERE username=?", (username,))
    lesson = fetchone("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    if not lesson:
        raise HTTPException(404, "课时不存在")

    progress = fetchone("SELECT * FROM user_progress WHERE user_id=? AND lesson_id=?", (user["id"], lesson_id))
    if progress:
        execute(
            "UPDATE user_progress SET completed=1, score=?, attempts=attempts+1, last_accessed=CURRENT_TIMESTAMP WHERE id=?",
            (data.score, progress["id"]),
        )
    else:
        execute(
            "INSERT INTO user_progress (user_id, lesson_id, completed, score, attempts) VALUES (?,?,1,?,1)",
            (user["id"], lesson_id, data.score),
        )

    # 更新今日学习时长
    today = datetime.now().date().isoformat()
    stat = fetchone("SELECT id FROM daily_stats WHERE user_id=? AND date=?", (user["id"], today))
    if stat:
        execute(
            "UPDATE daily_stats SET lessons_completed=lessons_completed+1, minutes_spent=minutes_spent+? WHERE id=?",
            (data.minutes_spent, stat["id"]),
        )
    else:
        execute(
            "INSERT INTO daily_stats (user_id, date, lessons_completed, minutes_spent) VALUES (?,?,1,?)",
            (user["id"], today, data.minutes_spent),
        )

    # 检查成就
    check_achievements(user["id"], data.score)

    return {"ok": True, "score": data.score}


# ============================================================
# 成就检查
# ============================================================
def check_achievements(user_id: int, score: int):
    completed = fetchone(
        "SELECT COUNT(*) AS c FROM user_progress WHERE user_id=? AND completed=1",
        (user_id,),
    )["c"]
    all_achievements = fetchall("SELECT * FROM achievements")

    for ach in all_achievements:
        # 已解锁的跳过
        unlocked = fetchone(
            "SELECT 1 FROM user_achievements WHERE user_id=? AND achievement_id=?",
            (user_id, ach["id"]),
        )
        if unlocked:
            continue

        ok = False
        cond = ach["condition_type"]
        val = ach["condition_value"]

        if cond == "lessons_completed" and completed >= val:
            ok = True
        elif cond == "perfect_score" and score >= val:
            ok = True
        elif cond == "streak_days":
            streak = compute_streak(user_id)
            if streak >= val:
                ok = True
        elif cond == "post_count":
            cnt = fetchone("SELECT COUNT(*) AS c FROM community_posts WHERE user_id=?", (user_id,))["c"]
            if cnt >= val:
                ok = True

        if ok:
            execute(
                "INSERT INTO user_achievements (user_id, achievement_id) VALUES (?,?)",
                (user_id, ach["id"]),
            )


def compute_streak(user_id: int) -> int:
    dates = fetchall(
        "SELECT DISTINCT date FROM daily_stats WHERE user_id=? ORDER BY date DESC",
        (user_id,),
    )
    if not dates:
        return 0
    streak = 0
    today = datetime.now().date()
    expected = today
    for d in dates:
        if d["date"] == expected.isoformat():
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


# ============================================================
# 进度 & 成就 API
# ============================================================
@app.get("/api/progress")
def get_progress(language: str = None, username: str = Depends(get_current_user)):
    user = fetchone("SELECT id FROM users WHERE username=?", (username,))
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
    courses = fetchall(sql, args)

    # 计算总体进度
    overall_total = sum(c["total_lessons"] for c in courses)
    overall_done = sum(c["completed_lessons"] for c in courses)
    streak = compute_streak(user["id"])

    return {
        "courses": courses,
        "overall": {"total": overall_total, "completed": overall_done, "percent": round(overall_done / overall_total * 100, 1) if overall_total else 0},
        "streak_days": streak,
    }


@app.get("/api/achievements")
def get_achievements(username: str = Depends(get_current_user)):
    user = fetchone("SELECT id FROM users WHERE username=?", (username,))
    all_ach = fetchall("SELECT * FROM achievements ORDER BY id")
    unlocked_ids = {r["achievement_id"] for r in fetchall(
        "SELECT achievement_id FROM user_achievements WHERE user_id=?", (user["id"],)
    )}
    for a in all_ach:
        a["unlocked"] = a["id"] in unlocked_ids
    return all_ach


# ============================================================
# 个性化推荐
# ============================================================
@app.post("/api/recommend")
def recommend(data: RecommendIn, username: str = Depends(get_current_user)):
    """根据目标语言和当前进度，推荐下一步应该学习的 lesson。"""
    user = fetchone("SELECT id FROM users WHERE username=?", (username,))
    language = data.language_code

    # 找出该语言下所有课程的未完成 lesson，取 order_index 最小的
    rows = fetchall(
        """SELECT l.*, c.level, c.title AS course_title
           FROM lessons l
           JOIN courses c ON c.id=l.course_id AND c.language_code=?
           LEFT JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=?
           WHERE up.completed IS NULL OR up.completed=0
           ORDER BY l.order_index
           LIMIT 1""",
        (language, user["id"]),
    )
    if not rows:
        return {"message": "太棒了！该语言下你已完成所有课程 🎉", "next": None}

    # 同时推荐一个复习 lesson（进度最低或分数最低的已完成 lesson）
    review = fetchall(
        """SELECT l.*, c.level, c.title AS course_title, up.score, up.attempts
           FROM lessons l
           JOIN courses c ON c.id=l.course_id AND c.language_code=?
           JOIN user_progress up ON up.lesson_id=l.id AND up.user_id=? AND up.completed=1
           ORDER BY up.score ASC
           LIMIT 1""",
        (language, user["id"]),
    )
    return {
        "next": rows[0],
        "review": review[0] if review else None,
        "message": "基于你的进度，这里是我们推荐的下一步练习",
    }


# ============================================================
# 社区 API
# ============================================================
@app.get("/api/community")
def list_posts(limit: int = 20):
    posts = fetchall(
        """SELECT p.*, u.username, u.target_language
           FROM community_posts p
           JOIN users u ON u.id=p.user_id
           ORDER BY p.created_at DESC LIMIT ?""",
        (limit,),
    )
    return posts


@app.post("/api/community")
def create_post(data: PostIn, username: str = Depends(get_current_user)):
    user = fetchone("SELECT id FROM users WHERE username=?", (username,))
    pid = execute(
        "INSERT INTO community_posts (user_id, content, category) VALUES (?,?,?)",
        (user["id"], data.content, data.category),
    )
    # 检查成就
    check_achievements(user["id"], 0)
    return {"id": pid, "ok": True}


@app.post("/api/community/{post_id}/like")
def like_post(post_id: int):
    execute("UPDATE community_posts SET likes=likes+1 WHERE id=?", (post_id,))
    return {"ok": True}


# ============================================================
# 仪表盘概览
# ============================================================
@app.get("/api/dashboard")
def dashboard(username: str = Depends(get_current_user)):
    user = fetchone("SELECT id, username, target_language FROM users WHERE username=?", (username,))
    language = user["target_language"]

    progress = get_progress(language, username)
    achievements = get_achievements(username)
    unlocked_count = sum(1 for a in achievements if a["unlocked"])
    rec = recommend(RecommendIn(language_code=language), username)
    recent_posts = fetchall(
        """SELECT p.*, u.username FROM community_posts p 
           JOIN users u ON u.id=p.user_id 
           ORDER BY p.created_at DESC LIMIT 5"""
    )
    streak = compute_streak(user["id"])

    return {
        "user": dict(user),
        "progress": progress,
        "achievements": {"unlocked": unlocked_count, "total": len(achievements), "list": achievements},
        "recommend": rec,
        "streak_days": streak,
        "recent_posts": recent_posts,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
