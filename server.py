# -*- coding: utf-8 -*-
"""Web 后端：FastAPI 提供 /api/chat 与 /api/quotes，托管前端静态页。"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import ask
from tools import market

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='黄金多因子分析 Agent')


class ChatReq(BaseModel):
    question: str


@app.post('/api/chat')
def chat(req: ChatReq):
    return {'answer': ask(req.question)}


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
