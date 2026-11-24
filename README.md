# 今日心情墙 ☀

一个用 FastAPI 做后端、SQLite 存数据、单页 HTML 做前端的**心情留言板**。可以记录此刻的心情（开心/不错/平静/低落/难过）和留言内容，所有数据重启后不丢失。

## ✨ 功能特性

- 📝 提交留言：填写昵称、心情指数、留言内容
- 😊 五种心情：开心 😄 / 不错 🙂 / 平静 😐 / 低落 😟 / 难过 😢
- 📋 留言列表：按提交顺序展示所有留言，卡片左侧显示心情表情和对应色带
- 🗑️ 删除留言：每条留言右侧有“删除”按钮，点击确认后从数据库移除
- 💾 数据持久化：使用 SQLite 数据库，重启电脑或服务后留言不丢失
- 🌐 跨域支持：前端可直接通过 `file://` 打开或本地 HTTP 服务访问

## 🛠 技术栈

| 部分 | 技术 |
|------|------|
| 后端 | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| 数据库 | [SQLite](https://www.sqlite.org/)（Python 自带 `sqlite3` 模块，无需安装） |
| 前端 | 原生 HTML + CSS + JavaScript（无框架） |

## 📁 项目结构

```
.
├── main.py           # 后端 API：路由、数据库连接、接口逻辑
├── index.html        # 前端页面：表单 + 留言列表
├── messages.db       # SQLite 数据库文件（首次运行自动生成）
├── requirements.txt  # Python 依赖清单
└── README.md         # 本说明文件
```

## 🚀 快速开始

### 1. 安装依赖（只需做一次）

打开命令行（PowerShell 或 cmd），执行：

```bash
cd d:\workshop
pip install -r requirements.txt
```

### 2. 启动后端服务

```bash
python -m uvicorn main:app --reload
```

看到以下输出说明启动成功：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

> ⚠️ 这个命令行窗口**不能关闭**，关了服务就停了。

> ⚠️ **必须在 `d:\workshop` 目录下启动。**
> 因为数据库用的是相对路径 `messages.db`，程序会把它建在“你当前所在目录”里。
> 如果你在别的目录（比如 `C:\Users\你`）运行 uvicorn，程序会**新建一个空数据库**，
> 网页上看起来就像“以前的留言全都不见了”，其实只是读错了文件。
> 所以每次启动前，先确认命令行里执行过 `cd d:\workshop`。

### 3. 打开前端页面

**方式 A（最简单）**：在文件管理器里**双击 `index.html`**，用浏览器打开即可。

**方式 B（推荐，避免 `file://` 兼容问题）**：新开一个命令行窗口，运行：

```bash
cd d:\workshop
python -m http.server 5500
```

然后浏览器访问 http://localhost:5500/index.html

> 端口 `5500` 是前端页面服务，`8000` 是后端 API，两者不冲突。

## 📡 API 接口

### 获取所有留言

```
GET /api/messages
```

返回示例：

```json
[
  {
    "id": 1,
    "nickname": "小明",
    "content": "今天天气真好",
    "mood": 5
  }
]
```

`mood` 字段：`1`=难过 😢 / `2`=低落 😟 / `3`=平静 😐 / `4`=不错 🙂 / `5`=开心 😄

### 提交一条留言

```
POST /api/messages
Content-Type: application/json

{
  "nickname": "小明",
  "content": "今天天气真好",
  "mood": 5
}
```

返回示例：

```json
{
  "id": 1,
  "nickname": "小明",
  "content": "今天天气真好",
  "mood": 5
}
```

#### 字段规则（后端会强制校验）

| 字段 | 规则 | 不符合时 |
|------|------|----------|
| `nickname` | 不能为空，不能全是空格，**1–20 个字** | 返回 422 |
| `content` | 不能为空，不能全是空格，**1–500 个字** | 返回 422 |
| `mood` | 必须是 **1–5** 的整数，不传默认 3 | 返回 422 |

> 小提示：昵称和内容前后的空格会被自动去掉（提交 `"  小明  "` 会存成 `"小明"`）。
> 422 是 FastAPI 的“数据格式不对”状态码，说明请求被拦下来了，数据库不会写入任何东西。

### 删除一条留言

```
DELETE /api/messages/{id}
```

例如删除编号为 3 的留言：`DELETE /api/messages/3`

删除成功返回：

```json
{
  "ok": true,
  "id": 3
}
```

如果这个编号不存在，返回 **404**：

```json
{
  "detail": "留言不存在"
}
```

> 也可以直接在网页上点每条留言右侧的“删除”按钮，效果一样。

### 获取旅行足迹（卡片数据）

```
GET /api/trips
```

返回一个 JSON 数组，每项的字段固定为 `id` / `city` / `date` / `note` / `color`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | 数字 | 自增编号 |
| `city` | 字符串 | 城市名 |
| `date` | 字符串 | 日期，格式固定为 `YYYY-MM-DD` |
| `note` | 字符串 | 这段旅程的备注 |
| `color` | 字符串 | 卡片颜色，十六进制，如 `#7aa8c9` |

真实返回示例：

```json
[
  {"id": 1, "city": "杭州", "date": "2025-04-05", "note": "西湖边走了一下午", "color": "#7aa8c9"},
  {"id": 2, "city": "成都", "date": "2025-05-18", "note": "在巷子里吃了一整天", "color": "#c9a87a"},
  {"id": 3, "city": "厦门", "date": "2025-06-21", "note": "海边吹风到日落", "color": "#7ac9a8"},
  {"id": 4, "city": "西安", "date": "2025-08-09", "note": "城墙下听了一场秦腔", "color": "#a87ac9"},
  {"id": 5, "city": "大理", "date": "2025-09-27", "note": "洱海边骑车绕了一圈", "color": "#c97a8a"}
]
```

说明：

- **首次启动自动填示例**：如果 `trips` 表是空的，程序会自动插入上面 5 条示例数据，每条颜色都不同；表里已有数据时不会重复插入。
- **不会影响留言功能**：旅行足迹和留言是同一个数据库文件里的两张独立表，互相不干扰。
- **跨域已放开**：接口允许任意来源访问，页面从 `http://localhost:5500` 打开或直接双击 `index.html`（`file://`）都能正常取到数据。

### 交互式文档

服务启动后，打开 http://127.0.0.1:8000/docs 可以用 FastAPI 自带的 Swagger UI 在线测试接口。

## 💾 数据库说明

- 数据库文件：`messages.db`
- 表名：`messages`
- 字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键，每条留言的唯一编号 |
| nickname | TEXT | 昵称，非空，最长 20 字 |
| content | TEXT | 留言内容，非空，最长 500 字 |
| mood | INTEGER | 心情指数 1-5，默认 3 |

数据库由 `main.py` 启动时的 `init_db()` 自动创建（如果不存在）。

> ⚠️ 数据库文件的位置取决于**你在哪个目录启动 uvicorn**，不在 `d:\workshop` 启动就会生成到别处。

## ❓ 常见问题

**Q: 浏览器控制台报错 `ERR_CONNECTION_REFUSED`？**

后端服务没启动。检查命令行里是否还在运行 `uvicorn main:app --reload`，没有就重新启动。

**Q: 怎么判断后端是否活着？**

浏览器直接打开 http://localhost:8000/api/messages ，能看到 `[]` 或留言列表就说明正常。

**Q: 重启电脑后留言还在吗？**

在。数据存在 `messages.db` 文件里（硬盘），不是内存，所以重启不丢。

**Q: 启动后留言全空了，明明之前还有？**

大概率是在**别的目录**启动了 uvicorn，程序在那边新建了一个空数据库。按下面两步确认：

1. 看命令行里当前目录是不是 `d:\workshop`（可以用 `dir messages.db` 检查这个文件在不在）
2. 关掉服务，`cd d:\workshop` 后重新启动

真实数据一直躺在 `d:\workshop\messages.db` 里，没有丢，只是刚才读的是另一个空文件。

**Q: 提交时返回 422 是什么情况？**

说明数据没通过后端校验。常见原因：昵称为空或全是空格、昵称超过 20 字、内容超过 500 字、`mood` 不在 1–5 之间。改成合规内容再提交即可。

**Q: 想清空所有留言？**

可以直接在网页上逐条点“删除”，也可以执行：

```bash
python -c "import sqlite3; conn=sqlite3.connect('messages.db'); conn.execute('DELETE FROM messages'); conn.commit(); conn.close()"
```

**Q: 前端页面提交后没有反应？**

1. 按 F12 打开浏览器控制台，看有没有红色报错
2. 确认后端在运行（见上）
3. 尝试用无痕模式打开页面，排除浏览器扩展干扰

## 🔧 数据库连接设计要点

`main.py` 中所有数据库操作都使用了上下文管理器，确保异常时资源释放：

```python
from contextlib import closing

with closing(sqlite3.connect(DB_PATH)) as conn:
    with conn:  # 自动 commit/rollback
        conn.execute(...)
```

- 外层 `closing()`：保证连接无论是否出错都会被关闭
- 内层 `with conn`：保证事务正常提交，异常时自动回滚

> ⚠️ 注意：Python 的 `sqlite3.Connection` 作为上下文管理器时，`__exit__` 只负责 commit/rollback，**不会自动关闭连接**，所以需要外层 `closing()` 来保证连接关闭。
