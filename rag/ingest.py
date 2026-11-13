# -*- coding: utf-8 -*-
"""把研报/文档向量化入库（BGE 中文 Embedding + ChromaDB）。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import chromadb
from rag import embedding

DB_DIR = ROOT / 'rag' / 'chroma_db'


def ingest_dir(docs_dir):
    client = chromadb.PersistentClient(path=str(DB_DIR))
    col = client.get_or_create_collection('gold_reports')
    texts, ids, metas = [], [], []
    for f in sorted(Path(docs_dir).glob('*')):
        if f.suffix.lower() not in ('.txt', '.md'):
            continue
        text = f.read_text(encoding='utf-8', errors='ignore').strip()
        if not text:
            continue
        for i in range(0, len(text), 300):
            texts.append(text[i:i + 300])
            ids.append('%s#%d' % (f.stem, i))
            metas.append({'source': f.name})
    if not texts:
        return '没有找到可入库的文档'
    col.upsert(documents=texts, embeddings=embedding.embed(texts), ids=ids, metadatas=metas)
    return '已入库 %d 个片段' % len(texts)


if __name__ == '__main__':
    import sys as _sys
    d = _sys.argv[1] if len(_sys.argv) > 1 else str(ROOT / 'docs')
    print(ingest_dir(d))
