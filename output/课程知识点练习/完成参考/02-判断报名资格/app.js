const shiJianKuang = document.getElementById("day");
const jiChuKuang = document.getElementById("level");
const judgeButton = document.getElementById("judge-button");
const jieGuo = document.getElementById("message");

judgeButton.addEventListener("click", () => {
  const zhouSan = shiJianKuang.value === "zhouSan";
  const youDianJiChu = jiChuKuang.value === "youDianJiChu";

  const nengBao = zhouSan && youDianJiChu;

  if (nengBao) {
    jieGuo.textContent = "可以报。周三能来，而且有点基础。";
  } else if (!zhouSan) {
    jieGuo.textContent = "不能报。机器人社在周三活动。";
  } else {
    jieGuo.textContent = "不能报。机器人社需要有点基础。";
  }
});
