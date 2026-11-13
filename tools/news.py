# -*- coding: utf-8 -*-
"""金十新闻情报工具：快讯 + 深度文章。"""
import json

from jin10_client import get_client


def search_flash(keyword):
    try:
        data = get_client().call_tool('search_flash', {'keyword': keyword})
        items = data.get('data', {}).get('items', []) if isinstance(data, dict) else []
        if not items:
            return '没有搜到关于“%s”的快讯' % keyword
        lines = []
        for it in items[:8]:
            lines.append('- [%s] %s' % (str(it.get('time', ''))[:16], str(it.get('content', ''))[:160]))
        return '\n'.join(lines)
    except Exception as e:
        return '快讯搜索失败：%s' % e


def list_flash():
    try:
        data = get_client().call_tool('list_flash', {})
        items = data.get('data', {}).get('items', []) if isinstance(data, dict) else []
        if not items:
            return '暂无快讯'
        lines = []
        for it in items[:8]:
            lines.append('- [%s] %s' % (str(it.get('time', ''))[:16], str(it.get('content', ''))[:160]))
        return '\n'.join(lines)
    except Exception as e:
        return '快讯列表失败：%s' % e


def search_news(keyword):
    try:
        data = get_client().call_tool('search_news', {'keyword': keyword})
        items = data.get('data', {}).get('items', []) if isinstance(data, dict) else []
        if not items:
            return '没有搜到关于“%s”的资讯' % keyword
        lines = []
        for it in items[:10]:
            lines.append('- id=%s | %s | %s' % (it.get('id'), str(it.get('time', ''))[:16], it.get('title', '')))
        return '\n'.join(lines)
    except Exception as e:
        return '资讯搜索失败：%s' % e


def get_news(news_id):
    try:
        data = get_client().call_tool('get_news', {'id': news_id})
        d = data.get('data', data) if isinstance(data, dict) else data
        return json.dumps(d, ensure_ascii=False)[:2000]
    except Exception as e:
        return '资讯详情失败：%s' % e
