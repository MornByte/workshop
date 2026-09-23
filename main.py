# 引入 FastAPI 框架，用来快速搭建 Web API
from fastapi import FastAPI
# 引入 BaseModel，用来定义数据的结构（比如一条留言长什么样）
from pydantic import BaseModel
# 引入 CORS 中间件，用来允许前端页面跨域调用本接口
from fastapi.middleware.cors import CORSMiddleware

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

# 用一个普通的 Python 列表来存留言。
# 因为只是存在内存里，所以程序一重启，留言就没了（满足"不用数据库"的要求）
messages = []


# 定义"一条留言"的数据结构
# 继承 BaseModel 后，FastAPI 会自动帮你做数据校验
# 比如客户端少传了字段，或者类型不对，它会直接返回清晰的错误提示
class MessageIn(BaseModel):
    nickname: str   # 昵称，必须是字符串
    content: str    # 留言内容，必须是字符串


# GET /api/messages：获取所有留言
# 访问这个地址时，FastAPI 会调用下面的函数，把所有留言返回给客户端
@app.get("/api/messages")
def get_messages():
    # 直接返回列表，FastAPI 会自动把它转成 JSON 格式
    return messages


# POST /api/messages：提交一条新留言
# 参数 message: MessageIn 表示：FastAPI 会自动读取请求体里的 JSON，
# 并按 MessageIn 的结构校验它，校验通过后传给函数
@app.post("/api/messages")
def add_message(message: MessageIn):
    # 把这条留言整理成一个字典，加一个 id 方便以后区分
    new_message = {
        "id": len(messages) + 1,        # 用当前留言数量+1 作为简单编号
        "nickname": message.nickname,  # 从请求里取昵称
        "content": message.content,    # 从请求里取内容
    }
    # 把新留言追加到内存列表里
    messages.append(new_message)
    # 返回这条刚创建的留言，方便客户端确认
    return new_message
