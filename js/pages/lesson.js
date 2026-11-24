/**
 * 学习模块页 — 互动答题（词汇闪卡 / 语法填空 / 口语跟读 / 听力）
 * 这个页面比较特殊：直接操作 DOM 注入，不返回 HTML 字符串
 */
import { store } from "../core/store.js";
import { Api } from "../api/client.js";
import { $, $all, toast } from "../core/dom.js";

export async function pageLesson(lessonId) {
  if (!lessonId) return '<div class="empty-state"><h2>未指定课时</h2></div>';
  if (!store.user) {
    toast("请先登录开始学习", "warning");
    // 跳转到登录 — 延迟导入避免循环依赖顶层调用
    import("../core/router.js").then(({ navigate }) => navigate("/login"));
    return "";
  }

  const data = await Api.lesson(lessonId);
  const lesson = data.lesson;
  const questions = (data.content?.questions) || [];

  const wrapper = document.createElement("div");
  wrapper.className = "lesson-view";
  wrapper.innerHTML = `
    <div class="lesson-header">
      <div class="lesson-progress-bar"><div class="lesson-progress-fill" id="lessonProgress" style="width:0%"></div></div>
      <div class="question-counter" id="questionCounter">0 / ${questions.length}</div>
      <h2>${lesson.title}</h2>
    </div>
    <div id="questionArea"></div>
    <div id="lessonResult"></div>`;

  document.getElementById("page").innerHTML = "";
  document.getElementById("page").appendChild(wrapper);

  // ---------- 答题状态 ----------
  let currentIdx = 0;
  let correctCount = 0;
  let answered = false;

  function renderQuestion() {
    if (currentIdx >= questions.length) {
      showResult();
      return;
    }
    answered = false;
    const q = questions[currentIdx];
    $("#lessonProgress").style.width = `${currentIdx / questions.length * 100}%`;
    $("#questionCounter").textContent = `${currentIdx + 1} / ${questions.length}`;

    const area = $("#questionArea");
    area.innerHTML = "";

    if (q.type === "word-card") {
      area.innerHTML = `
        <div class="question-card word-card">
          <div class="word-main">${q.word}</div>
          <button class="btn btn-primary" id="showAnswerBtn">🔄 显示释义</button>
          <div class="word-translation" style="display:none; margin-top: var(--md);">${q.translation}</div>
          <div class="word-example" style="display:none; margin-top: var(--md);">${q.example}</div>
        </div>
        <div class="result-actions">
          <button class="btn btn-ghost" id="nextWordBtn">认识了 · 继续</button>
        </div>`;
      $("#showAnswerBtn").onclick = () => {
        $(".word-translation").style.display = "block";
        $(".word-example").style.display = "block";
      };
      $("#nextWordBtn").onclick = () => { correctCount++; currentIdx++; renderQuestion(); };

    } else if (q.type === "fill-blank") {
      const opts = q.options.map((o, i) =>
        `<button class="option-btn" data-idx="${i}">${String.fromCharCode(65 + i)}. ${o}</button>`
      ).join("");
      area.innerHTML = `
        <div class="question-card">
          <div class="question-prompt">${q.prompt}</div>
          <div class="options-grid">${opts}</div>
        </div>`;
      $all(".option-btn").forEach(btn => (btn.onclick = () => handleOption(q, btn)));

    } else if (q.type === "speaking") {
      area.innerHTML = `
        <div class="question-card">
          <div class="sentence-display">${q.sentence}</div>
          <div class="translation-hint">${q.translation}</div>
          <div class="speaking-controls">
            <button class="record-btn" id="recordBtn" title="点击开始/停止录音">🎤</button>
            <button class="play-btn" id="playSentenceBtn">🔊 播放例句</button>
          </div>
        </div>
        <div class="result-actions" style="margin-top: var(--md); justify-content: center;">
          <button class="btn btn-primary" id="nextSpeakingBtn">跟读完成 · 继续</button>
        </div>`;
      $("#recordBtn").onclick = () => {
        const btn = $("#recordBtn");
        const recording = btn.classList.toggle("recording");
        btn.textContent = recording ? "⏹" : "🎤";
        toast(recording ? "录音中... 点击停止" : "录音结束", "info");
      };
      $("#playSentenceBtn").onclick = () => {
        if ("speechSynthesis" in window) {
          speechSynthesis.speak(new SpeechSynthesisUtterance(q.sentence));
        }
      };
      $("#nextSpeakingBtn").onclick = () => { currentIdx++; renderQuestion(); };

    } else if (q.type === "listening") {
      const opts = q.options.map((o, i) =>
        `<button class="option-btn" data-idx="${i}">${o}</button>`
      ).join("");
      area.innerHTML = `
        <div class="question-card">
          <div class="sentence-display" id="listenTranscript" style="opacity: 0.2; user-select: none;">${q.transcript}</div>
          <div class="listening-controls" style="margin-bottom: var(--lg);">
            <button class="play-btn" id="playListenBtn">🔊 播放音频</button>
            <button class="btn btn-ghost" id="revealBtn">👁 显示原文</button>
          </div>
          <div class="question-prompt" style="font-size: 16px;">Q: ${q.q}</div>
          <div class="options-grid">${opts}</div>
        </div>`;
      $("#playListenBtn").onclick = () => {
        if ("speechSynthesis" in window) {
          speechSynthesis.speak(new SpeechSynthesisUtterance(q.transcript));
        }
      };
      $("#revealBtn").onclick = () => { $("#listenTranscript").style.opacity = "1"; };
      $all(".option-btn").forEach(btn => (btn.onclick = () => handleOption(q, btn)));
    }
  }

  function handleOption(q, btn) {
    if (answered) return;
    answered = true;
    const idx = Number(btn.dataset.idx);
    if (idx === q.answer) {
      btn.classList.add("correct");
      correctCount++;
    } else {
      btn.classList.add("wrong");
      $all(".option-btn").forEach(b => {
        if (Number(b.dataset.idx) === q.answer) b.classList.add("correct");
      });
    }
    $all(".option-btn").forEach(b => b.classList.add("disabled"));
    setTimeout(() => { currentIdx++; renderQuestion(); }, 900);
  }

  async function finish() {
    try {
      const score = Math.round(correctCount / questions.length * 100);
      await Api.completeLesson(Number(lessonId), score, 15);
      toast(`课程完成！得分 ${score}`, "success");
      const { navigate } = await import("../core/router.js");
      navigate(`/course?id=${lesson.course_id}`);
    } catch (err) {
      toast(err.message, "error");
    }
  }

  function showResult() {
    $("#lessonProgress").style.width = "100%";
    const score = Math.round(correctCount / questions.length * 100);
    const emoji = score >= 80 ? "🎉" : score >= 60 ? "👍" : "💪";
    const msg = score === 100 ? "完美！" : score >= 80 ? "太棒了！" : score >= 60 ? "做得不错！" : "继续加油！";

    $("#questionArea").innerHTML = "";
    $("#lessonResult").innerHTML = `
      <div class="result-overlay">
        <div class="result-card">
          <div class="result-emoji">${emoji}</div>
          <div class="result-score">${score}</div>
          <div class="result-label">${msg} · 答对 ${correctCount}/${questions.length}</div>
          <div class="result-actions">
            <button class="btn btn-secondary" id="retryBtn">再练一次</button>
            <button class="btn btn-primary" id="finishBtn">完成课程</button>
          </div>
        </div>
      </div>`;

    $("#retryBtn").onclick = () => {
      currentIdx = 0; correctCount = 0;
      $("#lessonResult").innerHTML = "";
      renderQuestion();
    };
    $("#finishBtn").onclick = finish;
  }

  renderQuestion();
  return ""; // 已手动注入 DOM
}
