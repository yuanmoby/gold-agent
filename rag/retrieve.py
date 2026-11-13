# -*- coding: utf-8 -*-
"""检索知识库中与问题最相关的片段（依赖惰性加载）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DB_DIR = ROOT / 'rag' / 'chroma_db'


def retrieve(query, top_k=3):
    import chromadb
    from rag import embedding
    client = chromadb.PersistentClient(path=str(DB_DIR))
    col = client.get_collection('gold_reports')
    res = col.query(query_embeddings=embedding.embed([query]), n_results=top_k)
    docs = res.get('documents', [[]])[0]
    metas = res.get('metadatas', [[]])[0]
    return list(zip(docs, metas))


def retrieve_text(query, top_k=3):
    try:
        pairs = retrieve(query, top_k)
        if not pairs:
            return '知识库为空或未检索到相关内容'
        return '\n\n'.join('[来源:%s] %s' % (m.get('source', '?'), d) for d, m in pairs)
    except Exception as e:
        return '知识库检索失败：%s' % e
