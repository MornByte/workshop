# LinguaHub · 语汇 🌐

> 沉浸式多语种在线教育平台 — 让语言学习像玩游戏一样上瘾

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg)](https://fastapi.tiangolo.com)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com/MornByte/linguahub)

LinguaHub 是一款面向英语、日语、韩语学习者的在线教育平台，通过分级课程体系、互动练习即时反馈、连续学习激励和社区陪伴，帮助用户在碎片化时间里高效学习。

---

## ✨ 功能特色

| 模块 | 说明 |
|------|------|
| 📚 **分级课程体系** | 英语 / 日语 / 韩语 × A1 / B1 / C1 共 9 门课程，每门 12 课时 |
| 📝 **单词记忆** | 闪卡模式 + 释义揭示 + 例句引导 |
| 🎧 **语法练习** | 四选一填空，即时正误反馈动画 |
| 🎤 **口语跟读** | 录音按钮 + TTS 例句朗读 |
| 👂 **听力训练** | 先听后看原文，渐进揭示 |
| 🔥 **连续学习** | 自动计算连续学习天数 |
| 🎯 **个性化推荐** | 基于未完成进度推荐下一课 + 薄弱复习 |
| 🏆 **成就系统** | 9 个自动解锁成就 |
| 💬 **社区交流** | 发帖 + 点赞 |
| 🔐 **用户系统** | 注册 / 登录 / 退出 |

---

## 🛠 技术栈

| 层次 | 技术 |
|------|------|
| 后端 | Python 3.9+ · FastAPI · Uvicorn |
| 数据库 | SQLite（零运维，单文件） |
| 前端 | 原生 HTML + CSS + JavaScript（无构建依赖） |
| 路由 | Hash Routing（无需 rewrite） |
| 认证 | Bearer Token |

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- pip
- Chrome / Firefox / Safari（支持 ES2017+ 和 fetch API）

### 一键启动

```bash
# 1. 克隆项目
git clone https://github.com/MornByte/linguahub.git
cd linguahub

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端（8000 端口，首次启动自动建表 + 填充种子数据）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 4. 新终端启动前端静态文件服务（3000 端口）
python3 -m http.server 3000 --bind 0.0.0.0
```

打开浏览器访问：

- **前端应用**: http://localhost:3000/
- **API 文档 (Swagger)**: http://localhost:8000/docs

---

## 📁 项目结构

```
linguahub/
├── main.py                 # FastAPI 后端入口（所有 API 路由 + DB 初始化）
├── requirements.txt        # Python 依赖
├── index.html              # SPA 入口
├── css/
│   └── style.css           # 设计系统 + 全部组件样式（约 900 行）
├── js/
│   ├── api.js              # API 客户端封装
│   └── app.js              # 应用核心（路由 + 状态 + 12 个页面渲染器）
├── docs/
│   └── development.md      # 完整开发文档（架构/数据库/API/部署指南，1045 行）
├── .gitignore
└── README.md
```

---

## 🔌 API 概览

所有端点前缀 `/api`，需认证的端点携带 `Authorization: Bearer <token>`。

| 模块 | 端点 | 方法 | 需登录 |
|------|------|------|--------|
| 认证 | `/api/auth/register` | POST | ❌ |
| | `/api/auth/login` | POST | ❌ |
| | `/api/auth/logout` | POST | ✅ |
| | `/api/auth/me` | GET | ✅ |
| 语言/课程 | `/api/languages` | GET | ❌ |
| | `/api/courses?language={code}` | GET | ❌ |
| | `/api/courses/{id}` | GET | ✅ |
| | `/api/lessons/{id}` | GET | ✅ |
| 学习 | `/api/lessons/{id}/complete` | POST | ✅ |
| 进度 | `/api/progress?language={code}` | GET | ✅ |
| | `/api/achievements` | GET | ✅ |
| | `/api/recommend` | POST | ✅ |
| 社区 | `/api/community` | GET / POST | POST 需 |
| | `/api/community/{id}/like` | POST | ❌ |
| 仪表盘 | `/api/dashboard` | GET | ✅ |

### 快速 API 示例

```bash
# 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"123456","target_language":"en"}'

# 登录（获取 token）
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"123456"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['token'])")

# 获取语言列表
curl http://localhost:8000/api/languages

# 完成一节课时（替换 1 为实际 lesson_id）
curl -X POST http://localhost:8000/api/lessons/1/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"lesson_id":1,"score":85,"minutes_spent":15}'

# 仪表盘概览
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard
```

---

## 🗄 数据库

首次启动自动创建 `linguahub.db`（SQLite）并填充种子数据：

| 表 | 说明 | 种子数 |
|----|------|--------|
| users | 用户 | 运行时创建 |
| languages | 语言 | 3（🇬🇧英语 / 🇯🇵日语 / 🇰🇷韩语） |
| courses | 课程 | 9（3 语言 × A1/B1/C1） |
| lessons | 课时 | 108（每门 12 课 = 词汇/语法/口语/听力 × 3） |
| user_progress | 用户进度 | 运行时创建 |
| achievements | 成就 | 9 |
| user_achievements | 成就解锁 | 运行时创建 |
| community_posts | 社区动态 | 运行时创建 |
| daily_stats | 日统计 | 运行时创建 |

### 备份

```bash
cp linguahub.db "backups/linguahub_$(date +%Y%m%d_%H%M%S).db"
```

完整表结构和字段说明见 [docs/development.md](docs/development.md#3-数据库设计)。

---

## 🎨 设计系统

深色靛蓝主题 + 青绿主色 + 暖橙激励色：

| Token | 值 | 用途 |
|-------|----|------|
| `--bg-deep` | `#0f0f1a` | 页面底色 |
| `--accent-green` | `#16c79a` | 主色、进度、按钮 |
| `--accent-orange` | `#f5a623` | 成就、连续学习 |
| `--accent-blue` | `#4da8da` | 听力、链接 |
| `--accent-pink` | `#ff6b9d` | 口语、点赞 |

详见 [.uicraft.md](.uicraft.md)。

---

## 🏗 生产部署

### systemd 守护后端

```ini
# /etc/systemd/system/linguahub.service
[Unit]
Description=LinguaHub Backend API
After=network.target

[Service]
WorkingDirectory=/opt/linguahub
ExecStart=/opt/linguahub/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable linguahub && sudo systemctl start linguahub
```

### Nginx 反向代理（SPA + API）

```nginx
server {
    listen 80;
    server_name linguahub.example.com;

    # 前端静态文件
    location / {
        root /opt/linguahub;
        try_files $uri $uri/ /index.html;   # SPA fallback
        expires 7d;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

更多部署细节见 [docs/development.md#5-部署指南](docs/development.md#5-部署指南)。

---

## 🧪 端到端测试

已验证完整 API 流程（注册 → 登录 → 浏览课程 → 完成课时 → 进度追踪 → 成就解锁 → 社区发帖）：

```
✅ 注册用户 → 200 OK
✅ 登录获取 Token → 200 OK
✅ 语言列表 (3 种) → 200 OK
✅ 课程列表 (9 门) → 200 OK
✅ 课时详情 (108 课) → 200 OK
✅ 完成课程得分 85 → 200 OK
✅ 学习进度 1/36 → 200 OK
✅ 个性化推荐 → 200 OK
✅ 成就解锁 2/9 (迈出第一步 + 完美主义) → 200 OK
✅ 社区发帖 → 200 OK
✅ 仪表盘概览 → 200 OK
```

---

## 📈 后续优化方向

| 优先级 | 方向 |
|--------|------|
| P0 | 真实 TTS 音频合成（当前用 Web Speech API 兜底） |
| P0 | 密码哈希升级 bcrypt（当前 SHA-256） |
| P1 | Token 迁移 JWT / Redis（当前内存 Token） |
| P1 | 真实多语种题库（当前为演示数据） |
| P1 | 社区点赞去重（当前可无限 +1） |
| P2 | 学习计划推送（邮件/推送） |
| P2 | 排行榜（周榜/月榜） |
| P2 | 前端 PWA 离线缓存 |
| P3 | pytest + httpx 单元测试 |
| P3 | 前端多语言 i18n |

---

## 📄 文档

完整开发文档（架构设计 · 数据库设计 · API 接口 · 部署指南 · 附录）：

📘 [docs/development.md](docs/development.md)

---

## 📄 License

MIT
