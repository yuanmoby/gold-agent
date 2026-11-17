# -*- coding: utf-8 -*-
"""Agent 封装：提供统一分析接口 + 多轮会话（短期记忆）。"""
import requests

from graph import analyze, SYSTEM

MAX_HISTORY_CHARS = 8000  # 历史总字符上限，防止超出模型上下文


def _friendly_error(e):
    if isinstance(e, requests.exceptions.HTTPError):
        code = e.response.status_code if e.response is not None else '?'
        if code == 400:
            return '请求被拒（400）：对话历史太长，已超出模型上下文，请点「清空对话」后重新提问。'
        if code == 401:
            return '密钥无效（401）：请检查 .env 里的 DEEPSEEK_API_KEY 是否正确、有效。'
        if code == 429:
            return '请求太频繁（429）：请稍等十几秒再试。'
        return '请求失败（%s）：%s' % (code, str(e)[:150])
    return '请求失败：%s' % str(e)[:150]


def ask(question):
    """单次分析（无记忆），供 CLI 使用。"""
    try:
        answer, _ = analyze(question)
        return answer
    except Exception as e:
        return _friendly_error(e)


class ChatSession:
    """带短期记忆的会话：维护消息历史，支持多轮追问，自动裁剪过长历史。"""

    def __init__(self, max_chars=MAX_HISTORY_CHARS):
        self.messages = [{'role': 'system', 'content': SYSTEM}]
        self.max_chars = max_chars

    def _total_chars(self):
        return sum(len(str(m.get('content', ''))) for m in self.messages)

    def _trim(self):
        # 从最老的一轮开始删，直到总字符在限制内（保证 tool_calls/tool 成对不破坏）
        while self._total_chars() > self.max_chars and len(self.messages) > 2:
            idx = [i for i, m in enumerate(self.messages) if m.get('role') == 'user']
            if len(idx) < 2:
                break
            del self.messages[idx[0]:idx[1]]
        # 兜底：只剩一轮仍超长，就只保留 system + 最近那轮
        if self._total_chars() > self.max_chars:
            idx = [i for i, m in enumerate(self.messages) if m.get('role') == 'user']
            if idx:
                self.messages = [self.messages[0]] + self.messages[idx[-1]:]

    def chat(self, question):
        try:
            answer, self.messages = analyze(question, history=self.messages)
            self._trim()
            return answer
        except Exception as e:
            return _friendly_error(e)

    def reset(self):
        self.messages = [{'role': 'system', 'content': SYSTEM}]