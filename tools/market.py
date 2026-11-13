# -*- coding: utf-8 -*-
"""行情工具：金十 quote / kline / 品种代码。"""
import json
import time

from jin10_client import get_client


def get_quote(code):
    try:
        data = get_client().call_tool('get_quote', {'code': code})
        d = data.get('data', data) if isinstance(data, dict) else data
        return json.dumps(d, ensure_ascii=False)
    except Exception as e:
        return '行情查询失败：%s' % e


def get_kline(code, count=20):
    try:
        args = {'code': code}
        if count:
            args['count'] = count
        data = get_client().call_tool('get_kline', args)
        d = data.get('data', data) if isinstance(data, dict) else data
        klines = d.get('klines', []) if isinstance(d, dict) else []
        lines = ['%s 最近%d根K线：' % (code, len(klines))]
        for k in klines[-count:]:
            t = k.get('time')
            if isinstance(t, (int, float)):
                t = time.strftime('%Y-%m-%d %H:%M', time.localtime(t))
            lines.append('  时间%s 开%s 高%s 低%s 收%s 量%s' % (t, k.get('open'), k.get('high'), k.get('low'), k.get('close'), k.get('volume')))
        return '\n'.join(lines)
    except Exception as e:
        return 'K线查询失败：%s' % e


def list_codes():
    try:
        data = get_client().read_resource('quote://codes')
        rows = data.get('data', []) if isinstance(data, dict) else (data or [])
        if not rows:
            return '没有拿到品种代码'
        return '\n'.join('%s = %s' % (r.get('code'), r.get('name')) for r in rows)
    except Exception as e:
        return '品种代码查询失败：%s' % e
