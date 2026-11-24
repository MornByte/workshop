/**
 * 学习中心（仪表盘）— 一站式概览
 */
import { store } from "../core/store.js";
import { Api } from "../api/client.js";
import { requireAuth } from "../core/router.js";

export async function pageDashboard() {
  if (!(await requireAuth())) return "";

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
      <h1>📊 学习中心 · 你好 ${store.user.username}！</h1>
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
