#!/usr/bin/env python3
"""
账单数据处理脚本
功能：
1. 解析各种格式的账单数据（Excel、CSV、文本）
2. 应用过滤规则（剔除9元以下、处理退款、剔除内部转账）
3. 自动分类（人/车/家）
4. 生成飞书多维表格式数据
"""

import pandas as pd
import json
import re
from datetime import datetime
from collections import defaultdict

# ============ 分类规则 ============

# 车相关关键词
CAR_KEYWORDS = [
    '车', '加油', '停车', '高速', 'ETC', '充电', '洗车', '保养', '维修', 
    '保险', '小米汽车', '车险', '驾照', '违章', '年检', '轮胎', '机油',
    '高德打车', '滴滴', '货拉拉', '代驾'
]

# 家相关关键词（装修、家居、建材等）
HOME_KEYWORDS = [
    '装修', '家居', '建材', '瓷砖', '地板', '门窗', '卫浴', '橱柜', '家具', '家电', 
    '灯具', '窗帘', '床垫', '沙发', '床', '马桶', '淋浴', '空调', '暖气', '水电',
    '设计', '施工', '拆除', '清运', '美缝', '吊顶', '墙面', '油漆', '涂料',
    '五金', '工具', '电钻', '螺丝', '钉子', '玻璃', '石材', '木材', '板材',
    '插座', '开关', '电线', '水管', '龙头', '花洒', '浴室柜', '镜子', '锁',
    '收纳', '置物架', '晾衣架', '垃圾桶', '地毯', '抱枕', '四件套', '被子',
    '冰箱', '洗衣机', '电视', '烟机', '灶具', '热水器', '净水器', '扫地机器人'
]

# 家相关交易分类
HOME_CATEGORIES = ['家居家装', '数码电器']

# 内部转账关键词（不计入账单）
INTERNAL_KEYWORDS = [
    '余额宝', '花呗自动还款', '信用卡还款', '余利宝', '网商银行', 
    '提现', '收益发放', '转入', '转出', '充值', '零钱通'
]

# ============ 核心函数 ============

def parse_amount(amount_str):
    """解析金额，返回数值"""
    if pd.isna(amount_str):
        return 0
    if isinstance(amount_str, (int, float)):
        return float(amount_str)
    # 移除货币符号和逗号
    amount_str = str(amount_str).replace(',', '').replace('¥', '').replace('元', '').strip()
    try:
        return float(amount_str)
    except:
        return 0

def parse_datetime(dt_str):
    """解析日期时间，返回datetime对象"""
    if pd.isna(dt_str):
        return None
    if isinstance(dt_str, datetime):
        return dt_str
    
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y/%m/%d %H:%M:%S',
        '%Y/%m/%d %H:%M',
        '%Y-%m-%d',
        '%Y/%m/%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(str(dt_str).strip(), fmt)
        except:
            continue
    return None

def is_internal_transfer(description, merchant=None):
    """判断是否为内部转账/余额操作"""
    desc = str(description) if description else ''
    merch = str(merchant) if merchant else ''
    
    for kw in INTERNAL_KEYWORDS:
        if kw in desc or kw in merch:
            return True
    return False

def classify_transaction(category, merchant, description):
    """
    根据交易内容分类到人/车/家
    返回: '人' | '车' | '家'
    """
    merch = str(merchant) if merchant else ''
    desc = str(description) if description else ''
    cat = str(category) if category else ''
    
    # 1. 检查车相关
    for kw in CAR_KEYWORDS:
        if kw in merch or kw in desc:
            return '车'
    
    # 2. 检查家相关
    for kw in HOME_KEYWORDS:
        if kw in merch or kw in desc:
            return '家'
    
    if cat in HOME_CATEGORIES:
        return '家'
    
    # 3. 其他归到人
    return '人'

def extract_brand(description, merchant):
    """
    从交易内容中提取品牌信息
    """
    desc = str(description) if description else ''
    merch = str(merchant) if merchant else ''
    
    # 常见品牌映射
    brand_patterns = {
        '小米': ['小米', 'XIAOMI', 'MI'],
        '美的': ['美的', 'Midea'],
        '公牛': ['公牛', 'BULL'],
        '施耐德': ['施耐德', 'Schneider'],
        '九牧': ['九牧', 'JOMOO'],
        '海尔': ['海尔', 'Haier'],
        '格力': ['格力', 'GREE'],
        '西门子': ['西门子', 'Siemens'],
        '宜家': ['宜家', 'IKEA'],
        '无印良品': ['无印良品', 'MUJI'],
    }
    
    text = desc + ' ' + merch
    for brand, patterns in brand_patterns.items():
        for p in patterns:
            if p in text:
                return brand
    
    return None

