# -*- coding: utf-8 -*-
"""共享的 BGE 中文 Embedding：ingest 与 retrieve 必须用同一模型，保证向量一致。"""
import os

from sentence_transformers import SentenceTransformer

_MODEL_NAME = 'BAAI/bge-small-zh-v1.5'
_model = None


def get_model():
    global _model
    if _model is None:
        os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def embed(texts):
    """把文本批量转成归一化向量（归一化后 L2 排序等价于余弦排序）。"""
    model = get_model()
    vecs = model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
    return [v.tolist() for v in vecs]
