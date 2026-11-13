# -*- coding: utf-8 -*-
"""集中读取密钥与配置：优先环境变量，其次项目根目录 .env。"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load_env():
    env = {}
    env_file = ROOT / '.env'
    if env_file.exists():
        for line in env_file.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


_ENV = _load_env()


def get(name, default=''):
    return os.environ.get(name) or _ENV.get(name) or default


JIN10_TOKEN = get('JIN10_TOKEN')
DEEPSEEK_API_KEY = get('DEEPSEEK_API_KEY')
JIN10_BASE_URL = get('JIN10_BASE_URL', 'https://mcp.jin10.com/mcp')
DEEPSEEK_BASE_URL = get('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
DEEPSEEK_MODEL = get('DEEPSEEK_MODEL', 'deepseek-chat')