def process_refunds(records):
    """
    处理退款逻辑
    规则：
    - 支付100退100：完全抵消，不计入
    - 支付100退60：计入支出40
    - 支付100退150：计入收入50（这种情况较少）
    """
    # 分离支出和退款
    expenses = []
    refunds = []
    
    for r in records:
        if r.get('type') == 'refund' or r.get('is_refund'):
            refunds.append(r)
        else:
            expenses.append(r)
    
    # 匹配退款到支出
    result_expenses = []
    
    for exp in expenses:
        exp_amount = abs(exp.get('amount', 0))
        exp_merchant = exp.get('merchant', '')
        
        # 查找匹配的退款
        matching_refunds = []
        for ref in refunds:
            if ref.get('merchant') == exp_merchant:
                matching_refunds.append(ref)
        
        if matching_refunds:
            # 计算总退款金额
            total_refund = sum(abs(r.get('amount', 0)) for r in matching_refunds)
            
            if total_refund >= exp_amount:
                # 完全抵消，跳过此支出
                continue
            else:
                # 部分退款，调整金额
                exp['amount'] = exp_amount - total_refund
                exp['refund_note'] = f'原{exp_amount}元，退{total_refund}元'
        
        result_expenses.append(exp)
    
    return result_expenses

def process_excel_bill(file_path):
    """
    处理Excel格式的支付宝/微信账单
    """
    # 尝试不同的header行
    df = None
    for skip in [0, 10, 11, 12, 13, 23, 24]:
        try:
            df = pd.read_excel(file_path, skiprows=skip)
            if '交易时间' in df.columns or '时间' in df.columns:
                break
        except:
            continue
    
    if df is None:
        raise ValueError("无法识别账单格式")
    
    # 标准化列名
    column_mapping = {
        '交易时间': 'time',
        '时间': 'time',
        '交易分类': 'category',
        '分类': 'category',
        '交易对方': 'merchant',
        '对方': 'merchant',
        '商品说明': 'description',
        '说明': 'description',
        '收/支': 'type',
        '收支': 'type',
        '金额': 'amount',
        '收付款方式': 'payment_method',
        '支付方式': 'payment_method',
        '交易状态': 'status',
        '状态': 'status',
    }
    
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # 过滤有效记录
    records = []
    for _, row in df.iterrows():
        amount = parse_amount(row.get('amount', 0))
        
        # 规则1: 剔除9元以下
        if amount < 9:
            continue
        
        # 规则3: 剔除内部转账
        desc = row.get('description', '')
        merch = row.get('merchant', '')
        if is_internal_transfer(desc, merch):
            continue
        
        records.append({
            'time': parse_datetime(row.get('time')),
            'category': row.get('category', ''),
            'merchant': merch,
            'description': desc,
            'amount': amount,
            'type': row.get('type', ''),
            'status': row.get('status', ''),
            'payment_method': row.get('payment_method', ''),
        })
    
    # 处理退款
    records = process_refunds(records)
    
    # 分类
    for r in records:
        r['class'] = classify_transaction(r['category'], r['merchant'], r['description'])
        r['brand'] = extract_brand(r['description'], r['merchant'])
    
    return records

def to_feishu_format(records):
    """
    转换为飞书多维表格式
    """
    result = {'人': [], '车': [], '家': []}
    
    for r in records:
        cat = r.get('class', '人')
        dt = r.get('time')
        
        desc = r.get('description', '')
        if isinstance(desc, int):
            desc = str(desc)
        
        record = {
            '名称': r.get('merchant', '未知'),
            '费用': r.get('amount', 0),
            '时间': int(dt.timestamp() * 1000) if dt else None,
            '状态': False,  # 用户自行勾选
            '备注': str(desc)[:500],
        }
        
        if r.get('brand'):
            record['品牌'] = r['brand']
        
        result[cat].append(record)
    
    return result

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 process_bill.py <账单文件.xlsx>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"处理文件: {file_path}")
    records = process_excel_bill(file_path)
    
    print(f"处理后记录数: {len(records)}")
    
    # 统计
    by_class = defaultdict(list)
    for r in records:
        by_class[r['class']].append(r)
    
    for cls in ['人', '车', '家']:
        items = by_class[cls]
        total = sum(r['amount'] for r in items)
        print(f"{cls}: {len(items)} 笔, 共 {total:.2f} 元")
    
    # 输出JSON
    feishu_data = to_feishu_format(records)
    output_path = file_path.replace('.xlsx', '_processed.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(feishu_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存: {output_path}")

if __name__ == '__main__':
    main()
