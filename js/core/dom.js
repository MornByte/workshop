/**
 * DOM 工具 + UI 反馈
 * 所有页面共享的低级 DOM 操作和提示函数
 */

// ---------- 选择器 ----------
export function $(sel, root = document) {
  return root.querySelector(sel);
}
export function $all(sel, root = document) {
  return Array.from(root.querySelectorAll(sel));
}

// ---------- Toast 提示 ----------
let toastContainer;
export function toast(msg, type = "info") {
  if (!toastContainer) {
    toastContainer = document.createElement("div");
    toastContainer.className = "toast-container";
    document.body.appendChild(toastContainer);
  }
  const t = document.createElement("div");
  t.className = `toast ${type}`;
  t.textContent = msg;
  toastContainer.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

// ---------- 通用工具 ----------
export function loadingHTML(text = "加载中...") {
  return `<div class="loading"><div class="loading-spinner"></div><div>${text}</div></div>`;
}

export function getInitials(name) {
  return name ? name.slice(0, 1).toUpperCase() : "?";
}

export function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
