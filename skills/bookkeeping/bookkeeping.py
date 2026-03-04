#!/usr/bin/env python3
"""
飞书账单管家 - 核心处理模块
"""
import pandas as pd
import json
import requests
import time
from datetime import datetime, timedelta
from collections import defaultdict

class BillImporter:
    """飞书账单导入器"""
    
    # 飞书配置
    APP_ID = "cli_a91c3a810038dcc2"
    APP_SECRET = "cjxCK7wfUHsiDb8uMLNbxbdHCKgZDqUb"
    APP_TOKEN = "BOPEbIt7taU8Pws593YcEnsrnBt"
    
    TABLES = {
        '人': 'tbl7dEzuHBVUoxTI',
        '车': 'tblf4fTIxkuEslxj',
        '家': 'tblHenR8pEA7hB3v'
    }
    
    # 分类关键词
    CAR_KEYWORDS = ['加油', '充电', '洗车', '维修', '保养', 'ETC', '车险', '车贷', '车辆', '小米汽车']
    HOME_KEYWORDS = ['装修', '家居', '建材', '家具', '家电', '灯具', '插座', '开关', '网线']
    INTERNAL_KEYWORDS = ['余额宝', '花呗自动还款', '信用卡还款', '余利宝', '网商银行', '提现', '收益发放']
    
    def __init__(self):
        self.token = None
        self.records = {'人': [], '车': [], '家': []}
    
    def get_token(self):
        """获取飞书 tenant_access_token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {"app_id": self.APP_ID, "app_secret": self.APP_SECRET}
        
        resp = requests.post(url, headers=headers, json=data)
        result = resp.json()
        
        if result.get("code") == 0:
            self.token = result["tenant_access_token"]
            return True
        else:
            print(f"获取Token失败: {result}")
            return False
    
    def process_excel(self, file_path):
        """处理Excel账单"""
        print(f"处理文件: {file_path}")
        
        # 读取Excel
        df = pd.read_excel(file_path, skiprows=24)
        df.columns = ['交易时间', '交易分类', '交易对方', '对方账号', '商品说明', 
                      '收支', '金额', '收付款方式', '交易状态', '交易订单号', 
                      '商家订单号', '备注']
        df = df.dropna(subset=['交易时间'])
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce')
        
        # 规则1: 剔除9元以下
        df = df[df['金额'] >= 9]
        
        # 规则3: 剔除内部转账
        df = df[~df['商品说明'].astype(str).apply(
            lambda x: any(kw in x for kw in self.INTERNAL_KEYWORDS)
        )]
        
        print(f"过滤后记录数: {len(df)}")
        
        # 处理每条记录
        for _, row in df.iterrows():
            record = self._process_record(row)
            if record:
                category = self._classify(record['名称'], record['备注'])
                self.records[category].append(record)
        
        # 统计
        print("\n=== 分类统计 ===")
        for cat in ['人', '车', '家']:
            total = sum(r['费用'] for r in self.records[cat])
            print(f"{cat}: {len(self.records[cat])} 条, ¥{total:.2f}")
        
        return self.records
    
    def _process_record(self, row):
        """处理单条记录"""
        # 转换时间（北京时间转UTC）
        dt = pd.to_datetime(row['交易时间'])
        utc_dt = dt - timedelta(hours=8)
        timestamp = int(utc_dt.timestamp() * 1000)
        
        return {
            '名称': row['交易对方'],
            '费用': float(row['金额']),
            '时间': timestamp,
            '备注': str(row['商品说明'])[:300] if pd.notna(row['商品说明']) else '',
            '品牌': self._extract_brand(row['交易对方'], row['商品说明'])
        }
    
    def _classify(self, name, desc):
        """分类到人/车/家"""
        text = str(name) + str(desc)
        
        # 保险/医保 -> 人
        if '保险' in name or '医保' in name or '健康' in name:
            return '人'
        
        # 车相关 -> 车
        if any(kw in text for kw in self.CAR_KEYWORDS):
            return '车'
        
        # 家相关 -> 家
        if any(kw in text for kw in self.HOME_KEYWORDS):
            return '家'
        
        # 其他 -> 人
        return '人'
    
    def _extract_brand(self, name, desc):
        """提取品牌"""
        text = str(name) + ' ' + str(desc)
        brands = {
            '小米': 'XIAOMI', 'XIAOMI': 'XIAOMI',
            '美的': '美的',
            '公牛': '公牛',
            '九牧': '九牧',
            '绿联': '绿联',
        }
        for key, value in brands.items():
            if key in text:
                return value
        return None
    
    def import_to_feishu(self):
        """导入到飞书多维表"""
        if not self.token and not self.get_token():
            return False
        
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        
        print("\n=== 开始导入飞书 ===")
        
        for category, records in self.records.items():
            if not records:
                continue
            
            table_id = self.TABLES[category]
            print(f"\n【{category}表】导入 {len(records)} 条...")
            
            success = 0
            for r in records:
                fields = {
                    '名称': r['名称'],
                    '费用': r['费用'],
                    '最后更新时间': r['时间'],
                    '状态': False,
                    '备注': r['备注']
                }
                
                # 家表添加品牌
                if category == '家' and r.get('品牌'):
                    fields['品牌'] = r['品牌']
                
                url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{self.APP_TOKEN}/tables/{table_id}/records'
                resp = requests.post(url, headers=headers, json={'fields': fields})
                
                if resp.json().get('code') == 0:
                    success += 1
                
                time.sleep(0.05)  # 避免限流
            
            print(f"  完成: {success}/{len(records)}")
        
        print("\n=== 导入完成 ===")
        return True


# 命令行入口
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 bookkeeping.py <账单文件.xlsx>")
        sys.exit(1)
    
    importer = BillImporter()
    importer.process_excel(sys.argv[1])
    importer.import_to_feishu()
