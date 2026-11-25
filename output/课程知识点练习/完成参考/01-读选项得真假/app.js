const jiChuKuang = document.getElementById("level");
const readButton = document.getElementById("read-button");
const duDaoDeZhi = document.getElementById("read-level");
const biJiaoJieGuo = document.getElementById("check-result");

readButton.addEventListener("click", () => {
  const jiChuZhi = jiChuKuang.value;
  const youDianJiChu = jiChuZhi === "youDianJiChu";
  duDaoDeZhi.textContent = jiChuZhi;
  biJiaoJieGuo.textContent = youDianJiChu;
});

const nianLingKuang = document.getElementById("age");
const compareAgeButton = document.getElementById("compare-age");
const duDaoDeNianLing = document.getElementById("read-age");
const kuanSongJieGuo = document.getElementById("loose-result");
const yanGeJieGuo = document.getElementById("strict-result");

compareAgeButton.addEventListener("click", () => {
  const nianLingZhi = nianLingKuang.value;
  duDaoDeNianLing.textContent = '"' + nianLingZhi + '"';

  kuanSongJieGuo.textContent = nianLingZhi == 16;
  yanGeJieGuo.textContent = nianLingZhi === 16;
});
