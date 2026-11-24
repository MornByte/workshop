"""课时示例内容生成器 — 为 4 种 lesson_type 生成 JSON 题目"""

from typing import Any, Dict


def build_lesson_content(lesson_type: str, index: int) -> Dict[str, Any]:
    """根据 lesson_type 生成示例题目 JSON。

    注：当前为演示数据，生产应从真实题库表读取或外部加载。
    """
    if lesson_type == "vocab":
        return _build_vocab(index)
    if lesson_type == "grammar":
        return _build_grammar(index)
    if lesson_type == "speaking":
        return _build_speaking(index)
    if lesson_type == "listening":
        return _build_listening(index)
    return {"questions": []}


def _build_vocab(index: int) -> Dict[str, Any]:
    words = [
        {"word": "Hello", "translation": "你好", "example": "Hello, nice to meet you."},
        {"word": "Goodbye", "translation": "再见", "example": "Goodbye, see you tomorrow!"},
        {"word": "Thank you", "translation": "谢谢", "example": "Thank you for your help."},
        {"word": "Sorry", "translation": "对不起", "example": "Sorry, I'm late."},
        {"word": "Please", "translation": "请", "example": "Please sit down."},
        {"word": "Yes", "translation": "是的", "example": "Yes, I agree."},
        {"word": "No", "translation": "不", "example": "No, thank you."},
        {"word": "Help", "translation": "帮助", "example": "Can you help me?"},
        {"word": "Love", "translation": "爱", "example": "I love learning languages."},
        {"word": "Study", "translation": "学习", "example": "I study every day."},
    ]
    return {"questions": [{"type": "word-card", **w} for w in words]}


def _build_grammar(index: int) -> Dict[str, Any]:
    questions = [
        {"type": "fill-blank", "prompt": "I ___ a student.", "options": ["am", "is", "are", "be"], "answer": 0},
        {"type": "fill-blank", "prompt": "She ___ to school every day.", "options": ["go", "goes", "going", "went"], "answer": 1},
        {"type": "fill-blank", "prompt": "They ___ playing football now.", "options": ["is", "are", "was", "were"], "answer": 1},
        {"type": "fill-blank", "prompt": "Yesterday I ___ pizza.", "options": ["eat", "eats", "ate", "eaten"], "answer": 2},
        {"type": "fill-blank", "prompt": "___ you speak English?", "options": ["Do", "Does", "Is", "Can"], "answer": 0},
    ]
    return {"questions": questions}


def _build_speaking(index: int) -> Dict[str, Any]:
    sentences = [
        {"sentence": "Hello, how are you?", "translation": "你好，最近怎么样？"},
        {"sentence": "I'm fine, thank you.", "translation": "我很好，谢谢。"},
        {"sentence": "What is your name?", "translation": "你叫什么名字？"},
        {"sentence": "My name is Alex.", "translation": "我叫 Alex。"},
        {"sentence": "Where are you from?", "translation": "你来自哪里？"},
    ]
    return {"questions": [{"type": "speaking", **s} for s in sentences]}


def _build_listening(index: int) -> Dict[str, Any]:
    audios = [
        {"type": "listening", "transcript": "Good morning! How can I help you today?",
         "q": "说话者在做什么？", "options": ["问候服务", "讲故事", "道歉", "告别"], "answer": 0},
        {"type": "listening", "transcript": "Could you please speak more slowly?",
         "q": "说话者的请求是？", "options": ["请慢说", "请大声", "请翻译", "请重复"], "answer": 0},
        {"type": "listening", "transcript": "Let's meet at the café at three o'clock.",
         "q": "约定时间是？", "options": ["三点", "两点", "四点", "不明确"], "answer": 0},
    ]
    return {"questions": audios}
