# -*- coding: utf-8 -*-
"""Web 后端：FastAPI 提供 /api/chat 与 /api/quotes，托管前端静态页。"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import ChatSession
from tools import market

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='黄金多因子分析 Agent')

sessions = {}


class ChatReq(BaseModel):
    question: str
    session_id: str = 'default'


@app.post('/api/chat')
def chat(req: ChatReq):
    if req.session_id not in sessions:
        sessions[req.session_id] = ChatSession()
    return {'answer': sessions[req.session_id].chat(req.question)}


@app.get('/api/quotes')
def quotes():
    codes = ['XAUUSD', 'XAGUSD', 'USOIL', 'USDCNH']
    data = {}
    for c in codes:
        data[c] = market.get_quote(c)
    return data


@app.get('/')
def index():
    return FileResponse(ROOT / 'static' / 'index.html')


app.mount('/static', StaticFiles(directory=str(ROOT / 'static')), name='static')


if __name__ == '__main__':
    import os
    import uvicorn
    port = int(os.environ.get('PORT', '8000'))
    uvicorn.run(app, host='0.0.0.0', port=port)