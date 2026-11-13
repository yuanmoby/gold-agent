# -*- coding: utf-8 -*-
"""命令行入口：python cli.py "帮我分析今天的黄金" """
import sys

from agent import ask


def main():
    q = sys.argv[1] if len(sys.argv) > 1 else '帮我分析今天的黄金，重点看非农、CPI 和美伊局势'
    print('问题：', q, '\n')
    print(ask(q))


if __name__ == '__main__':
    main()
