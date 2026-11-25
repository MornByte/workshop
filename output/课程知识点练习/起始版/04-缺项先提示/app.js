const biaoDan = document.getElementById("signup");
const checkButton = document.getElementById("check-button");
const zhouYiKuang = document.getElementById("zhouYi");
const zhouSanKuang = document.getElementById("zhouSan");
const nianJiTiShi = document.getElementById("grade-hint");
const shiJianTiShi = document.getElementById("time-hint");
const jieGuo = document.getElementById("message");

function clearFeedback() {
  nianJiTiShi.textContent = "";
  shiJianTiShi.textContent = "";
  jieGuo.textContent = "";
}

checkButton.addEventListener("click", () => {
  clearFeedback();

  const nianJiXuanXiang = biaoDan.querySelector('input[name="nianJi"]:checked');
  const youShiJian = zhouYiKuang.checked || zhouSanKuang.checked;
  const queNianJi = nianJiXuanXiang === null;
  const queShiJian = !youShiJian;

  // 04 · 缺项提示

  if (zhouSanKuang.checked) {
    jieGuo.textContent = "可以报。周三能参加活动。";
  } else {
    jieGuo.textContent = "不能报。活动安排在周三。";
  }
});

biaoDan.addEventListener("reset", () => {
  clearFeedback();
  jieGuo.textContent = "还没判断";
});
