/**
 * 成就殿堂
 */
import { Api } from "../api/client.js";
import { requireAuth } from "../core/router.js";

export async function pageAchievements() {
  if (!(await requireAuth())) return "";

  const list = await Api.achievements();
  const unlocked = list.filter(a => a.unlocked).length;

  const cards = list.map(a => `
    <div class="achievement-card ${a.unlocked ? "unlocked" : "locked"}">
      <div class="achievement-icon">${a.icon}</div>
      <div class="achievement-name">${a.name}</div>
      <div class="achievement-desc">${a.description}</div>
      ${a.unlocked ? '<div style="color: var(--accent-orange); font-size: 12px; margin-top: var(--xs);">✅ 已解锁</div>' : ""}
    </div>
  `).join("");

  return `
    <div class="page-header">
      <h1>🏆 成就殿堂</h1>
      <p>已解锁 ${unlocked} / ${list.length} — 继续努力解锁更多精彩！</p>
    </div>
    <div class="achievement-grid">${cards}</div>`;
}
