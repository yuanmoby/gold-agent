# -*- coding: utf-8 -*-
"""补充数据工具：美债收益率、黄金库存、CFTC 黄金持仓（akshare）。"""
import akshare as ak


def get_us_treasury():
    """美国国债收益率（2/5/10/30 年期 + 10Y-2Y 利差），利率维度核心。"""
    try:
        df = ak.bond_zh_us_rate(start_date='20260101')
        row = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else None
        lines = ['美国国债收益率（%s）：' % str(row['日期'])]
        lines.append('2年 %s%% | 5年 %s%% | 10年 %s%% | 30年 %s%% | 10Y-2Y %s%%' % (
            row.get('美国国债收益率2年'), row.get('美国国债收益率5年'),
            row.get('美国国债收益率10年'), row.get('美国国债收益率30年'),
            row.get('美国国债收益率10年-2年')))
        if prev is not None:
            lines.append('较上一交易日：10年期 %s -> %s' % (prev.get('美国国债收益率10年'), row.get('美国国债收益率10年')))
        return '\n'.join(lines)
    except Exception as e:
        return '美债收益率查询失败：%s' % e


def get_gold_inventory():
    """黄金库存（供需维度参考）。"""
    try:
        df = ak.macro_cons_gold()
        gold = df[df['商品'] == '黄金'].tail(3)
        if gold.empty:
            return '未获取到黄金库存数据'
        lines = ['黄金库存（最近 %d 条）：' % len(gold)]
        for _, r in gold.iterrows():
            lines.append('%s：库存 %s，增持/减持 %s，总价值 %s' % (r['日期'], r.get('总库存'), r.get('增持/减持'), r.get('总价值')))
        return '\n'.join(lines)
    except Exception as e:
        return '黄金库存查询失败：%s' % e


def get_cftc_gold():
    """CFTC 黄金持仓（COMEX 黄金多/空/净仓位），资金持仓维度核心。"""
    try:
        df = ak.macro_usa_cftc_merchant_goods_holding()
        sub = df[['日期', '黄金-多头仓位', '黄金-空头仓位', '黄金-净仓位']].tail(3)
        lines = ['CFTC 黄金持仓（COMEX，最近 %d 期）：' % len(sub)]
        for _, r in sub.iterrows():
            lines.append('%s：多头 %s，空头 %s，净仓位 %s' % (r['日期'], r['黄金-多头仓位'], r['黄金-空头仓位'], r['黄金-净仓位']))
        return '\n'.join(lines)
    except Exception as e:
        return 'CFTC 黄金持仓查询失败：%s' % e