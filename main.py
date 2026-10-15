# 引入 FastAPI 框架，用来快速搭建 Web API
from fastapi import FastAPI
# 引入 BaseModel，用来定义数据的结构（比如一条留言长什么样）
from pydantic import BaseModel
# 引入 CORS 中间件，用来允许前端页面跨域调用本接口
from fastapi.middleware.cors import CORSMiddleware
# sqlite3 是 Python 自带的工具，不需要 pip install，也不需要装额外软件
import sqlite3

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
    """启动时检查并创建留言表。如果表已经存在就跳过，不会重复创建。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增编号，每插入一条自动加 1
            nickname TEXT NOT NULL,               -- 昵称，不能是空
            content  TEXT NOT NULL,               -- 内容，不能是空
            mood     INTEGER NOT NULL DEFAULT 3   -- 心情指数 1-5，默认 3（平静）
        )
    """)
    conn.commit()   # 确认刚才的建表操作（写入磁盘）
    conn.close()    # 关闭连接（好习惯）


# 程序一启动就立刻初始化数据库，保证表存在
init_db()


# 定义"一条留言"的数据结构
# 继承 BaseModel 后，FastAPI 会自动帮你做数据校验
class MessageIn(BaseModel):
    nickname: str   # 昵称，必须是字符串
    content: str    # 留言内容，必须是字符串
    mood: int = 3   # 心情指数 1-5，默认 3（平静）


# GET /api/messages：获取所有留言
# 访问这个地址时，FastAPI 会调用下面的函数，把所有留言返回给客户端
@app.get("/api/messages")
def get_messages():
    # 连接到数据库文件，读取所有留言
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT id, nickname, content, mood FROM messages ORDER BY id"
    )
    rows = cursor.fetchall()   # 拿到所有结果，每行是一个元组 (id, nickname, content, mood)
    conn.close()
    # 把数据库返回的"元组列表"转换成前端期望的"字典列表"
    return [
        {"id": row[0], "nickname": row[1], "content": row[2], "mood": row[3]}
        for row in rows
    ]


# POST /api/messages：提交一条新留言
# 参数 message: MessageIn 表示：FastAPI 会自动读取请求体里的 JSON，
# 并按 MessageIn 的结构校验它，校验通过后传给函数
@app.post("/api/messages")
def add_message(message: MessageIn):
    conn = sqlite3.connect(DB_PATH)
    # "?" 是占位符，sqlite3 会自动把你传的字符串安全地填进去，
    # 防止有人输入恶意内容破坏数据库（这叫"SQL 注入"防护）
    cursor = conn.execute(
        "INSERT INTO messages (nickname, content, mood) VALUES (?, ?, ?)",
        (message.nickname, message.content, message.mood),
    )
    conn.commit()               # 把新留言真正写入数据库文件
    new_id = cursor.lastrowid   # 获取数据库自动分配的 id
    conn.close()
    # 返回这条刚创建的留言，方便客户端确认
    return {"id": new_id, "nickname": message.nickname, "content": message.content, "mood": message.mood}
