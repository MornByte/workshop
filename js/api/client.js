/**
 * API 客户端 — 统一 fetch 封装 + 业务方法对象
 * 自动注入 Authorization 头，统一错误抛出
 */
import { API_BASE } from "../config.js";
import { getToken, clearToken } from "../core/store.js";

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));

  // 401 表示 token 失效，清理本地
  if (res.status === 401) {
    clearToken();
  }

  if (!res.ok) {
    throw new Error(data.detail || `请求失败 (${res.status})`);
  }
  return data;
}

export const Api = {
  // 认证
  register: (username, password, email, target_language) =>
    api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password, email, target_language }),
    }),
  login: (username, password) =>
    api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  logout: () => api("/api/auth/logout", { method: "POST" }),
  me: () => api("/api/auth/me"),

  // 语言 / 课程
  languages: () => api("/api/languages"),
  courses: (lang) => api(`/api/courses${lang ? `?language=${lang}` : ""}`),
  course: (id) => api(`/api/courses/${id}`),
  lesson: (id) => api(`/api/lessons/${id}`),
  completeLesson: (lesson_id, score, minutes_spent = 15) =>
    api(`/api/lessons/${lesson_id}/complete`, {
      method: "POST",
      body: JSON.stringify({ lesson_id, score, minutes_spent }),
    }),

  // 进度 / 成就
  progress: (lang) => api(`/api/progress${lang ? `?language=${lang}` : ""}`),
  achievements: () => api("/api/achievements"),
  dashboard: () => api("/api/dashboard"),
  recommend: (language_code) =>
    api("/api/recommend", {
      method: "POST",
      body: JSON.stringify({ language_code }),
    }),

  // 社区
  community: () => api("/api/community"),
  createPost: (content, category = "general") =>
    api("/api/community", {
      method: "POST",
      body: JSON.stringify({ content, category }),
    }),
  likePost: (post_id) => api(`/api/community/${post_id}/like`, { method: "POST" }),
};
