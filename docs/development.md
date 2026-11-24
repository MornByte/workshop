# LinguaHub · 语汇 — 多语种在线教育平台 开发文档

> **版本**: v2.0.0  
> **更新日期**: 2026-11-24  
> **技术栈**: Python 3.14 · FastAPI · SQLite · 原生 JavaScript SPA  
> **文档目录**: 架构设计 · 数据库设计 · API 接口 · 部署指南 · 附录

---

## 目 录

- [1. 项目概述](#1-项目概述)
  - [1.1 产品定位](#11-产品定位)
  - [1.2 功能清单](#12-功能清单)
  - [1.3 技术选型](#13-技术选型)
- [2. 架构设计](#2-架构设计)
  - [2.1 总体架构](#21-总体架构)
  - [2.2 目录结构](#22-目录结构)
  - [2.3 前端架构](#23-前端架构)
  - [2.4 后端架构](#24-后端架构)
  - [2.5 数据流](#25-数据流)
- [3. 数据库设计](#3-数据库设计)
  - [3.1 实体关系](#31-实体关系)
  - [3.2 表结构详表](#32-表结构详表)
  - [3.3 种子数据](#33-种子数据)
- [4. API 接口说明](#4-api-接口说明)
  - [4.1 通用约定](#41-通用约定)
  - [4.2 认证模块](#42-认证模块)
  - [4.3 语言与课程](#43-语言与课程)
  - [4.4 学习模块](#44-学习模块)
  - [4.5 进度与成就](#45-进度与成就)
  - [4.6 个性化推荐](#46-个性化推荐)
  - [4.7 社区交流](#47-社区交流)
  - [4.8 仪表盘](#48-仪表盘)
- [5. 部署指南](#5-部署指南)
  - [5.1 环境要求](#51-环境要求)
  - [5.2 快速启动](#52-快速启动)
  - [5.3 生产部署](#53-生产部署)
  - [5.4 Nginx 反向代理](#54-nginx-反向代理)
  - [5.5 数据备份](#55-数据备份)
- [6. 附录](#6-附录)
  - [6.1 HTTP 状态码](#61-http-状态码)
  - [6.2 lesson_type 枚举](#62-lesson_type-枚举)
  - [6.3 成就 condition_type 枚举](#63-成就-condition_type-枚举)
  - [6.4 后续优化方向](#64-后续优化方向)

---

## 1. 项目概述

### 1.1 产品定位

LinguaHub（语汇）是一款面向 18-35 岁语言学习者的沉浸式在线教育平台。核心主张是让语言学习像玩游戏一样上瘾——通过分级课程体系、互动练习即时反馈、连续学习激励系统和社区陪伴，帮助用户在碎片化时间里高效学习英语、日语、韩语。

### 1.2 功能清单

| 模块 | 功能 | 关键实现 |
|------|------|----------|
| 用户系统 | 注册 / 登录 / 退出 | Bearer Token 会话，本地存储 |
| 课程体系 | 3 语言 × A1/B1/C1 共 9 门 | 每门 12 课时，4 种类型循环 |
| 单词记忆 | 闪卡模式 + 释义揭示 | 前端翻卡交互，示例引导 |
| 语法练习 | 四选一填空 | 即时正误反馈，高亮正确答案 |
| 口语跟读 | 录音 + TTS 例句 | MediaRecorder 预留，Web Speech API |
| 听力训练 | 先听后看原文 | 隐藏 transcript，渐进揭示 |
| 进度追踪 | 课程/课时/总分 | 进度条 + 百分比 + 连续天数 |
| 个性化推荐 | 推荐下一课 + 薄弱复习 | 基于完成状态和得分排序 |
| 成就系统 | 9 个自动解锁成就 | lessons_completed / streak / perfect / post_count |
| 社区交流 | 发帖 + 点赞 | 按最新时间排序 |

### 1.3 技术选型

| 层次 | 技术 | 选型理由 |
|------|------|----------|
| 后端框架 | FastAPI 0.141 | 原生异步、类型安全、自动生成 OpenAPI 文档 |
| ASGI 服务器 | Uvicorn | FastAPI 官方推荐，轻量高效 |
| 数据库 | SQLite | 零运维、单文件、学习项目足够 |
| ORM | 原生 sqlite3 | 避免引入额外依赖，保持项目简洁 |
| 密码加密 | SHA-256 + secrets | 满足当前安全等级（生产应换 bcrypt） |
| 前端 | 原生 HTML + CSS + JS | 无构建依赖、可直接预览、适合教学场景 |
| 前端路由 | Hash Routing | 无需服务端 rewrite 即可直接运行 |
| 数据格式 | JSON | 前后端统一，FastAPI 自动序列化 |
| 跨域 | CORSMiddleware allow_origins="*" | 开发期简单，生产需限制 |

---

## 2. 架构设计

### 2.1 总体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端浏览器                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  index.html ──► css/style.css + js/api.js + js/app.js    │   │
│  │                                                          │   │
│  │  Hash Router ──► Page Renderers ──► State(全局/Token)    │   │
│  │         │                                                  │   │
│  │         ▼ fetch() + Bearer Token                            │   │
│  └─────────┼────────────────────────────────────────────────┘   │
└────────────┼───────────────────────────────────────────────────┘
             │ HTTP/JSON (CORS *)
┌────────────┼───────────────────────────────────────────────────┐
│            ▼              后端 (FastAPI + Uvicorn, :8000)       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Authentication (HTTPBearer) → active_tokens (内存字典)   │   │
│  │                                                          │   │
│  │  Auth API ─── Courses API ─── Lessons API ─── ...        │   │
│  │      │             │            │          │             │   │
│  │      ▼             ▼            ▼          ▼             │   │
│  │  fetchone() / fetchall() / execute()  ──────────────────│   │
│  └─────────────────────────────────────────┬────────────────┘   │
│                                            │                    │
│                                   ┌────────┴────────┐          │
│                                   │                 │          │
│                          SQLite Database       Python ThreadPool│
│                          linguahub.db          (sqlite3 默认串行)│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
/workspace/
├── main.py                 # FastAPI 应用入口 + 所有 API 路由 + DB 初始化（约 670 行）
├── linguahub.db            # SQLite 数据库文件（首次启动自动创建）
├── requirements.txt        # Python 依赖
├── index.html              # SPA 入口 HTML（仅骨架，内容由 JS 动态渲染）
├── css/
│   └── style.css           # 完整设计系统（深色主题 + 变量体系 + 全部组件样式）
├── js/
│   ├── api.js              # API 客户端封装（fetch + Token 自动注入）
│   └── app.js              # 主应用（Hash 路由 + 全局 State + 12 个页面渲染器）
└── .uicraft.md             # 设计语境（品牌/配色/原则）
```

### 2.3 前端架构

前端采用原生 JS 单页应用模式，三层职责清晰分离：

```
js/api.js  ─── API 客户端层
│   - 封装 fetch 调用，统一错误处理
│   - 自动注入 Authorization: Bearer <token>
│   - 管理 Token 的 localStorage 存取
│
js/app.js  ─── 应用核心层
│   ├─ parseHash()            解析 URL hash → path + query
│   ├─ State (global)         全局状态：user / langs / activeLang
│   ├─ render()               主渲染函数，switch path 路由
│   ├─ renderNavbar()         动态导航栏（未登录显示登录按钮，已登录显示用户信息）
│   ├─ pageXxx()              12 个页面渲染器
│   └─ bindPageEvents()      事件委托 + 动态事件绑定
│
index.html ── 仅提供 <div class="app"><nav>#navbar</nav><main>#page</main></div>
css/style.css ── 设计令牌 (CSS Variables) + 组件样式（约 900 行）
```

**路由映射表：**

| Hash Path | 页面渲染器 | 需要登录 |
|-----------|-----------|----------|
| `/` | pageHome | 否 |
| `/languages` | pageLanguages | 否 |
| `/courses?lang={code}` | pageCourses | 否 |
| `/course?id={id}` | pageCourse | 否 |
| `/lesson?id={id}` | pageLesson | 是 |
| `/dashboard` | pageDashboard | 是 |
| `/achievements` | pageAchievements | 是 |
| `/community` | pageCommunity | 否（发帖需登录） |
| `/login` | pageLogin(false) | 否 |
| `/register` | pageLogin(true) | 否 |

### 2.4 后端架构

后端 `main.py` 包含一个 FastAPI 实例、9 张表的 schema、Pydantic 数据模型和 14 个 API 端点。核心分层：

```
main.py
├── SCHEMA 常量 (多行 SQL)        → 9 张建表语句
├── init_db()                     → 启动时：executescript + executemany 填充种子数据
├── build_lesson_content()        → 生成示例 lesson JSON（前端可替换为真实题库）
├── Pydantic Models
│   ├── RegisterIn(username, password, email?, target_language?)
│   ├── LoginIn(username, password)
│   ├── CompleteLessonIn(lesson_id, score, minutes_spent?)
│   ├── PostIn(content, category?)
│   └── RecommendIn(language_code)
├── 工具函数
│   ├── fetchone(query, args)     → 查询单行 dict
│   ├── fetchall(query, args)     → 查询多行 list[dict]
│   ├── execute(query, args)      → 写操作，返回 lastrowid
│   ├── hash_password(password)   → SHA-256 哈希
│   ├── get_current_user(token)   → HTTPBearer 依赖，返回 username 或 401
│   ├── compute_streak(user_id)   → 连续学习天数（从 daily_stats 计算）
│   └── check_achievements(user_id, score) → 完成课程时自动检查并解锁成就
└── API 端点 (14 个)
    /api/auth/* (4) + /api/languages (1) + /api/courses* (2)
    + /api/lessons* (3) + /api/progress (1) + /api/achievements (1)
    + /api/recommend (1) + /api/community* (3) + /api/dashboard (1)
```

### 2.5 数据流

以"完成一节词汇课"为例的完整数据流：

```
浏览器                              后端                               SQLite
  │                                 │                                 │
  │ ① GET /api/course/1 (带 Token) │                                 │
  │ ─────────────────────────────► │ ② LEFT JOIN lessons             │
  │                                 │     + user_progress            │
  │                                 │ ───────────────────────────────►│
  │                                 │ ◄──────────────────────────────│
  │ ③ 返回课程信息+完成状态        │                                 │
  │ ◄───────────────────────────── │                                 │
  │                                 │                                 │
  │ ④ GET /api/lessons/1           │                                 │
  │ ─────────────────────────────► │ ⑤ SELECT lessons                │
  │                                 │     + parse content_json       │
  │ ◄───────────────────────────── │                                 │
  │                                 │                                 │
  │ ⑥ POST /api/lessons/1/complete │                                 │
  │    {score: 85, minutes_spent:15}│                                 │
  │ ─────────────────────────────► │ ⑦ UPSERT user_progress          │
  │                                 │ ⑧ UPSERT daily_stats (今天)    │
  │                                 │ ⑨ check_achievements()          │
  │                                 │    → INSERT user_achievements   │
  │                                 │ ───────────────────────────────►│
  │ ◄───────────────────────────── │ ⑩ {"ok": true, "score": 85}    │
```

---

## 3. 数据库设计

### 3.1 实体关系

```
users ──1:N──► user_progress ◄──N:1── lessons ──N:1── courses ──N:1── languages
  │                                           │
  ├──1:N──► user_achievements ──N:1── achievements
  ├──1:N──► community_posts
  └──1:N──► daily_stats
```

核心实体：**用户**、**语言**、**课程**、**课时**、**进度**、**成就**、**社区**、**日统计**。

### 3.2 表结构详表

#### 3.2.1 users 用户表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 用户 ID |
| username | TEXT | UNIQUE NOT NULL | 用户名（2-30 字符） |
| password_hash | TEXT | NOT NULL | SHA-256 哈希值 |
| email | TEXT | | 邮箱（可选） |
| target_language | TEXT | DEFAULT 'en' | 目标语言代码 |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | 注册时间 |

#### 3.2.2 languages 语言表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 语言 ID |
| code | TEXT | UNIQUE NOT NULL | en / ja / ko |
| name | TEXT | NOT NULL | 中文显示名 |
| native_name | TEXT | NOT NULL | 母语名称 |
| flag | TEXT | | emoji 国旗 |
| description | TEXT | | 语言简介 |

#### 3.2.3 courses 课程表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 课程 ID |
| language_code | TEXT | NOT NULL FK→languages.code | 所属语言 |
| level | TEXT | NOT NULL | A1 / A2 / B1 / B2 / C1 / C2 |
| title | TEXT | NOT NULL | 课程标题 |
| subtitle | TEXT | | 副标题/简介 |
| icon | TEXT | | emoji 图标 |
| color | TEXT | | 主题色 HEX |
| total_lessons | INTEGER | DEFAULT 0 | 课时总数 |

#### 3.2.4 lessons 课时表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 课时 ID |
| course_id | INTEGER | NOT NULL FK→courses.id | 所属课程 |
| title | TEXT | NOT NULL | 课时标题 |
| lesson_type | TEXT | NOT NULL | vocab / grammar / speaking / listening |
| order_index | INTEGER | NOT NULL | 课程内顺序（1-based） |
| duration_min | INTEGER | DEFAULT 15 | 预估时长（分钟） |
| content_json | TEXT | NOT NULL | 题目/对话等内容的 JSON 字符串 |

**content_json 格式示例：**

```jsonc
// vocab 类型
{ "questions": [
    { "type": "word-card", "word": "Hello", "translation": "你好", "example": "Hello, nice to meet you." },
    ...
]}

// grammar 类型
{ "questions": [
    { "type": "fill-blank", "prompt": "I ___ a student.", "options": ["am","is","are","be"], "answer": 0 },
    ...
]}

// speaking 类型
{ "questions": [
    { "type": "speaking", "sentence": "Hello, how are you?", "translation": "你好，最近怎么样？" },
    ...
]}

// listening 类型
{ "questions": [
    { "type": "listening", "transcript": "...", "q": "...", "options": [...], "answer": 0 },
    ...
]}
```

#### 3.2.5 user_progress 用户进度表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 记录 ID |
| user_id | INTEGER | NOT NULL FK→users.id | 用户 |
| lesson_id | INTEGER | NOT NULL FK→lessons.id | 课时 |
| completed | INTEGER | DEFAULT 0 | 0=未完成，1=已完成 |
| score | INTEGER | DEFAULT 0 | 最近一次得分 |
| attempts | INTEGER | DEFAULT 0 | 尝试次数 |
| last_accessed | TEXT | DEFAULT CURRENT_TIMESTAMP | 最后访问时间 |

**唯一约束**: UNIQUE(user_id, lesson_id) — 每个用户对每节课只有一条进度记录。

#### 3.2.6 achievements 成就表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 成就 ID |
| code | TEXT | UNIQUE NOT NULL | 内部代码 |
| name | TEXT | NOT NULL | 显示名称 |
| description | TEXT | | 解锁条件描述 |
| icon | TEXT | | emoji 图标 |
| condition_type | TEXT | NOT NULL | 见 §6.3 枚举 |
| condition_value | INTEGER | NOT NULL | 条件阈值 |
| reward_points | INTEGER | DEFAULT 50 | 解锁奖励点数 |

#### 3.2.7 user_achievements 用户成就解锁记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 记录 ID |
| user_id | INTEGER | NOT NULL FK→users.id | 用户 |
| achievement_id | INTEGER | NOT NULL FK→achievements.id | 成就 |
| unlocked_at | TEXT | DEFAULT CURRENT_TIMESTAMP | 解锁时间 |

#### 3.2.8 community_posts 社区动态

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 动态 ID |
| user_id | INTEGER | NOT NULL FK→users.id | 发布者 |
| content | TEXT | NOT NULL | 动态正文（≤500 字符） |
| category | TEXT | DEFAULT 'general' | 分类标签 |
| likes | INTEGER | DEFAULT 0 | 点赞数 |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | 发布时间 |

#### 3.2.9 daily_stats 日统计

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 记录 ID |
| user_id | INTEGER | NOT NULL FK→users.id | 用户 |
| date | TEXT | NOT NULL (ISO 8601) | 统计日期 YYYY-MM-DD |
| lessons_completed | INTEGER | DEFAULT 0 | 当日完成课时数 |
| minutes_spent | INTEGER | DEFAULT 0 | 当日学习时长（分钟） |

**唯一约束**: UNIQUE(user_id, date)。用于计算连续学习天数（streak）。

### 3.3 种子数据

首次启动自动填充（使用 INSERT OR IGNORE，重启不会重复）：

| 实体 | 数量 | 详情 |
|------|------|------|
| languages | 3 | 🇬🇧英语 / 🇯🇵日语 / 🇰🇷韩语 |
| courses | 9 | 3 语言 × 3 级别（A1 / B1 / C1） |
| lessons | 108 | 每门 12 课时 = 4 种类型 × 3 课 |
| achievements | 9 | 4 种解锁条件（lessons_completed × 4 / streak_days × 3 / perfect_score / post_count） |

---

## 4. API 接口说明

### 4.1 通用约定

**Base URL**: `http://<host>:8000`

**认证方式**: Bearer Token  
需认证的端点需在请求头携带 `Authorization: Bearer <token>`，Token 由 `/api/auth/login` 返回。

**响应格式**: 成功返回 JSON，错误返回 `{"detail": "..."}` + HTTP 错误码。

**分页**: 当前社区列表支持 `?limit=N`（默认 20）。

**时间格式**: 所有时间字段为 ISO 8601 字符串（SQLite CURRENT_TIMESTAMP）。

**CORS**: 当前配置 `allow_origins=["*"]`，生产应收紧。

---

### 4.2 认证模块

#### 4.2.1 用户注册

```
POST /api/auth/register          （公开）
```

**请求体**:

```jsonc
{
  "username": "string",           // 2-30 字符，必填
  "password": "string",           // ≥4 字符，必填
  "email": "string | null",       // 可选
  "target_language": "en"         // en / ja / ko，默认 en
}
```

**成功响应** `200`:

```jsonc
{ "ok": true, "message": "注册成功" }
```

**错误响应**:
| 状态码 | 触发条件 |
|--------|----------|
| 400 | 用户名已存在 |
| 422 | Pydantic 校验失败（用户名长度/密码长度） |

---

#### 4.2.2 用户登录

```
POST /api/auth/login             （公开）
```

**请求体**:

```jsonc
{ "username": "string", "password": "string" }
```

**成功响应** `200`:

```jsonc
{
  "ok": true,
  "token": "d7e701396eae41ca494...",   // 32 字符十六进制
  "user": {
    "id": 1,
    "username": "testuser",
    "target_language": "en"
  }
}
```

**错误响应**:
| 状态码 | 触发条件 |
|--------|----------|
| 401 | 用户名或密码错误 |

---

#### 4.2.3 用户退出

```
POST /api/auth/logout            （需 Token）
```

**成功响应** `200`:

```jsonc
{ "ok": true }
```

**说明**: 服务端从内存中删除该 Token。

---

#### 4.2.4 获取当前用户信息

```
GET /api/auth/me                 （需 Token）
```

**成功响应** `200`:

```jsonc
{
  "user": {
    "id": 1,
    "username": "testuser",
    "email": null,
    "target_language": "en",
    "created_at": "2026-11-24 11:15:30"
  },
  "stats": {
    "completed_lessons": 3,
    "total_score": 255,
    "achievements_count": 2
  }
}
```

---

### 4.3 语言与课程

#### 4.3.1 获取所有语言

```
GET /api/languages               （公开）
```

**响应**:

```jsonc
[
  { "id": 1, "code": "en", "name": "英语", "native_name": "English", "flag": "🇬🇧", "description": "..." },
  { "id": 2, "code": "ja", "name": "日语", ... },
  { "id": 3, "code": "ko", ... }
]
```

---

#### 4.3.2 获取课程列表

```
GET /api/courses                 （公开）
GET /api/courses?language=en     （按语言过滤）
```

**响应**:

```jsonc
[
  {
    "id": 1,
    "language_code": "en",
    "level": "A1",
    "title": "英语入门 A1",
    "subtitle": "日常问候与基础句型",
    "icon": "🌱",
    "color": "#16c79a",
    "total_lessons": 12
  },
  ...
]
```

---

#### 4.3.3 获取课程详情（含课时列表）

```
GET /api/courses/{course_id}     （需 Token）
```

**响应**:

```jsonc
{
  "course": { /* courses 表原始字段 */ },
  "lessons": [
    {
      "id": 1,
      "course_id": 1,
      "title": "核心词汇 · 第 1 课",
      "lesson_type": "vocab",
      "order_index": 1,
      "duration_min": 12,
      "completed": 1,          // 0 或 1（该用户的完成状态）
      "score": 85,
      "last_accessed": "2026-11-24 11:30:00"
    },
    ...
  ]
}
```

---

### 4.4 学习模块

#### 4.4.1 获取课时详情

```
GET /api/lessons/{lesson_id}     （需 Token）
```

**响应**:

```jsonc
{
  "lesson": {
    "id": 1,
    "course_id": 1,
    "title": "核心词汇 · 第 1 课",
    "lesson_type": "vocab",
    "order_index": 1,
    "duration_min": 12
  },
  "content": {
    "questions": [ /* 见 §3.2.4 content_json 格式 */ ]
  }
}
```

---

#### 4.4.2 完成课时 / 提交分数

```
POST /api/lessons/{lesson_id}/complete   （需 Token）
```

**请求体**:

```jsonc
{
  "lesson_id": 1,           // 路径参数同时需要在 body 中？不，路径参数已包含
  "score": 85,              // 0-100，必填
  "minutes_spent": 15       // 学习时长，默认 15
}
```

> **注意**: `lesson_id` 作为 URL 路径参数，`CompleteLessonIn` 中的字段会与路径参数合并校验。

**成功响应** `200`:

```jsonc
{ "ok": true, "score": 85 }
```

**副作用**:
1. UPSERT `user_progress`：设置 completed=1，更新 score，attempts+1
2. UPSERT `daily_stats`（今天）：lessons_completed+1，minutes_spent+N
3. 调用 `check_achievements()`：检查并解锁成就

---

### 4.5 进度与成就

#### 4.5.1 获取学习进度

```
GET /api/progress                （需 Token）
GET /api/progress?language=en    （按语言过滤）
```

**响应**:

```jsonc
{
  "courses": [
    {
      "id": 1, "language_code": "en", "level": "A1",
      "title": "英语入门 A1", "subtitle": "...",
      "icon": "🌱", "color": "#16c79a", "total_lessons": 12,
      "completed_lessons": 3
    }
  ],
  "overall": {
    "total": 36,             // 该语言下所有课程的总课时
    "completed": 3,          // 已完成
    "percent": 8.3           // 百分比（四舍五入到小数点后 1 位）
  },
  "streak_days": 1           // 连续学习天数
}
```

---

#### 4.5.2 获取成就列表

```
GET /api/achievements            （需 Token）
```

**响应**:

```jsonc
[
  {
    "id": 1,
    "code": "first_step",
    "name": "迈出第一步",
    "description": "完成第一课",
    "icon": "🎯",
    "condition_type": "lessons_completed",
    "condition_value": 1,
    "reward_points": 30,
    "unlocked": true            // 该用户是否已解锁
  },
  ...
]
```

---

### 4.6 个性化推荐

#### 4.6.1 获取推荐

```
POST /api/recommend              （需 Token）
```

**请求体**:

```jsonc
{ "language_code": "en" }
```

**场景 A（有未完成课时）**:

```jsonc
{
  "next": {
    "id": 1, "course_id": 1, "title": "核心词汇 · 第 1 课",
    "lesson_type": "vocab", "order_index": 1, "duration_min": 12,
    "level": "A1", "course_title": "英语入门 A1"
  },
  "review": {                  // 可能为 null（尚无已完成课时）
    "id": 5, "title": "语法精讲 · 第 2 课",
    "score": 60, "attempts": 2,
    ...
  },
  "message": "基于你的进度，这里是我们推荐的下一步练习"
}
```

**场景 B（所有课时已完成）**:

```jsonc
{ "message": "太棒了！该语言下你已完成所有课程 🎉", "next": null }
```

**推荐算法**:
- `next`: 该语言下 `user_progress.completed IS NULL OR 0` 的课时，按 `order_index ASC` 取第一条
- `review`: 该用户已完成课时中 `score` 最低的一条（ORDER BY score ASC LIMIT 1）

---

### 4.7 社区交流

#### 4.7.1 获取社区动态

```
GET /api/community               （公开）
GET /api/community?limit=50      （可选）
```

**响应**:

```jsonc
[
  {
    "id": 1,
    "user_id": 1,
    "content": "今天完成了第一节英语课！",
    "category": "学习打卡",
    "likes": 5,
    "created_at": "2026-11-24 11:45:00",
    "username": "testuser",
    "target_language": "en"
  },
  ...
]
```

---

#### 4.7.2 发布动态

```
POST /api/community              （需 Token）
```

**请求体**:

```jsonc
{
  "content": "string",          // 1-500 字符，必填
  "category": "学习打卡"         // 默认 "general"
}
```

**成功响应** `200`:

```jsonc
{ "id": 1, "ok": true }
```

**副作用**: 自动调用 `check_achievements()`，检查 `post_count` 条件。

---

#### 4.7.3 点赞

```
POST /api/community/{post_id}/like    （公开）
```

**成功响应** `200`:

```jsonc
{ "ok": true }
```

**说明**: 当前实现是 `likes = likes + 1`，无用户去重。生产应引入 `post_likes` 表。

---

### 4.8 仪表盘

#### 4.8.1 仪表盘概览（一站式）

```
GET /api/dashboard               （需 Token）
```

**响应**:

```jsonc
{
  "user": {
    "id": 1, "username": "testuser", "target_language": "en"
  },
  "progress": {
    "courses": [ /* 同 /api/progress.courses */ ],
    "overall": { "total": 36, "completed": 3, "percent": 8.3 },
    "streak_days": 1
  },
  "achievements": {
    "unlocked": 2, "total": 9,
    "list": [ /* 同 /api/achievements */ ]
  },
  "recommend": { /* 同 /api/recommend 响应 */ },
  "streak_days": 1,
  "recent_posts": [ /* 最新 5 条社区动态 */ ]
}
```

**说明**: 这是一个聚合端点，减少前端多次请求。内部调用了 `get_progress`、`get_achievements`、`recommend` 三个函数。

---

## 5. 部署指南

### 5.1 环境要求

| 依赖 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.9+ | 使用了 typing.Dict/List/Optional |
| pip | 20.0+ | 依赖安装 |
| 操作系统 | Linux / macOS / Windows | SQLite 跨平台 |
| 浏览器 | Chrome 80+ / Firefox 80+ / Safari 14+ | 需支持 ES2017+ 和 fetch API |

### 5.2 快速启动

```bash
# 1. 克隆项目
cd /workspace

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动后端（默认 8000 端口）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 5. 新终端启动前端静态文件服务（默认 3000 端口）
python3 -m http.server 3000 --bind 0.0.0.0

# 6. 打开浏览器访问
# http://localhost:3000/     （前端）
# http://localhost:8000/docs （Swagger API 文档）
```

### 5.3 生产部署

#### 5.3.1 使用 systemd 守护后端

创建 `/etc/systemd/system/linguahub.service`：

```ini
[Unit]
Description=LinguaHub Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/linguahub
Environment=PATH=/opt/linguahub/venv/bin
ExecStart=/opt/linguahub/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

然后：
```bash
sudo systemctl enable linguahub
sudo systemctl start linguahub
sudo journalctl -u linguahub -f       # 查看日志
```

#### 5.3.2 安全加固清单

1. **CORS 限制**: 将 `allow_origins=["*"]` 改为 `allow_origins=["https://your-domain.com"]`
2. **密码哈希**: 将 `hash_password()` 从 SHA-256 升级为 bcrypt
   ```bash
   pip install bcrypt
   ```
3. **Token 存储**: 当前使用内存字典 `active_tokens`，服务重启会丢失。生产应换用：
   - JWT（无状态，签名验证）
   - Redis（带过期时间，可多实例共享）
4. **HTTPS**: 在 Nginx/LB 层终止 TLS
5. **数据库备份**: 见 §5.5

### 5.4 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name linguahub.your-domain.com;

    # 前端静态文件
    location / {
        root /opt/linguahub;
        try_files $uri $uri/ /index.html;   # SPA fallback
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }

    # Swagger 文档
    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 5.5 数据备份

SQLite 数据库是单文件，简单可靠：

```bash
# 每日 02:00 自动备份
# crontab -e
# 0 2 * * * /opt/linguahub/backup.sh

# backup.sh 内容
#!/bin/bash
cd /opt/linguahub
cp linguahub.db "backups/linguahub_$(date +%Y%m%d_%H%M%S).db"
find backups -name '*.db' -mtime +30 -delete   # 保留 30 天
```

---

## 6. 附录

### 6.1 HTTP 状态码

| 状态码 | 使用场景 |
|--------|----------|
| 200 OK | 所有 GET / POST 成功 |
| 400 Bad Request | 业务校验失败（用户名已存在） |
| 401 Unauthorized | Token 缺失、无效、或密码错误 |
| 404 Not Found | 课程/课时/用户不存在 |
| 422 Unprocessable Entity | Pydantic 数据校验失败 |

### 6.2 lesson_type 枚举

| 值 | 标签 | 交互模式 |
|----|------|----------|
| `vocab` | 词汇 | 闪卡翻牌 + 释义揭示 |
| `grammar` | 语法 | 四选一填空 + 即时反馈 |
| `speaking` | 口语 | 录音按钮 + TTS 例句 |
| `listening` | 听力 | 先听后看 + 选择题 |

### 6.3 成就 condition_type 枚举

| 值 | 含义 | condition_value 单位 |
|----|------|---------------------|
| `lessons_completed` | 累计完成课时数 | 课时数 |
| `streak_days` | 连续学习天数 | 天数 |
| `perfect_score` | 单次课程得分阈值 | 分数（≥ value 时触发） |
| `post_count` | 社区发布动态数 | 条数 |

### 6.4 后续优化方向

| 优先级 | 方向 | 说明 |
|--------|------|------|
| P0 | 音频合成接入 | speaking/listening 当前用 Web Speech API 兜底，应接入真实 TTS（Azure / Google / 阿里云） |
| P0 | bcrypt 替换 SHA-256 | 当前密码哈希强度不足以抵御彩虹表 |
| P1 | Token 迁移 JWT / Redis | 内存 Token 在服务重启后失效，且无法横向扩展 |
| P1 | 真实题库 | 当前 `build_lesson_content()` 返回的是演示数据，应接入真实多语种题库 |
| P1 | 社区点赞去重 | 当前每条 post 的 likes 可以无限 +1，应引入 `post_likes(user_id, post_id)` |
| P2 | 学习计划推送 | 基于 streak 发送邮件/推送提醒 |
| P2 | 排行榜 | 周榜/月榜（总课时 / 成就点数） |
| P2 | 前端 PWA | 添加 Service Worker 和 manifest，支持离线缓存 |
| P3 | 单元测试 | 当前无后端测试，建议用 pytest + httpx 补充 |
| P3 | 多语言前端 i18n | 当前前端文案均为中文常量，应抽离为 lang 文件 |

---

> **文档结束** — LinguaHub 开发团队 © 2026
