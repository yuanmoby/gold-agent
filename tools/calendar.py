# -*- coding: utf-8 -*-
"""财经日历工具。"""
from jin10_client import get_client

KEYWORDS = ('美国', '中国', '美联储', 'CPI', 'PMI', '非农', '利率', '黄金', '原油', 'EIA', 'OPEC', '欧佩克', 'PCE', '失业')


def get_calendar():
    try:
        data = get_client().call_tool('list_calendar', {})
        events = data.get('data', []) if isinstance(data, dict) else (data or [])
        if not events:
            return '财经日历暂无数据'
        picked = [e for e in events if int(e.get('star', 0) or 0) >= 2 or any(k in str(e.get('title', '')) for k in KEYWORDS)]
        picked = picked or events[:20]
        lines = []
        for e in picked[:25]:
            star = '★' * int(e.get('star', 0) or 0)
            parts = ['%s %s %s' % (e.get('pub_time', ''), star, e.get('title', ''))]
            vals = []
            if e.get('previous') is not None:
                vals.append('前值%s' % e['previous'])
            if e.get('consensus') is not None:
                vals.append('预期%s' % e['consensus'])
            if e.get('actual') is not None:
                vals.append('公布%s' % e['actual'])
            if e.get('affect_txt'):
                vals.append('影响:%s' % e['affect_txt'])
            if vals:
                parts.append(' | ' + ' | '.join(vals))
            lines.append(''.join(parts))
        return '\n'.join(lines)
    except Exception as e:
        return '财经日历查询失败：%s' % e
