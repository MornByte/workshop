const zhouYiKuang = document.getElementById("zhouYi");
const zhouSanKuang = document.getElementById("zhouSan");
const zhouWuKuang = document.getElementById("zhouWu");
const jiChuKuang = document.getElementById("level");
const recommendButton = document.getElementById("recommend-button");
const robotCard = document.getElementById("robot");
const choirCard = document.getElementById("choir");
const basketCard = document.getElementById("basket");
const noMatch = document.getElementById("no-match");
const waiting = document.getElementById("waiting");

function xianShiTuiJian(tuiJian) {
  robotCard.hidden = tuiJian !== "机器人社";
  choirCard.hidden = tuiJian !== "合唱团";
  basketCard.hidden = tuiJian !== "篮球社";
  noMatch.hidden = tuiJian !== "";
  waiting.hidden = tuiJian !== undefined;
}

recommendButton.addEventListener("click", () => {
  const zhouYi = zhouYiKuang.checked;
  const zhouSan = zhouSanKuang.checked;
  const zhouWu = zhouWuKuang.checked;
  const youDianJiChu = jiChuKuang.value === "youDianJiChu";
  let tuiJian;
  if (zhouSan && youDianJiChu) {
    tuiJian = "机器人社";
  } else if (zhouWu) {
    tuiJian = "合唱团";
  } else if (zhouYi) {
    tuiJian = "篮球社";
  } else {
    tuiJian = "";
  }

  xianShiTuiJian(tuiJian);
});
