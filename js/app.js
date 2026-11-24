/* ============================================================
   LinguaHub · 应用主入口
   状态管理 + Hash 路由 + 页面渲染
   ============================================================ */

// ---------- 全局状态 ----------
const State = {
  user: null,
  langs: [],
  activeLang: localStorage.getItem("linguahub_lang") || "en",
};

// ---------- 工具函数 ----------
function $(sel, root = document) { return root.querySelector(sel); }
function $all(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

function toast(msg, type = "info") {
  let container = $(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }
  const t = document.createElement("div");
  t.className = `toast ${type}`;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

function getInitials(name) {
  if (!name) return "?";
  return name.slice(0, 1).toUpperCase();
}

const LANG_NAMES = { en: "英语", ja: "日语", ko: "韩语" };
const LANG_FLAGS = { en: "🇬🇧", ja: "🇯🇵", ko: "🇰🇷" };
const LEVEL_LABELS = { A1: "入门", A2: "初级", B1: "中级", B2: "中高级", C1: "精通", C2: "母语级" };
const LESSON_TYPE_LABELS = { vocab: "词汇", grammar: "语法", speaking: "口语", listening: "听力" };

function loadingHTML(text = "加载中...") {
  return `<div class="loading"><div class="loading-spinner"></div><div>${text}</div></div>`;
}

// ---------- 路由 ----------
function parseHash() {
  // #/courses?lang=en
  const hash = window.location.hash.slice(1) || "/";
  const [path, queryStr] = hash.split("?");
  const params = {};
  if (queryStr) queryStr.split("&").forEach(kv => {
    const [k, v] = kv.split("=");
    if (k) params[k] = decodeURIComponent(v || "");
  });
  const segments = path.split("/").filter(Boolean);
  return { path, segments, params };
}

function navigate(path) {
  window.location.hash = path;
}

// ---------- 认证检查 ----------
function requireAuth() {
  if (!State.user) {
    toast("请先登录", "warning");
    navigate("/login");
    return false;
  }
  return true;
}

// ---------- 主渲染 ----------
async function render() {
  const app = $("#page");
  app.innerHTML = loadingHTML();

  // 尝试恢复登录
  if (!State.user && getToken()) {
    try {
      const me = await Api.me();
      State.user = me.user;
    } catch {
      clearToken();
    }
  }

  // 加载语种列表
  if (State.langs.length === 0) {
    try { State.langs = await Api.languages(); } catch { /* ignore */ }
  }

  // 渲染导航栏
  renderNavbar();

  const route = parseHash();
  try {
    switch (route.path) {
      case "/":
        app.innerHTML = pageHome(); break;
      case "/languages":
        app.innerHTML = pageLanguages(); break;
      case "/courses":
        app.innerHTML = await pageCourses(route.params.lang); break;
      case "/course":
        app.innerHTML = await pageCourse(route.params.id); break;
      case "/lesson":
        app.innerHTML = await pageLesson(route.params.id); break;
      case "/dashboard":
        app.innerHTML = await pageDashboard(); break;
      case "/achievements":
        app.innerHTML = await pageAchievements(); break;
      case "/community":
        app.innerHTML = await pageCommunity(); break;
      case "/login":
        app.innerHTML = pageLogin(false); break;
      case "/register":
        app.innerHTML = pageLogin(true); break;
      default:
        app.innerHTML = `<div class="empty-state"><div class="empty-icon">🧭</div><h2>页面走丢了</h2><p>返回 <a href="#/">首页</a></p></div>`;
    }
  } catch (err) {
    app.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><h2>加载失败</h2><p>${err.message}</p></div>`;
  }

  app.classList.remove("page-enter");
  void app.offsetWidth; // force reflow
  app.classList.add("page-enter");

  // 绑定页面内事件
  bindPageEvents();
}

// ---------- 导航栏渲染 ----------
function renderNavbar() {
  const nav = $("#navbar");
  if (!nav) return;

  const langChips = State.langs.map(l =>
    `<span class="lang-chip ${l.code === State.activeLang ? "active" : ""}" data-lang="${l.code}" title="${l.name} ${l.native_name}">${l.flag}</span>`
  ).join("");

  const navLinks = [
    { path: "/", label: "🏠 首页" },
    { path: "/dashboard", label: "📊 学习中心", auth: true },
    { path: "/languages", label: "🌍 选择语言" },
    { path: "/community", label: "💬 社区" },
    { path: "/achievements", label: "🏆 成就", auth: true },
  ].map(l => {
    const active = parseHash().path === l.path ? "active" : "";
    return `<span class="nav-link ${active}" data-path="${l.path}">${l.label}</span>`;
  }).join("");

  let userArea;
  if (State.user) {
    userArea = `
      <div class="user-info" id="userMenu">
        <div class="avatar">${getInitials(State.user.username)}</div>
        <span class="username">${State.user.username}</span>
      </div>
      <button class="btn btn-ghost btn-sm" id="logoutBtn">退出</button>`;
  } else {
    userArea = `
      <div class="auth-buttons">
        <button class="btn btn-secondary btn-sm" id="loginBtn">登录</button>
        <button class="btn btn-primary btn-sm" id="registerBtn">注册</button>
      </div>`;
  }

  nav.innerHTML = `
    <div class="navbar-inner">
      <div class="logo" data-path="/">
        <div class="logo-icon">🌐</div>
        <span class="logo-text">LinguaHub</span>
      </div>
      <div class="nav-links">${navLinks}</div>
      <div class="nav-right">
        <div class="lang-selector">${langChips}</div>
        ${userArea}
      </div>
    </div>`;

  // 绑定导航事件
  $all("#navbar [data-path]").forEach(el => el.addEventListener("click", () => {
    const p = el.dataset.path;
    if (State.user || p === "/" || p === "/languages" || p === "/login" || p === "/register") {
      navigate(p);
    } else {
      toast("请先登录", "warning");
      navigate("/login");
    }
  }));

  $all("#navbar .lang-chip").forEach(el => el.addEventListener("click", () => {
    State.activeLang = el.dataset.lang;
    localStorage.setItem("linguahub_lang", State.activeLang);
    render();
  }));

  const logoutBtn = $("#logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", async () => {
    try { await Api.logout(); } catch {}
    clearToken();
    State.user = null;
    toast("已退出登录", "info");
    navigate("/");
  });

  const loginBtn = $("#loginBtn");
  if (loginBtn) loginBtn.addEventListener("click", () => navigate("/login"));
  const registerBtn = $("#registerBtn");
  if (registerBtn) registerBtn.addEventListener("click", () => navigate("/register"));
}

// ==================================================================
// 各个页面
// ==================================================================

// ---------- 首页 ----------
function pageHome() {
  const langFlag = LANG_FLAGS[State.activeLang] || "🌍";
  const langName = LANG_NAMES[State.activeLang] || "语言";

  return `
    <div class="hero">
      <h1>开启你的${langName}之旅 ✨</h1>
      <p>沉浸式语言学习平台 — 分级课程、互动练习、口语跟读、社区陪伴</p>
      <div class="hero-actions">
        ${State.user
          ? `<button class="btn btn-primary btn-lg" data-path="/dashboard">📊 进入学习中心</button>
             <button class="btn btn-secondary btn-lg" data-path="/courses?lang=${State.activeLang}">${langFlag} 浏览${langName}课程</button>`
          : `<button class="btn btn-primary btn-lg" data-path="/register">🚀 免费开始学习</button>
             <button class="btn btn-secondary btn-lg" data-path="/login">已有账号 · 登录</button>`}
      </div>
    </div>

    <div class="page-header" style="text-align:center; margin-top: var(--2xl);">
      <h1>我们提供什么</h1>
      <p>6 大核心模块，覆盖从入门到精通的完整路径</p>
    </div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="feature-icon">📚</div>
        <h3>分级课程体系</h3>
        <p>A1 到 C1，5 个难度等级，循序渐进的学习路径</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">📝</div>
        <h3>单词记忆</h3>
        <p>闪卡模式 + 例句引导，科学间隔重复强化记忆</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🎧</div>
        <h3>语法精讲</h3>
        <p>填空选择互动练习，即时反馈巩固每一个知识点</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🎤</div>
        <h3>口语跟读</h3>
        <p>地道例句反复跟读，训练语感和发音节奏</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">👂</div>
        <h3>听力训练</h3>
        <p>真实场景对话听力，从泛听到精听层层进阶</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🔥</div>
        <h3>成就激励</h3>
        <p>连续学习打卡 + 成就解锁系统，让学习像玩游戏一样上瘾</p>
      </div>
    </div>`;
}

// ---------- 选择语言 ----------
function pageLanguages() {
  const cards = State.langs.map(l => `
    <div class="language-card" data-lang="${l.code}">
      <div class="lang-flag">${l.flag}</div>
      <div class="lang-name">${l.name}</div>
      <div class="lang-native">${l.native_name}</div>
      <div class="lang-desc">${l.description}</div>
    </div>
  `).join("");

  return `
    <div class="page-header">
      <h1>🌍 选择你想学习的语言</h1>
      <p>点击任意语言，开始你的沉浸式学习之旅</p>
    </div>
    <div class="language-grid">${cards}</div>`;
}

// ---------- 课程列表 ----------
async function pageCourses(lang) {
  const language = lang || State.activeLang;
  const courses = await Api.courses(language);

  if (courses.length === 0) {
    return `<div class="empty-state"><div class="empty-icon">📭</div><h2>暂无课程</h2></div>`;
  }

  const progress = State.user ? await Api.progress(language) : null;

  const cards = courses.map(c => {
    const prog = progress?.courses?.find(p => p.id === c.id);
    const pct = prog ? Math.round(prog.completed_lessons / prog.total_lessons * 100) : 0;
    return `
      <div class="course-card" data-course-id="${c.id}">
        <div class="course-banner" style="background: linear-gradient(135deg, ${c.color}22, ${c.color}55);">
          ${c.icon}
        </div>
        <div class="course-info">
          <span class="course-level-badge" style="background: ${c.color}22; color: ${c.color};">${c.level}</span>
          <div class="course-title">${c.title}</div>
          <div class="course-subtitle">${c.subtitle || ""}</div>
          <div class="course-progress">
            <div class="progress-bar"><div class="progress-fill" style="width: ${pct}%"></div></div>
            <div class="progress-text">
              <span>${prog ? prog.completed_lessons : 0}/${c.total_lessons} 课时</span>
              <span>${pct}%</span>
            </div>
          </div>
        </div>
      </div>`;
  }).join("");

  return `
    <div class="page-header">
      <h1>${LANG_FLAGS[language] || "🌍"} ${LANG_NAMES[language] || language}课程</h1>
      <p>点击课程卡片查看详细课时列表</p>
    </div>
    <div class="course-grid">${cards}</div>`;
}

// ---------- 课程详情（课时列表） ----------
async function pageCourse(courseId) {
  if (!courseId) return '<div class="empty-state"><h2>未指定课程</h2></div>';
  const data = await Api.course(courseId);
  const course = data.course;
  const lessons = data.lessons;

  let vocabCount = 0, grammarCount = 0, speakingCount = 0, listeningCount = 0;
  lessons.forEach(l => {
    if (l.lesson_type === "vocab") vocabCount++;
    else if (l.lesson_type === "grammar") grammarCount++;
    else if (l.lesson_type === "speaking") speakingCount++;
    else listeningCount++;
  });
  const completedCount = lessons.filter(l => l.completed).length;

  const items = lessons.map(l => {
    const typeClass = `type-${l.lesson_type}`;
    const done = l.completed;
    return `
      <div class="lesson-item ${done ? "completed" : ""}" data-lesson-id="${l.id}">
        <div class="lesson-idx">${l.order_index}</div>
        <span class="lesson-type-badge ${typeClass}">${LESSON_TYPE_LABELS[l.lesson_type]}</span>
        <div class="lesson-info">
          <div class="lesson-title">${l.title}</div>
          <div class="lesson-meta">约 ${l.duration_min} 分钟${l.score ? ` · 得分 ${l.score}` : ""}</div>
        </div>
        <div class="lesson-status">${done ? "✅" : "▶️"}</div>
      </div>`;
  }).join("");

  return `
    <div class="page-header">
      <h1>${course.icon} ${course.title}</h1>
      <p>${course.subtitle || ""}</p>
      <div style="margin-top: var(--md); display: flex; gap: var(--lg); flex-wrap: wrap;">
        <span class="stat-sub">📝 词汇 ${vocabCount}</span>
        <span class="stat-sub">🎧 语法 ${grammarCount}</span>
        <span class="stat-sub">🎤 口语 ${speakingCount}</span>
        <span class="stat-sub">👂 听力 ${listeningCount}</span>
        <span class="stat-sub" style="color: var(--accent-green);">✅ 已完成 ${completedCount}/${lessons.length}</span>
      </div>
    </div>
    <div class="lesson-list">${items}</div>`;
}

// ---------- 学习模块（互动答题） ----------
async function pageLesson(lessonId) {
  if (!lessonId) return '<div class="empty-state"><h2>未指定课时</h2></div>';
  if (!State.user) {
    toast("请先登录开始学习", "warning");
    navigate("/login");
    return "";
  }

  const data = await Api.lesson(lessonId);
  const lesson = data.lesson;
  const content = data.content;
  const questions = content.questions || [];

  const wrapper = document.createElement("div");
  wrapper.className = "lesson-view";
  wrapper.innerHTML = `
    <div class="lesson-header">
      <div class="lesson-progress-bar"><div class="lesson-progress-fill" id="lessonProgress" style="width:0%"></div></div>
      <div class="question-counter" id="questionCounter">0 / ${questions.length}</div>
      <h2>${lesson.title}</h2>
    </div>
    <div id="questionArea"></div>
    <div id="lessonResult"></div>`;

  const pageEl = wrapper;
  document.getElementById("page").innerHTML = "";
  document.getElementById("page").appendChild(wrapper);

  // 答题逻辑
  let currentIdx = 0;
  let correctCount = 0;
  let answered = false;

  function renderQuestion() {
    if (currentIdx >= questions.length) {
      showResult();
      return;
    }
    answered = false;
    const q = questions[currentIdx];
    $("#lessonProgress").style.width = `${currentIdx / questions.length * 100}%`;
    $("#questionCounter").textContent = `${currentIdx + 1} / ${questions.length}`;

    const area = $("#questionArea");
    area.innerHTML = "";

    if (q.type === "word-card") {
      area.innerHTML = `
        <div class="question-card word-card">
          <div class="word-main">${q.word}</div>
          <button class="btn btn-primary" id="showAnswerBtn">🔄 显示释义</button>
          <div class="word-translation" style="display:none; margin-top: var(--md);">${q.translation}</div>
          <div class="word-example" style="display:none; margin-top: var(--md);">${q.example}</div>
        </div>
        <div class="result-actions">
          <button class="btn btn-ghost" id="nextWordBtn">认识了 · 继续</button>
        </div>`;
      $("#showAnswerBtn").onclick = () => {
        $(".word-translation").style.display = "block";
        $(".word-example").style.display = "block";
      };
      $("#nextWordBtn").onclick = () => { correctCount++; currentIdx++; renderQuestion(); };

    } else if (q.type === "fill-blank") {
      const opts = q.options.map((o, i) =>
        `<button class="option-btn" data-idx="${i}">${String.fromCharCode(65 + i)}. ${o}</button>`
      ).join("");
      area.innerHTML = `
        <div class="question-card">
          <div class="question-prompt">${q.prompt}</div>
          <div class="options-grid">${opts}</div>
        </div>`;
      $all(".option-btn").forEach(btn => btn.onclick = () => handleFillBlank(q, btn));

    } else if (q.type === "speaking") {
      area.innerHTML = `
        <div class="question-card">
          <div class="sentence-display">${q.sentence}</div>
          <div class="translation-hint">${q.translation}</div>
          <div class="speaking-controls">
            <button class="record-btn" id="recordBtn" title="点击开始/停止录音">🎤</button>
            <button class="play-btn" id="playSentenceBtn">🔊 播放例句</button>
          </div>
        </div>
        <div class="result-actions" style="margin-top: var(--md); justify-content: center;">
          <button class="btn btn-primary" id="nextSpeakingBtn">跟读完成 · 继续</button>
        </div>`;
      $("#recordBtn").onclick = () => {
        const btn = $("#recordBtn");
        const recording = btn.classList.toggle("recording");
        if (recording) {
          btn.textContent = "⏹";
          toast("录音中... 点击停止", "info");
        } else {
          btn.textContent = "🎤";
          toast("录音结束", "success");
        }
      };
      $("#playSentenceBtn").onclick = () => {
        if ("speechSynthesis" in window) {
          const u = new SpeechSynthesisUtterance(q.sentence);
          u.lang = lesson.lesson_type === "speaking" ? "en-US" : "en-US";
          speechSynthesis.speak(u);
        }
      };
      $("#nextSpeakingBtn").onclick = () => { currentIdx++; renderQuestion(); };

    } else if (q.type === "listening") {
      const opts = q.options.map((o, i) =>
        `<button class="option-btn" data-idx="${i}">${o}</button>`
      ).join("");
      area.innerHTML = `
        <div class="question-card">
          <div class="sentence-display" id="listenTranscript" style="opacity: 0.2; user-select: none;">${q.transcript}</div>
          <div class="listening-controls" style="margin-bottom: var(--lg);">
            <button class="play-btn" id="playListenBtn">🔊 播放音频</button>
            <button class="btn btn-ghost" id="revealBtn">👁 显示原文</button>
          </div>
          <div class="question-prompt" style="font-size: 16px;">Q: ${q.q}</div>
          <div class="options-grid">${opts}</div>
        </div>`;
      $("#playListenBtn").onclick = () => {
        if ("speechSynthesis" in window) {
          speechSynthesis.speak(new SpeechSynthesisUtterance(q.transcript));
        }
      };
      $("#revealBtn").onclick = () => { $("#listenTranscript").style.opacity = "1"; };
      $all(".option-btn").forEach(btn => btn.onclick = () => handleFillBlank(q, btn));
    }
  }

  function handleFillBlank(q, btn) {
    if (answered) return;
    answered = true;
    const idx = Number(btn.dataset.idx);
    const isCorrect = idx === q.answer;
    if (isCorrect) {
      btn.classList.add("correct");
      correctCount++;
    } else {
      btn.classList.add("wrong");
      $all(".option-btn").forEach(b => {
        if (Number(b.dataset.idx) === q.answer) b.classList.add("correct");
      });
    }
    $all(".option-btn").forEach(b => b.classList.add("disabled"));

    setTimeout(() => { currentIdx++; renderQuestion(); }, 900);
  }

  function showResult() {
    $("#lessonProgress").style.width = "100%";
    const score = Math.round(correctCount / questions.length * 100);
    const emoji = score >= 80 ? "🎉" : score >= 60 ? "👍" : "💪";
    const msg = score === 100 ? "完美！" : score >= 80 ? "太棒了！" : score >= 60 ? "做得不错！" : "继续加油！";

    $("#questionArea").innerHTML = "";
    $("#lessonResult").innerHTML = `
      <div class="result-overlay">
        <div class="result-card">
          <div class="result-emoji">${emoji}</div>
          <div class="result-score">${score}</div>
          <div class="result-label">${msg} · 答对 ${correctCount}/${questions.length}</div>
          <div class="result-actions">
            <button class="btn btn-secondary" id="retryBtn">再练一次</button>
            <button class="btn btn-primary" id="finishBtn">完成课程</button>
          </div>
        </div>
      </div>`;

    $("#retryBtn").onclick = () => {
      currentIdx = 0; correctCount = 0;
      $("#lessonResult").innerHTML = "";
      renderQuestion();
    };
    $("#finishBtn").onclick = async () => {
      try {
        await Api.completeLesson(Number(lessonId), score, 15);
        toast(`课程完成！得分 ${score}`, "success");
        navigate(`/course?id=${lesson.course_id}`);
      } catch (err) {
        toast(err.message, "error");
      }
    };
  }

  renderQuestion();
  return ""; // 已手动注入 DOM
}

// ---------- 学习中心（仪表盘） ----------
async function pageDashboard() {
  if (!requireAuth()) return "";
  const dash = await Api.dashboard();
  const progress = dash.progress;
  const streak = dash.streak_days;
  const rec = dash.recommend;
  const ach = dash.achievements;

  const courseCards = progress.courses.map(c => {
    const pct = Math.round(c.completed_lessons / c.total_lessons * 100);
    return `
      <div class="card" style="margin-bottom: var(--md);">
        <div style="display: flex; align-items: center; gap: var(--md);">
          <div style="font-size: 32px;">${c.icon}</div>
          <div style="flex:1;">
            <div style="font-weight: 600;">${c.title}</div>
            <div style="font-size: 13px; color: var(--text-secondary);">${c.level} · ${c.completed_lessons}/${c.total_lessons} 课时</div>
          </div>
          <button class="btn btn-secondary btn-sm" data-course-id="${c.id}">继续</button>
        </div>
        <div class="progress-bar" style="margin-top: var(--md);">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      </div>`;
  }).join("");

  let recBanner = "";
  if (rec?.next) {
    recBanner = `
      <div class="recommend-banner">
        <h3>🎯 为你推荐的下一步</h3>
        <p>${rec.message}</p>
        <div style="margin-bottom: var(--md);">
          <strong>${rec.next.title}</strong>
          <span style="color: var(--text-muted); font-size: 13px;">（${rec.next.course_title}）</span>
        </div>
        <button class="btn btn-primary" data-lesson-id="${rec.next.id}">▶ 开始学习</button>
        ${rec?.review ? `<button class="btn btn-secondary" data-lesson-id="${rec.review.id}" style="margin-left: var(--sm);">🔄 复习：${rec.review.title}</button>` : ""}
      </div>`;
  }

  const recentAchievements = ach.list.filter(a => a.unlocked).slice(-3);
  const achHTML = recentAchievements.length > 0
    ? recentAchievements.map(a => `<span class="achievement-icon" title="${a.name}">${a.icon}</span>`).join(" ")
    : "还没有解锁成就 · 加油！";

  return `
    <div class="page-header">
      <h1>📊 学习中心 · 你好 ${State.user.username}！</h1>
      <p>今日也坚持学习吧，每一步都在让你变得更好</p>
    </div>

    <div class="dashboard-grid">
      <div class="stat-card green">
        <div class="stat-label">已完成课时</div>
        <div class="stat-value green">${progress.overall.completed}</div>
        <div class="stat-sub">总计 ${progress.overall.total} 课时</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">连续学习</div>
        <div class="stat-value orange">${streak} 天</div>
        <div class="stat-sub">${streak >= 7 ? "✨ 太棒了，继续保持！" : "坚持，坚持！"}</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">总体进度</div>
        <div class="stat-value blue">${progress.overall.percent}%</div>
        <div class="stat-sub">${progress.overall.percent >= 50 ? "过了一半啦 🎉" : "稳步前进中"}</div>
      </div>
      <div class="stat-card pink">
        <div class="stat-label">已解锁成就</div>
        <div class="stat-value pink">${ach.unlocked}/${ach.total}</div>
        <div class="stat-sub">${achHTML}</div>
      </div>
    </div>

    ${recBanner}

    <h2 style="margin: var(--lg) 0 var(--md); font-size: 18px;">我的课程</h2>
    ${courseCards || '<div class="empty-state"><p>还没有选任何课程，去 <a href="#/languages">选择语言</a> 开始吧</p></div>'}`;
}

// ---------- 成就页面 ----------
async function pageAchievements() {
  if (!requireAuth()) return "";
  const list = await Api.achievements();
  const unlocked = list.filter(a => a.unlocked).length;

  const cards = list.map(a => `
    <div class="achievement-card ${a.unlocked ? "unlocked" : "locked"}">
      <div class="achievement-icon">${a.icon}</div>
      <div class="achievement-name">${a.name}</div>
      <div class="achievement-desc">${a.description}</div>
      ${a.unlocked ? '<div style="color: var(--accent-orange); font-size: 12px; margin-top: var(--xs);">✅ 已解锁</div>' : ""}
    </div>
  `).join("");

  return `
    <div class="page-header">
      <h1>🏆 成就殿堂</h1>
      <p>已解锁 ${unlocked} / ${list.length} — 继续努力解锁更多精彩！</p>
    </div>
    <div class="achievement-grid">${cards}</div>`;
}

// ---------- 社区 ----------
async function pageCommunity() {
  const posts = await Api.community();

  let formHTML = "";
  if (State.user) {
    formHTML = `
      <div class="post-form">
        <textarea class="form-input form-textarea" id="postContent" placeholder="分享你的学习心得、遇到的问题或今日打卡..." maxlength="500"></textarea>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: var(--md);">
          <span class="stat-sub">最多 500 字</span>
          <button class="btn btn-primary btn-sm" id="submitPost">📢 发布</button>
        </div>
      </div>`;
  } else {
    formHTML = `<div class="card" style="text-align: center; margin-bottom: var(--lg);">
      <p style="margin-bottom: var(--md);">登录后即可发布和互动</p>
      <button class="btn btn-primary btn-sm" data-path="/login">去登录</button>
    </div>`;
  }

  const list = posts.length > 0 ? posts.map(p => {
    const avatarColor = `hsl(${(p.user_id * 37) % 360}, 65%, 55%)`;
    return `
      <div class="post-card" data-post-id="${p.id}">
        <div class="post-header">
          <div class="avatar" style="background: ${avatarColor};">${getInitials(p.username)}</div>
          <div style="flex:1;">
            <div style="font-weight: 600;">${p.username}</div>
            <div style="font-size: 12px; color: var(--text-muted);">${new Date(p.created_at).toLocaleString("zh-CN")}</div>
          </div>
          <span class="lesson-type-badge type-vocab">${LANG_FLAGS[p.target_language] || "🌍"} ${LANG_NAMES[p.target_language] || p.target_language}</span>
        </div>
        <div class="post-body">${escapeHTML(p.content)}</div>
        <div class="post-footer">
          <button class="like-btn" data-like="${p.id}">❤️ 点赞 (${p.likes})</button>
          <span>#${p.category}</span>
        </div>
      </div>`;
  }).join("") : `<div class="empty-state"><div class="empty-icon">💬</div><h2>还没有动态</h2><p>发布第一条学习心得吧！</p></div>`;

  return `
    <div class="page-header">
      <h1>💬 学习社区</h1>
      <p>和同好一起成长，分享每一次进步</p>
    </div>
    ${formHTML}
    <div class="post-list">${list}</div>`;
}

function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------- 登录 / 注册 ----------
function pageLogin(isRegister) {
  const mode = isRegister ? "register" : "login";
  const title = isRegister ? "创建账号" : "欢迎回来";
  const subtitle = isRegister ? "开启你的语言学习之旅 🚀" : "继续你的学习进度 💪";

  const extraFields = isRegister ? `
    <div class="form-group">
      <label class="form-label">邮箱（可选）</label>
      <input class="form-input" type="email" id="regEmail" placeholder="you@example.com" />
    </div>
    <div class="form-group">
      <label class="form-label">目标语言</label>
      <select class="form-input" id="regLang">
        ${State.langs.map(l => `<option value="${l.code}" ${l.code === State.activeLang ? "selected" : ""}>${l.flag} ${l.name}</option>`).join("")}
      </select>
    </div>` : "";

  return `
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-title">${title}</div>
        <div class="auth-subtitle">${subtitle}</div>
        <form id="authForm">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input class="form-input" type="text" id="authUsername" required minlength="2" placeholder="2-30 字符" />
          </div>
          <div class="form-group">
            <label class="form-label">密码</label>
            <input class="form-input" type="password" id="authPassword" required minlength="4" placeholder="至少 4 位" />
          </div>
          ${extraFields}
          <button type="submit" class="btn btn-primary" style="width:100%; margin-top: var(--md);">
            ${isRegister ? "🚀 创建账号" : "🔐 登录"}
          </button>
        </form>
        <div class="auth-switch">
          ${isRegister
            ? '已有账号？<a href="#/login">去登录</a>'
            : '还没有账号？<a href="#/register">立即注册</a>'}
        </div>
      </div>
    </div>`;
}

// ---------- 页面事件绑定 ----------
function bindPageEvents() {
  // 语言选择
  $all("[data-lang]").forEach(el => el.addEventListener("click", () => {
    const code = el.dataset.lang;
    State.activeLang = code;
    localStorage.setItem("linguahub_lang", code);
    navigate(`/courses?lang=${code}`);
  }));

  // 课程卡片
  $all("[data-course-id]").forEach(el => el.addEventListener("click", () => {
    navigate(`/course?id=${el.dataset.courseId}`);
  }));

  // 课时项目
  $all("[data-lesson-id]").forEach(el => el.addEventListener("click", () => {
    const id = el.dataset.lessonId;
    if (requireAuth()) navigate(`/lesson?id=${id}`);
  }));

  // 点赞
  $all("[data-like]").forEach(el => el.addEventListener("click", async () => {
    try {
      await Api.likePost(Number(el.dataset.like));
      toast("点赞成功 ❤️", "success");
      render();
    } catch (err) { toast(err.message, "error"); }
  }));

  // 发布动态
  const submitPost = $("#submitPost");
  if (submitPost) submitPost.addEventListener("click", async () => {
    const content = $("#postContent").value.trim();
    if (!content) { toast("内容不能为空", "warning"); return; }
    try {
      await Api.createPost(content, "学习打卡");
      $("#postContent").value = "";
      toast("发布成功 🎉", "success");
      render();
    } catch (err) { toast(err.message, "error"); }
  });

  // 登录/注册表单
  const authForm = $("#authForm");
  if (authForm) authForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = $("#authUsername").value.trim();
    const password = $("#authPassword").value;
    try {
      if (parseHash().path === "/register") {
        const email = $("#regEmail")?.value || null;
        const lang = $("#regLang")?.value || "en";
        await Api.register(username, password, email, lang);
        toast("注册成功！正在登录...", "success");
      }
      const res = await Api.login(username, password);
      setToken(res.token);
      State.user = res.user;
      toast(`欢迎回来，${State.user.username}！`, "success");
      navigate("/dashboard");
    } catch (err) { toast(err.message, "error"); }
  });

  // 导航按钮在学习模块内不可用（lesson view 直接渲染）
  if ($("#page .lang-selector") === null) {
    // lesson 模块自己渲染了内容，不要重新绑定
  }
}

// ---------- 启动 ----------
window.addEventListener("hashchange", render);
window.addEventListener("DOMContentLoaded", () => {
  // 初始化页面骨架
  document.body.insertAdjacentHTML("afterbegin", `
    <div class="app">
      <nav class="navbar" id="navbar"></nav>
      <main class="main-content" id="page"></main>
    </div>`);
  render();
});
