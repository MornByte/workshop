/**
 * 首页 — 产品介绍 + 行动号召
 */
import { store } from "../core/store.js";
import { LANG_FLAGS, LANG_NAMES } from "../config.js";

export function pageHome() {
  const langFlag = LANG_FLAGS[store.activeLang] || "🌍";
  const langName = LANG_NAMES[store.activeLang] || "语言";

  return `
    <div class="hero">
      <h1>开启你的${langName}之旅 ✨</h1>
      <p>沉浸式语言学习平台 — 分级课程、互动练习、口语跟读、社区陪伴</p>
      <div class="hero-actions">
        ${store.user
          ? `<button class="btn btn-primary btn-lg" data-path="/dashboard">📊 进入学习中心</button>
             <button class="btn btn-secondary btn-lg" data-path="/courses?lang=${store.activeLang}">${langFlag} 浏览${langName}课程</button>`
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
