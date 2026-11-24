"""数据库连接与查询工具函数 — 所有模块共享的低层 DB 接口"""

import sqlite3
from contextlib import closing
from typing import Any, List, Tuple

from backend.config import DB_PATH


def _connect() -> sqlite3.Connection:
    """打开一条 SQLite 连接，启用 Row 工厂方便 dict 访问。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetchone(query: str, args: Tuple = ()) -> dict | None:
    """执行查询并返回单行 dict；无结果返回 None。"""
    with closing(_connect()) as conn:
        row = conn.execute(query, args).fetchone()
        return dict(row) if row else None


def fetchall(query: str, args: Tuple = ()) -> List[dict]:
    """执行查询并返回多行 dict 列表。"""
    with closing(_connect()) as conn:
        return [dict(r) for r in conn.execute(query, args).fetchall()]


def execute(query: str, args: Tuple = ()) -> int:
    """执行写操作（INSERT / UPDATE / DELETE）并返回 lastrowid。"""
    with closing(_connect()) as conn:
        with conn:
            return conn.execute(query, args).lastrowid


def execute_many(query: str, rows: List[Tuple]) -> None:
    """批量执行写操作（在同一事务内）。"""
    with closing(_connect()) as conn:
        with conn:
            conn.executemany(query, rows)


def vacuum() -> None:
    """压缩数据库文件（清理碎片化）。"""
    with closing(_connect()) as conn:
        conn.execute("VACUUM")
