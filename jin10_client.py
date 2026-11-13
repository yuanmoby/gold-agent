# -*- coding: utf-8 -*-
"""金十数据 MCP 客户端（手写 JSON-RPC 2.0 over HTTP + SSE 解析）。"""
import json
import requests

import config


class Jin10Error(Exception):
    pass


def _parse_response(resp):
    text = resp.text
    ctype = resp.headers.get('Content-Type', '')
    is_sse = ('text/event-stream' in ctype) or text.lstrip().startswith('event:')
    if is_sse:
        blocks = []
        for event in text.split('\n\n'):
            data_lines = [ln[5:].strip() for ln in event.splitlines() if ln.startswith('data:')]
            if data_lines:
                blocks.append('\n'.join(data_lines))
        if not blocks:
            raise Jin10Error('SSE无数据: ' + text[:400])
        for block in reversed(blocks):
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue
        raise Jin10Error('SSE解析失败: ' + blocks[-1][:400])
    try:
        return resp.json()
    except Exception:
        raise Jin10Error('响应不是JSON: %s %s' % (resp.status_code, text[:200]))


class Jin10Client:
    def __init__(self):
        if not config.JIN10_TOKEN:
            raise Jin10Error('未配置 JIN10_TOKEN，请在 .env 里填写')
        self.token = config.JIN10_TOKEN
        self.session_id = None
        self._id = 0

    def _headers(self):
        h = {
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
            'User-Agent': 'Mozilla/5.0',
        }
        if self.session_id:
            h['Mcp-Session-Id'] = self.session_id
        return h

    def _rpc(self, method, params=None, notify=False):
        payload = {'jsonrpc': '2.0', 'method': method}
        if not notify:
            self._id += 1
            payload['id'] = self._id
        if params is not None:
            payload['params'] = params
        resp = requests.post(config.JIN10_BASE_URL, headers=self._headers(), json=payload, timeout=40)
        resp.encoding = 'utf-8'
        sid = resp.headers.get('Mcp-Session-Id') or resp.headers.get('mcp-session-id')
        if sid:
            self.session_id = sid
        if notify:
            return None
        data = _parse_response(resp)
        if 'error' in data:
            raise Jin10Error('协议错误: %s' % data['error'])
        return data.get('result', {})

    def initialize(self):
        result = self._rpc('initialize', {
            'protocolVersion': '2025-11-25',
            'capabilities': {},
            'clientInfo': {'name': 'gold-agent', 'version': '1.0'},
        })
        self._rpc('notifications/initialized', notify=True)
        return result

    def read_resource(self, uri):
        result = self._rpc('resources/read', {'uri': uri})
        contents = result.get('contents', [])
        if contents:
            text = contents[0].get('text', '')
            try:
                return json.loads(text)
            except Exception:
                return text
        return result

    def call_tool(self, name, arguments=None):
        result = self._rpc('tools/call', {'name': name, 'arguments': arguments or {}})
        if result.get('isError'):
            msg = ''
            for c in result.get('content', []):
                if c.get('type') == 'text':
                    msg += c.get('text', '')
            raise Jin10Error(msg or ('工具 %s 返回业务错误' % name))
        sc = result.get('structuredContent')
        if sc is not None:
            return sc
        for c in result.get('content', []):
            if c.get('type') == 'text':
                try:
                    return json.loads(c.get('text', ''))
                except Exception:
                    return c.get('text', '')
        return result


_client = None


def get_client():
    global _client
    if _client is None:
        c = Jin10Client()
        c.initialize()
        _client = c
    return _client
