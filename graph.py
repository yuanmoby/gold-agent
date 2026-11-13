# -*- coding: utf-8 -*-
"""黄金多因子分析 Agent：LangGraph ReAct 编排。"""
import json
import operator
from typing import Annotated, TypedDict

import requests
from langgraph.graph import StateGraph, START, END

import config
from tools import market, calendar, news, search
from rag import retrieve

TOOLS = [
    {'type': 'function', 'function': {'name': 'get_gold_quote', 'description': '查询黄金 XAUUSD 实时行情（含今日高低点）', 'parameters': {'type': 'object', 'properties': {'code': {'type': 'string', 'description': '品种代码，默认 XAUUSD'}}, 'required': []}}},
    {'type': 'function', 'function': {'name': 'get_quote', 'description': '查询金十任意品种实时行情，如 XAGUSD/USOIL/UKOIL/USDCNH', 'parameters': {'type': 'object', 'properties': {'code': {'type': 'string', 'description': '品种代码'}}, 'required': ['code']}}},
    {'type': 'function', 'function': {'name': 'get_kline', 'description': '查询任意品种分钟级 K 线', 'parameters': {'type': 'object', 'properties': {'code': {'type': 'string'}, 'count': {'type': 'integer', 'description': 'K线根数，默认20'}}, 'required': ['code']}}},
    {'type': 'function', 'function': {'name': 'list_codes', 'description': '查询金十支持的品种代码列表', 'parameters': {'type': 'object', 'properties': {}}}},
    {'type': 'function', 'function': {'name': 'get_calendar', 'description': '查询今日重要财经日历（CPI/PMI/非农/美联储等，含前值预期公布值）', 'parameters': {'type': 'object', 'properties': {}}}},
    {'type': 'function', 'function': {'name': 'search_flash', 'description': '搜索金十快讯（实时新闻：美伊/美联储/黄金/非农/CPI）', 'parameters': {'type': 'object', 'properties': {'keyword': {'type': 'string'}}, 'required': ['keyword']}}},
    {'type': 'function', 'function': {'name': 'search_news', 'description': '搜索金十深度资讯文章，返回文章 id 列表', 'parameters': {'type': 'object', 'properties': {'keyword': {'type': 'string'}}, 'required': ['keyword']}}},
    {'type': 'function', 'function': {'name': 'get_news', 'description': '根据资讯 id 读取单篇文章全文', 'parameters': {'type': 'object', 'properties': {'id': {'type': 'string'}}, 'required': ['id']}}},
    {'type': 'function', 'function': {'name': 'search_web', 'description': '联网搜索补充数据（美债收益率、VIX 等金十覆盖不到的数据）', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}}},
    {'type': 'function', 'function': {'name': 'retrieve_knowledge', 'description': '从本地研报知识库检索历史资料（RAG）', 'parameters': {'type': 'object', 'properties': {'query': {'type': 'string'}}, 'required': ['query']}}},
]

SYSTEM = """你是黄金多因子分析助手，必须做到：
1. 只用工具返回的真实数据作答，禁止编造任何数字、日期或新闻。
2. 行情默认用 get_gold_quote 查 XAUUSD；用户问其他品种用 get_quote/get_kline，代码不确定时先 list_codes。
3. 宏观数据用 get_calendar；突发新闻用 search_flash；深度分析用 search_news 再 get_news；金十覆盖不到的（美债收益率、VIX 等）才用 search_web。
4. 涉及历史背景、过去走势成因时，用 retrieve_knowledge 查本地研报库。
5. 必须覆盖六个维度：1)利率与货币 2)通胀 3)避险与情绪 4)供需 5)关联市场 6)资金持仓。
6. 输出结构：先列行情与关键事实（带时间/数值），再逐维度给利多/利空判断，最后汇总多空，并明确列出仍缺失的数据。
7. 最后必须注明：仅为因素梳理，不构成投资建议，无法预测走势。"""


def _call_llm(messages):
    resp = requests.post(
        config.DEEPSEEK_BASE_URL + '/chat/completions',
        headers={'Authorization': 'Bearer ' + config.DEEPSEEK_API_KEY},
        json={'model': config.DEEPSEEK_MODEL, 'messages': messages, 'tools': TOOLS, 'temperature': 0.3},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']


def _run_tool(name, args):
    if name == 'get_gold_quote':
        return market.get_quote(args.get('code', 'XAUUSD'))
    if name == 'get_quote':
        return market.get_quote(args['code'])
    if name == 'get_kline':
        return market.get_kline(args['code'], args.get('count', 20))
    if name == 'list_codes':
        return market.list_codes()
    if name == 'get_calendar':
        return calendar.get_calendar()
    if name == 'search_flash':
        return news.search_flash(args['keyword'])
    if name == 'search_news':
        return news.search_news(args['keyword'])
    if name == 'get_news':
        return news.get_news(args['id'])
    if name == 'search_web':
        return search.search_web(args['query'])
    if name == 'retrieve_knowledge':
        return retrieve.retrieve_text(args['query'])
    return '未知工具：%s' % name


class State(TypedDict):
    messages: Annotated[list, operator.add]


def node_llm(state):
    return {'messages': [_call_llm(state['messages'])]}


def node_tools(state):
    last = state['messages'][-1]
    tool_msgs = []
    for tc in last.get('tool_calls', []):
        name = tc['function']['name']
        try:
            args = json.loads(tc['function'].get('arguments') or '{}')
        except json.JSONDecodeError:
            args = {}
        result = _run_tool(name, args)
        tool_msgs.append({'role': 'tool', 'tool_call_id': tc['id'], 'content': str(result)})
    return {'messages': tool_msgs}


def route(state):
    if state['messages'][-1].get('tool_calls'):
        return 'tools'
    return END


builder = StateGraph(State)
builder.add_node('llm', node_llm)
builder.add_node('tools', node_tools)
builder.add_edge(START, 'llm')
builder.add_conditional_edges('llm', route, {'tools': 'tools', END: END})
builder.add_edge('tools', 'llm')
graph = builder.compile()


def analyze(question):
    result = graph.invoke({'messages': [
        {'role': 'system', 'content': SYSTEM},
        {'role': 'user', 'content': question},
    ]})
    return result['messages'][-1].get('content', '')
