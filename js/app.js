/**
 * LinguaHub · 前端应用入口（薄壳）
 * 只负责：页面骨架注入 + 监听 hashchange 触发 render
 * 所有业务逻辑在 core/ 和 pages/ 模块中
 */
import { render } from "./core/router.js";

// 监听 URL hash 变化 → 重新渲染
window.addEventListener("hashchange", render);

// DOM 就绪后注入骨架并首次渲染
window.addEventListener("DOMContentLoaded", () => {
  document.body.insertAdjacentHTML("afterbegin", `
    <div class="app">
      <nav class="navbar" id="navbar"></nav>
      <main class="main-content" id="page"></main>
    </div>`);
  render();
});
