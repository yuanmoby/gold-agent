# 黄金多因子分析 Agent

一个基于 **LangGraph + 金十数据 MCP + RAG** 的金融分析 Agent：实时查行情、抓财经日历与快讯、检索历史研报，按六维框架输出黄金的多空分析。

## 能力
- 实时行情：黄金 / 白银 / 原油 / 汇率（金十数据，权威）
- 宏观数据：财经日历（CPI / PMI / 非农 / 美联储，含前值预期公布值）
- 新闻情报：金十快讯搜索 + 深度文章
- 知识库：RAG 检索本地研报（BGE 中文 Embedding + ChromaDB）
- 分析引擎：LangGraph ReAct 编排，六维框架（利率货币 / 通胀 / 避险情绪 / 供需 / 关联市场 / 资金持仓）

## 目录结构
```
gold-agent/
├─ config.py         # 密钥集中管理（.env）
├─ jin10_client.py   # 金十 MCP 客户端（手写 JSON-RPC 2.0）
├─ tools/            # 行情 / 日历 / 新闻 / 搜索
├─ rag/              # 研报入库与检索
├─ graph.py          # LangGraph ReAct 状态图
├─ agent.py          # 统一分析接口
├─ cli.py            # 命令行入口
├─ server.py         # FastAPI 后端
├─ static/           # 前端（深色黄金主题）
└─ docs/             # 研报样例（RAG 数据源）
```

## 快速开始
```bash
cd D:/tenement/gold-agent
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 1) 配置密钥（.env，已自动生成；请勿提交 Git）
#    JIN10_TOKEN=...      DEEPSEEK_API_KEY=sk-...

# 2) 入库研报（首次会下载 BGE 中文模型，走国内镜像）
python rag/ingest.py docs

# 3) 命令行分析
python cli.py "帮我分析今天的黄金，重点看非农、CPI 和美伊局势"

# 4) 网页版（好看的前端）
python server.py
# 浏览器打开 http://127.0.0.1:8000
```

## 设计决策（面试必讲）
- 为什么用 LangGraph 而不是手写循环：状态图 + 条件边，把「LLM 决策 → 工具执行 → 回传」建模成图，可扩展、可观察、可断点。
- 为什么用 MCP：金十数据走标准 MCP 协议，客户端手写 JSON-RPC 2.0 + SSE 解析，不绑死 SDK。
- 为什么加 RAG：模型训练记忆会过时，历史研报/成因分析必须从知识库检索，解决幻觉。
- 为什么温度 0.3：金融分析要稳定准确，不要创意。
- 工具如何容错：每个工具 try/except，失败返回错误文本让模型换思路，不崩溃。

## 免责声明
本项目仅用于技术学习与展示，不构成任何投资建议。
