# -*- coding: utf-8 -*-
"""联网搜索工具（DeepSeek 官方 search 接口）。"""
import requests

import config


def search_web(query):
    try:
        resp = requests.post(
            config.DEEPSEEK_BASE_URL + '/v1/tools/search',
            headers={'Authorization': 'Bearer ' + config.DEEPSEEK_API_KEY},
            json={'query': query, 'count': 5},
            timeout=20,
        )
        data = resp.json()
        results = data.get('results', [])
        if not results:
            return '没有搜到结果'
        lines = []
        for r in results[:5]:
            title = r.get('title', '')
            summary = r.get('summary') or r.get('snippet') or ''
            date = r.get('date') or ''
            url = r.get('url') or ''
            line = '- %s（%s）：%s' % (title, date, summary)
            if url:
                line += ' 来源：%s' % url
            lines.append(line)
        return '\n'.join(lines)
    except Exception as e:
        return '搜索失败：%s' % e
