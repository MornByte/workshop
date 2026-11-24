"""成就系统服务 — 负责计算 streak、检查并解锁成就"""

from datetime import datetime, timedelta
from typing import List

from backend.db import connection as db


def compute_streak(user_id: int) -> int:
    """计算用户的连续学习天数（从 daily_stats 记录倒序回溯）。"""
    dates = db.fetchall(
        "SELECT DISTINCT date FROM daily_stats WHERE user_id=? ORDER BY date DESC",
        (user_id,),
    )
    if not dates:
        return 0

    streak = 0
    expected = datetime.now().date()
    for row in dates:
        row_date = datetime.fromisoformat(row["date"]).date() \
            if isinstance(row["date"], str) else row["date"]
        if row_date == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


def check_achievements(user_id: int, score: int) -> List[str]:
    """检查所有成就条件，解锁新成就；返回新解锁的 code 列表。

    调用时机：完成 lesson（带 score）/ 发布社区动态。
    """
    completed = db.fetchone(
        "SELECT COUNT(*) AS c FROM user_progress WHERE user_id=? AND completed=1",
        (user_id,),
    )["c"]

    all_ach = db.fetchall("SELECT * FROM achievements ORDER BY id")
    newly_unlocked: List[str] = []

    for ach in all_ach:
        # 已解锁的跳过
        existing = db.fetchone(
            "SELECT 1 FROM user_achievements WHERE user_id=? AND achievement_id=?",
            (user_id, ach["id"]),
        )
        if existing:
            continue

        unlocked = _evaluate_condition(ach, user_id, completed, score)
        if unlocked:
            db.execute(
                "INSERT INTO user_achievements (user_id, achievement_id) VALUES (?,?)",
                (user_id, ach["id"]),
            )
            newly_unlocked.append(ach["code"])

    return newly_unlocked


def _evaluate_condition(ach: dict, user_id: int, completed: int, score: int) -> bool:
    """单个成就的条件判断。"""
    cond = ach["condition_type"]
    val = ach["condition_value"]

    if cond == "lessons_completed":
        return completed >= val
    if cond == "perfect_score":
        return score >= val
    if cond == "streak_days":
        return compute_streak(user_id) >= val
    if cond == "post_count":
        row = db.fetchone(
            "SELECT COUNT(*) AS c FROM community_posts WHERE user_id=?", (user_id,)
        )
        return row["c"] >= val
    return False
