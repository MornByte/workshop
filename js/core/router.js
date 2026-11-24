/**
 * 路由核心 — Hash 路由解析 + 主渲染函数 + 页面事件绑定
 * 这是前端的"调度中心"
 */
import { $, $all, toast, loadingHTML } from "./dom.js";
import { store, restoreSession, setActiveLang } from "./store.js";
import { Api } from "../api/client.js";
import { renderNavbar } from "./navbar.js";

// 页面渲染函数（集中 import，避免循环依赖问题）
import { pageHome } from "../pages/home.js";
import { pageLanguages } from "../pages/languages.js";
import { pageCourses, pageCourse } from "../pages/courses.js";
import { pageLesson } from "../pages/lesson.js";
import { pageDashboard } from "../pages/dashboard.js";
import { pageAchievements } from "../pages/achievements.js";
import { pageCommunity } from "../pages/community.js";
import { pageLogin } from "../pages/auth.js";

// ---------- 路由解析 ----------
export function parseHash() {
  // #/courses?lang=en
  const hash = window.location.hash.slice(1) || "/";
  const [path, queryStr] = hash.split("?");
  const params = {};
  if (queryStr) {
    queryStr.split("&").forEach(kv => {
      const [k, v] = kv.split("=");
      if (k) params[k] = decodeURIComponent(v || "");
    });
  }
  const segments = path.split("/").filter(Boolean);
  return { path, segments, params };
}

export function navigate(path) {
  window.location.hash = path;
}

// ---------- 认证检查（页面调用）----------
export async function requireAuth() {
  if (!store.user) {
    toast("请先登录", "warning");
    navigate("/login");
    return false;
  }
  return true;
}

// ---------- 主渲染 ----------
export async function render() {
  const app = $("#page");
  app.innerHTML = loadingHTML();

  // 恢复登录态
  await restoreSession(Api);

  // 加载语种列表
  if (store.langs.length === 0) {
    try { store.langs = await Api.languages(); } catch { /* ignore */ }
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
        // lesson 页面自己注入 DOM，不覆盖 innerHTML
        await pageLesson(route.params.id);
        break;
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

  // 页面进入动画
  app.classList.remove("page-enter");
  void app.offsetWidth; // force reflow
  app.classList.add("page-enter");

  // 绑定页面内事件
  bindPageEvents();
}

// ---------- 页面事件绑定 ----------
export function bindPageEvents() {
  // 语言选择卡片
  $all("[data-lang]").forEach(el => el.addEventListener("click", () => {
    const code = el.dataset.lang;
    setActiveLang(code);
    navigate(`/courses?lang=${code}`);
  }));

  // 课程卡片 → 课程详情
  $all("[data-course-id]").forEach(el => el.addEventListener("click", () => {
    navigate(`/course?id=${el.dataset.courseId}`);
  }));

  // 课时项目 → 学习页
  $all("[data-lesson-id]").forEach(el => el.addEventListener("click", () => {
    const id = el.dataset.lessonId;
    requireAuth().then(ok => ok && navigate(`/lesson?id=${id}`));
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

  // 登录 / 注册表单
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
      localStorage.setItem("linguahub_token", res.token);
      store.user = res.user;
      toast(`欢迎回来，${store.user.username}！`, "success");
      navigate("/dashboard");
    } catch (err) { toast(err.message, "error"); }
  });
}
