/**
 * 学习社区 — 发帖 + 点赞
 */
import { store } from "../core/store.js";
import { Api } from "../api/client.js";
import { getInitials, escapeHTML } from "../core/dom.js";
import { LANG_FLAGS, LANG_NAMES } from "../config.js";

export async function pageCommunity() {
  const posts = await Api.community();

  let formHTML = "";
  if (store.user) {
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
