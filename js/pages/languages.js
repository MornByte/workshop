/**
 * 语言选择页
 */
import { store } from "../core/store.js";

export function pageLanguages() {
  const cards = store.langs.map(l => `
    <div class="language-card" data-lang="${l.code}">
      <div class="lang-flag">${l.flag}</div>
      <div class="lang-name">${l.name}</div>
      <div class="lang-native">${l.native_name}</div>
      <div class="lang-desc">${l.description}</div>
    </div>
  `).join("");

  return `
    <div class="page-header">
      <h1>🌍 选择你想学习的语言</h1>
      <p>点击任意语言，开始你的沉浸式学习之旅</p>
    </div>
    <div class="language-grid">${cards}</div>`;
}
