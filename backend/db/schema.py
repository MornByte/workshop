"""数据库 DDL、种子数据与初始化逻辑 — 应用启动时自动建表并填充示例数据"""

import json

from backend.db import connection as db
from backend.db.content_generator import build_lesson_content


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
    name TEXT NOT NULL,
    native_name TEXT NOT NULL,
    flag TEXT,
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
    content_json TEXT NOT NULL,
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
    condition_type TEXT NOT NULL,
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

# ---------- 种子数据 ----------

LANG_SEEDS = [
    ("en", "英语", "English", "🇬🇧", "全球通用的国际语言，商务与旅行必备"),
    ("ja", "日语", "日本語", "🇯🇵", "入门友好的亚洲语言，敬语系统独特"),
    ("ko", "韩语", "한국어", "🇰🇷", "拼音化书写易于上手，潮流文化带动学习需求"),
]

COURSE_SEEDS = [
    ("en", "A1", "英语入门 A1", "日常问候与基础句型", "🌱", "#16c79a", 12),
    ("en", "B1", "英语进阶 B1", "流利对话与中级语法", "🌿", "#1a9e7f", 12),
    ("en", "C1", "英语精通 C1", "地道表达与高级词汇", "🌳", "#0f6b54", 12),
    ("ja", "A1", "日语入门 A1", "五十音与基础寒暄", "🌸", "#f5a623", 12),
    ("ja", "B1", "日语进阶 B1", "N4-N3 核心语法", "🎎", "#e08e0b", 12),
    ("ja", "C1", "日语精通 C1", "敬语与地道表达", "🏯", "#a86a00", 12),
    ("ko", "A1", "韩语入门 A1", "韩文字母与问候", "🥣", "#ff6b6b", 12),
    ("ko", "B1", "韩语进阶 B1", "中级语法与日常对话", "🍜", "#e04848", 12),
    ("ko", "C1", "韩语精通 C1", "敬语与文化表达", "🏛️", "#a02828", 12),
]

ACHIEVEMENT_SEEDS = [
    ("first_step", "迈出第一步", "完成第一课", "🎯", "lessons_completed", 1, 30),
    ("starter", "初级学员", "完成 5 节课", "📚", "lessons_completed", 5, 60),
    ("dedicated", "勤勉学者", "完成 20 节课", "🎓", "lessons_completed", 20, 120),
    ("master", "语言大师", "完成 50 节课", "🏆", "lessons_completed", 50, 250),
    ("streak3", "三日坚持", "连续学习 3 天", "🔥", "streak_days", 3, 50),
    ("streak7", "七日魔法", "连续学习 7 天", "⭐", "streak_days", 7, 150),
    ("streak30", "月度达人", "连续学习 30 天", "💎", "streak_days", 30, 500),
    ("perfect", "完美主义", "单次课程满分", "💯", "perfect_score", 100, 80),
    ("community", "社区活跃", "发布 3 条动态", "💬", "post_count", 3, 40),
]


def init_db() -> None:
    """应用启动时调用：建表 + 填充种子数据（幂等，重启不重复）。"""
    # 先执行 DDL
    with db._connect() as conn:  # 内部直接用连接（需要事务包装）
        with conn:
            conn.executescript(SCHEMA)

            db.execute_many(
                "INSERT OR IGNORE INTO languages "
                "(code, name, native_name, flag, description) VALUES (?,?,?,?,?)",
                LANG_SEEDS,
            )

            db.execute_many(
                "INSERT OR IGNORE INTO courses "
                "(language_code, level, title, subtitle, icon, color, total_lessons) VALUES (?,?,?,?,?,?,?)",
                COURSE_SEEDS,
            )

            db.execute_many(
                "INSERT OR IGNORE INTO achievements "
                "(code, name, description, icon, condition_type, condition_value, reward_points) VALUES (?,?,?,?,?,?,?)",
                ACHIEVEMENT_SEEDS,
            )

            # 为每门课程生成 12 节课时
            course_ids = [row[0] for row in conn.execute("SELECT id FROM courses").fetchall()]
            lesson_templates = [
                ("vocab", "核心词汇", 12),
                ("grammar", "语法精讲", 15),
                ("speaking", "口语跟读", 10),
                ("listening", "听力训练", 15),
            ]
            for cid in course_ids:
                existing = conn.execute(
                    "SELECT COUNT(*) FROM lessons WHERE course_id=?", (cid,)
                ).fetchone()[0]
                if existing > 0:
                    continue
                idx = 1
                for ltype, label, mins in lesson_templates:
                    for i in range(1, 4):
                        conn.execute(
                            "INSERT INTO lessons "
                            "(course_id, title, lesson_type, order_index, duration_min, content_json) "
                            "VALUES (?,?,?,?,?,?)",
                            (cid, f"{label} · 第 {i} 课", ltype, idx, mins,
                             json.dumps(build_lesson_content(ltype, idx))),
                        )
                        idx += 1


def reset_db() -> None:
    """⚠️ 开发用 — 清空所有数据并重建 schema。"""
    from backend.config import DB_PATH
    import os
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
