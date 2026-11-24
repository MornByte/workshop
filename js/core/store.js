/**
 * 全局状态管理 — 单例 store
 * 所有页面共享的可变状态（用户、语言列表、当前语言）
 * Token 持久化在 localStorage，运行时状态在内存
 */
import { LS_LANG, LS_TOKEN } from "../config.js";

export const store = {
  user: null,          // 当前登录用户对象（来自 /api/auth/me）
  langs: [],           // 语言列表 [{code, name, native_name, flag, description}]
  activeLang: localStorage.getItem(LS_LANG) || "en",
};

// ---------- Token 存取 ----------
export function getToken() {
  return localStorage.getItem(LS_TOKEN) || "";
}

export function setToken(token) {
  localStorage.setItem(LS_TOKEN, token);
}

export function clearToken() {
  localStorage.removeItem(LS_TOKEN);
}

// ---------- 语言持久化 ----------
export function setActiveLang(code) {
  store.activeLang = code;
  localStorage.setItem(LS_LANG, code);
}

// ---------- 登录态恢复（页面加载时调用一次）----------
export async function restoreSession(Api) {
  if (store.user || !getToken()) return;
  try {
    const me = await Api.me();
    store.user = me.user;
  } catch {
    clearToken();
  }
}
