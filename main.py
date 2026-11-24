# 引入 FastAPI 框架，用来快速搭建 Web API
# HTTPException 用来在接口出错时返回指定的状态码（比如删除不存在的留言返回 404）
from fastapi import FastAPI, HTTPException
# 引入 BaseModel，用来定义数据的结构（比如一条留言长什么样）
# Field 用来给字段加限制（长度、数值范围）；field_validator 用来写自定义检查
from pydantic import BaseModel, Field, field_validator
# 引入 CORS 中间件，用来允许前端页面跨域调用本接口
from fastapi.middleware.cors import CORSMiddleware
# sqlite3 是 Python 自带的工具，不需要 pip install，也不需要装额外软件
import sqlite3
# closing 用来配合 with 语句，保证数据库连接无论是否出错都会被关闭
from contextlib import closing

# 创建一个 FastAPI 应用实例，整个后端服务都围绕它来写
app = FastAPI()

# 配置跨域允许：
# 直接用浏览器打开 index.html（地址是 file:// 开头）时，
# 它去请求 http://localhost:8000 会被浏览器当成"跨域"而拦截。
# 加上这个中间件后，后端在响应头里声明"允许任何网页来调用我"，
# 浏览器就不会拦截了。（学习项目可以直接放开所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 允许所有来源
    allow_methods=["*"],       # 允许所有请求方法（GET、POST 等）
    allow_headers=["*"],       # 允许所有请求头
)

# 数据库文件路径。sqlite3 不需要服务器进程，它就是一个普通文件（messages.db）。
# 重启电脑、重启 uvicorn，这个文件里的数据都不会丢。
DB_PATH = "messages.db"


def init_db():
    """启动时检查并创建数据表。如果表已经存在就跳过，不会重复创建。"""
    # 外层 with closing(...)：无论是否出错，退出时都会自动关闭连接
    # 内层 with conn: 正常结束自动 commit，中途出错自动 rollback
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增编号，每插入一条自动加 1
                    nickname TEXT NOT NULL,               -- 昵称，不能是空
                    content  TEXT NOT NULL,               -- 内容，不能是空
                    mood     INTEGER NOT NULL DEFAULT 3   -- 心情指数 1-5，默认 3（平静）
                )
            """)
            # 旅行足迹表：和留言表放在同一个数据库文件里，互不影响
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trips (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增编号
                    city  TEXT NOT NULL,                      -- 城市名
                    date  TEXT NOT NULL,                      -- 日期，格式 YYYY-MM-DD
                    note  TEXT NOT NULL,                      -- 这段旅程的备注
                    color TEXT NOT NULL                       -- 卡片颜色，十六进制如 #7aa8c9
                )
            """)


# 5 条旅行足迹示例数据，城市对应前端页面上的卡片
TRIP_SEEDS = [
    ("杭州", "2025-04-05", "西湖边走了一下午", "#7aa8c9"),
    ("成都", "2025-05-18", "在巷子里吃了一整天", "#c9a87a"),
    ("厦门", "2025-06-21", "海边吹风到日落", "#7ac9a8"),
    ("西安", "2025-08-09", "城墙下听了一场秦腔", "#a87ac9"),
    ("大理", "2025-09-27", "洱海边骑车绕了一圈", "#c97a8a"),
]


def seed_trips():
    """首次启动时，如果 trips 表还是空的，就自动插入 5 条示例数据。

    判断条件是"表里有没有数据"，而不是"有没有建过表"，
    所以重启不会重复插入；你自己删光了，下次启动会重新补上。
    """
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            count = conn.execute("SELECT COUNT(*) FROM trips").fetchone()[0]
            if count == 0:
                conn.executemany(
                    "INSERT INTO trips (city, date, note, color) VALUES (?, ?, ?, ?)",
                    TRIP_SEEDS,
                )


# 程序一启动就立刻初始化数据库，保证表存在
init_db()
# 再检查一次示例数据，空表才填充
seed_trips()


# 定义"一条留言"的数据结构
# 继承 BaseModel 后，FastAPI 会自动帮你做数据校验
class MessageIn(BaseModel):
    # min_length / max_length：长度限制，和前端输入框的 maxlength 保持一致
    nickname: str = Field(min_length=1, max_length=20)   # 昵称：1-20 个字符
    content: str = Field(min_length=1, max_length=500)   # 内容：1-500 个字符
    # ge=1、le=5：闭区间限制，即必须是 1、2、3、4、5 之一
    mood: int = Field(default=3, ge=1, le=5)

    @field_validator("nickname", "content")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """去掉首尾空格；如果去掉后什么都不剩，就报错（防止只输入空格）。"""
        value = value.strip()
        if not value:
            raise ValueError("不能只输入空格")
        return value


# GET /api/messages：获取所有留言
# 访问这个地址时，FastAPI 会调用下面的函数，把所有留言返回给客户端
@app.get("/api/messages")
def get_messages():
    # with closing(...) 保证查询过程中即使出错，连接也会被自动关闭
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cursor = conn.execute(
            "SELECT id, nickname, content, mood FROM messages ORDER BY id"
        )
        rows = cursor.fetchall()   # 拿到所有结果，每行是一个元组 (id, nickname, content, mood)
    # 把数据库返回的"元组列表"转换成前端期望的"字典列表"
    return [
        {"id": row[0], "nickname": row[1], "content": row[2], "mood": row[3]}
        for row in rows
    ]


# GET /api/trips：返回所有旅行足迹
# 字段固定为 id / city / date / note / color，date 是 YYYY-MM-DD 字符串
@app.get("/api/trips")
def get_trips():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        rows = conn.execute(
            "SELECT id, city, date, note, color FROM trips ORDER BY id"
        ).fetchall()
    # 转成字典列表，前端拿到就能直接渲染卡片
    return [
        {
            "id": row[0],
            "city": row[1],
            "date": row[2],
            "note": row[3],
            "color": row[4],
        }
        for row in rows
    ]


# POST /api/messages：提交一条新留言
# 参数 message: MessageIn 表示：FastAPI 会自动读取请求体里的 JSON，
# 并按 MessageIn 的结构校验它，校验通过后传给函数
@app.post("/api/messages")
def add_message(message: MessageIn):
    # 外层 with closing(...)：自动关闭连接；内层 with conn：自动 commit/rollback
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            # "?" 是占位符，sqlite3 会自动把你传的字符串安全地填进去，
            # 防止有人输入恶意内容破坏数据库（这叫"SQL 注入"防护）
            cursor = conn.execute(
                "INSERT INTO messages (nickname, content, mood) VALUES (?, ?, ?)",
                (message.nickname, message.content, message.mood),
            )
            new_id = cursor.lastrowid   # 获取数据库自动分配的 id
    # 返回这条刚创建的留言，方便客户端确认
    return {"id": new_id, "nickname": message.nickname, "content": message.content, "mood": message.mood}


# DELETE /api/messages/{message_id}：删除指定编号的留言
# 路径里的 {message_id} 是"变量"，比如访问 /api/messages/3 时，message_id 就是 3
# FastAPI 会自动把它转成 int 类型，传非数字会直接返回 422
@app.delete("/api/messages/{message_id}")
def delete_message(message_id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            cursor = conn.execute(
                "DELETE FROM messages WHERE id = ?",
                (message_id,),
            )
            # rowcount 表示这条 SQL 影响了几行：0 说明根本没有这个 id
            deleted_count = cursor.rowcount

    if deleted_count == 0:
        # 404 = "你要找的东西不存在"，前端和浏览器都能看懂这个状态码
        raise HTTPException(status_code=404, detail="留言不存在")

    return {"ok": True, "id": message_id}
