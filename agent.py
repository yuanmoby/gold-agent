# -*- coding: utf-8 -*-
"""Agent 封装：提供统一分析接口 + 多轮会话（短期记忆）。"""
from graph import analyze, SYSTEM


def ask(question):
    """单次分析（无记忆），供 CLI 使用。"""
    try:
        answer, _ = analyze(question)
        return answer
    except Exception as e:
        return '分析失败：%s（请检查网络与 .env 中的密钥配置）' % e


class ChatSession:
    """带短期记忆的会话：维护消息历史，支持多轮追问。"""

    def __init__(self, max_history=30):
        self.messages = [{'role': 'system', 'content': SYSTEM}]
        self.max_history = max_history

    def chat(self, question):
        try:
            answer, self.messages = analyze(question, history=self.messages)
            if len(self.messages) > self.max_history + 1:
                self.messages = [self.messages[0]] + self.messages[-(self.max_history):]
            return answer
        except Exception as e:
            return '分析失败：%s（请检查网络与 .env 中的密钥配置）' % e