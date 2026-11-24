/**
 * 顶部导航栏渲染 — 独立模块，因为导航栏状态会随登录/语言切换变化
 */
import { $, $all, toast, getInitials } from "./dom.js";
import { store, clearToken, setActiveLang } from "./store.js";
import { Api } from "../api/client.js";
import { render, navigate, parseHash } from "./router.js";

export function renderNavbar() {
  const nav = $("#navbar");
  if (!nav) return;

  const langChips = store.langs.map(l =>
    `<span class="lang-chip ${l.code === store.activeLang ? "active" : ""}" data-nav-lang="${l.code}" title="${l.name} ${l.native_name}">${l.flag}</span>`
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
  if (store.user) {
    userArea = `
      <div class="user-info" id="userMenu">
        <div class="avatar">${getInitials(store.user.username)}</div>
        <span class="username">${store.user.username}</span>
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
    const publicPaths = ["/", "/languages", "/login", "/register"];
    if (store.user || publicPaths.includes(p)) {
      navigate(p);
    } else {
      toast("请先登录", "warning");
      navigate("/login");
    }
  }));

  // 语言切换（导航栏内的 chip）
  $all("#navbar .lang-chip").forEach(el => el.addEventListener("click", () => {
    setActiveLang(el.dataset.navLang);
    render();
  }));

  // 退出登录
  const logoutBtn = $("#logoutBtn");
  if (logoutBtn) logoutBtn.addEventListener("click", async () => {
    try { await Api.logout(); } catch { /* ignore */ }
    clearToken();
    store.user = null;
    toast("已退出登录", "info");
    navigate("/");
  });

  const loginBtn = $("#loginBtn");
  if (loginBtn) loginBtn.addEventListener("click", () => navigate("/login"));
  const registerBtn = $("#registerBtn");
  if (registerBtn) registerBtn.addEventListener("click", () => navigate("/register"));
}
