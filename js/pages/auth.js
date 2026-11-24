/**
 * 登录 / 注册页面（同一个表单，通过 isRegister 切换）
 */
import { store } from "../core/store.js";

export function pageLogin(isRegister) {
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
        ${store.langs.map(l => `<option value="${l.code}" ${l.code === store.activeLang ? "selected" : ""}>${l.flag} ${l.name}</option>`).join("")}
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
