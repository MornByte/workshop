/**
 * 课程列表 + 课程详情（课时列表）
 */
import { store } from "../core/store.js";
import { Api } from "../api/client.js";
import { LANG_FLAGS, LANG_NAMES, LESSON_TYPE_LABELS } from "../config.js";

// 课程列表页
export async function pageCourses(lang) {
  const language = lang || store.activeLang;
  const courses = await Api.courses(language);

  if (courses.length === 0) {
    return `<div class="empty-state"><div class="empty-icon">📭</div><h2>暂无课程</h2></div>`;
  }

  const progress = store.user ? await Api.progress(language) : null;

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

// 课程详情页（含课时列表）
export async function pageCourse(courseId) {
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
