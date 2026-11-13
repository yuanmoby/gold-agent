# 黄金多因子分析 Agent

基于 **LangGraph + 金十数据 MCP + RAG** 的金融分析 Agent：实时查行情、抓财经日历与快讯、检索历史研报，按六维框架输出黄金多空分析。

## 能力
- 实时行情：黄金 / 白银 / 原油 / 汇率（金十数据，权威）
- 宏观数据：财经日历（CPI / PMI / 非农 / 美联储，含前值预期公布值）
- 新闻情报：金十快讯搜索 + 深度文章
- 知识库：RAG 检索本地研报（BGE 中文 Embedding + ChromaDB）
- 分析引擎：LangGraph ReAct 编排，六维框架（利率货币/通胀/避险情绪/供需/关联市场/资金持仓）

## 目录结构
```
gold-agent/
├─ config.py          # 密钥集中管理（.env，不提交 Git）
├─ jin10_client.py    # 金十 MCP 客户端（手写 JSON-RPC 2.0 + SSE）
├─ tools/             # 行情 / 日历 / 新闻 / 搜索
├─ rag/               # 研报入库与检索（惰性加载，RAG 可选）
├─ graph.py           # LangGraph ReAct 状态图
├─ agent.py           # 统一分析接口
├─ cli.py             # 命令行入口
├─ app_streamlit.py   # Streamlit 界面（可部署 Streamlit Cloud）
├─ server.py          # FastAPI 后端 + 深色主题前端
├─ render.yaml        # Render 部署配置（备用）
└─ docs/              # 研报样例（RAG 数据源）
```

## 本地运行
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 可选：RAG 依赖（要用研报检索才装，会下载 torch 与 BGE 模型）
pip install -r requirements-rag.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 密钥：.env（已生成，勿提交 Git）
#   JIN10_TOKEN=...   DEEPSEEK_API_KEY=sk-...

# RAG 入库（首次下载 BGE 中文模型）
python rag/ingest.py docs

# 命令行
python cli.py "帮我分析今天的黄金，重点看非农和CPI"

# 网页版 A：Streamlit
streamlit run app_streamlit.py

# 网页版 B：FastAPI 深色主题
python server.py
```

## 部署到公网（Streamlit Community Cloud，免费 + 固定链接）
1. 把本仓库推到 GitHub（已完成：github.com/yuanmoby/gold-agent）
2. 打开 share.streamlit.io，用 GitHub 登录 → Create app
3. 选仓库 gold-agent、分支 main、入口文件 **app_streamlit.py** → Deploy
4. 在 Advanced settings → Secrets 里填：
   `JIN10_TOKEN = 你的token`
   `DEEPSEEK_API_KEY = sk-xxx`
5. 几分钟后得到固定公网地址，形如 `https://yuanmoby-gold-agent.streamlit.app`

> 说明：Streamlit 版复用同一个 Agent 后端；RAG 依赖已拆到 requirements-rag.txt，云端只装轻量依赖、不下载 torch。云端无本地知识库时 RAG 返回「知识库为空」，属预期，行情/新闻/六维分析不受影响。

## 设计决策（面试必讲）
- 为什么用 LangGraph：状态图 + 条件边，把「LLM 决策 → 工具执行 → 回传」建模成图，可扩展、可断点。
- 为什么用 MCP：金十数据走标准 MCP 协议，客户端手写 JSON-RPC 2.0 + SSE 解析，不绑死 SDK。
- 为什么加 RAG：模型记忆会过时，历史研报/成因分析要检索知识库，解决幻觉。
- 为什么 RAG 惰性加载：不启动就加载 torch，本地和云端启动都快，按需加载。
- 为什么温度 0.3：金融分析要稳定准确，不要创意。
- 工具如何容错：每个工具 try/except，失败返回错误文本让模型换思路，不崩溃。

## 免责声明
本项目仅用于技术学习与展示，不构成任何投资建议。
