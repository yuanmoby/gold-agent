# -*- coding: utf-8 -*-
"""Agent 封装：提供统一分析接口，供 CLI 与 Web 后端调用。"""
from graph import analyze


def ask(question):
    try:
        return analyze(question)
    except Exception as e:
        return '分析失败：%s（请检查网络与 .env 中的密钥配置）' % e
