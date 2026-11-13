# -*- coding: utf-8 -*-
"""Streamlit 版界面（可部署到 Streamlit Community Cloud）。复用同一个 Agent 后端。"""
import os

import streamlit as st

# 优先用 Streamlit Cloud Secrets，其次环境变量 / .env
try:
    if st.secrets.get('JIN10_TOKEN'):
        os.environ['JIN10_TOKEN'] = st.secrets['JIN10_TOKEN']
    if st.secrets.get('DEEPSEEK_API_KEY'):
        os.environ['DEEPSEEK_API_KEY'] = st.secrets['DEEPSEEK_API_KEY']
except Exception:
    pass

from agent import ask
from tools import market

st.set_page_config(page_title='黄金多因子分析 Agent', page_icon='◆', layout='wide')

st.title('◆ 黄金多因子分析 Agent')
st.caption('LangGraph ReAct · 金十 MCP · RAG · 六维分析框架 · github.com/yuanmoby/gold-agent')

with st.sidebar:
    st.subheader('实时行情')
    if st.button('刷新行情'):
        st.session_state['quotes'] = {
            '黄金 XAUUSD': market.get_quote('XAUUSD'),
            '白银 XAGUSD': market.get_quote('XAGUSD'),
            '美原油 USOIL': market.get_quote('USOIL'),
            '美元人民币 USDCNH': market.get_quote('USDCNH'),
        }
    quotes = st.session_state.get('quotes')
    if quotes:
        for name, raw in quotes.items():
            with st.expander(name):
                st.code(raw[:200])
    else:
        st.caption('点「刷新行情」查看实时价')
    st.caption('数据来自金十 MCP，实时更新')

st.session_state.setdefault('chat_history', [])
for m in st.session_state['chat_history']:
    with st.chat_message(m['role']):
        st.write(m['content'])

if not st.session_state['chat_history']:
    with st.chat_message('assistant'):
        st.write('你好，我是黄金多因子分析 Agent。试试问我：')
        for s in ['帮我分析今天的黄金，重点看非农、CPI 和美伊局势', '白银现在什么价？', '美联储最近对黄金有什么影响？']:
            st.write('· ' + s)

if prompt := st.chat_input('问我任何黄金/宏观问题…'):
    st.session_state['chat_history'].append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.write(prompt)
    with st.chat_message('assistant'):
        with st.spinner('思考中（可能正在调用行情/日历/快讯/研报工具）…'):
            answer = ask(prompt)
        st.write(answer)
    st.session_state['chat_history'].append({'role': 'assistant', 'content': answer})
