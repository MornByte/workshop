/**
 * 全局配置常量 — 单一事实源
 * 任何"魔法字符串"都应该集中到这里
 */

// ---------- 后端地址 ----------
export const API_BASE = "http://127.0.0.1:8000";

// ---------- localStorage key ----------
export const LS_TOKEN = "linguahub_token";
export const LS_LANG = "linguahub_lang";

// ---------- 语言显示映射 ----------
export const LANG_NAMES = { en: "英语", ja: "日语", ko: "韩语" };
export const LANG_FLAGS = { en: "🇬🇧", ja: "🇯🇵", ko: "🇰🇷" };

// ---------- 课程等级 ----------
export const LEVEL_LABELS = {
  A1: "入门", A2: "初级", B1: "中级",
  B2: "中高级", C1: "精通", C2: "母语级",
};

// ---------- 课时类型 ----------
export const LESSON_TYPE_LABELS = {
  vocab: "词汇", grammar: "语法",
  speaking: "口语", listening: "听力",
};
