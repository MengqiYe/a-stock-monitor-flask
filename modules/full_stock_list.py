#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股完整股票列表模块
========================================
包含所有A股上市股票，按市场和行业分类

数据来源：akshare实时获取 + 离线缓存
"""

import akshare as ak
import pandas as pd
from typing import Dict, List, Optional
import time

# ==================== 行业分类 ====================
INDUSTRY_CATEGORIES = {
    '银行': ['银行'],
    '证券': ['证券', '券商'],
    '保险': ['保险'],
    '房地产': ['房地产', '地产', '房产'],
    '医药生物': ['医药', '生物', '制药', '医疗', '中药', '化学制药', '生物制品', '医疗服务', '医疗器械'],
    '食品饮料': ['食品', '饮料', '白酒', '啤酒', '乳制品', '调味品', '肉制品'],
    '家用电器': ['家电', '白色家电', '小家电', '厨电', '家电零部件'],
    '汽车': ['汽车', '整车', '零部件', '新能源汽车', '汽车电子'],
    '电子': ['电子', '半导体', '芯片', '消费电子', '光学', '面板', 'PCB', '电子元件'],
    '计算机': ['计算机', '软件', 'IT服务', '信息技术', '互联网', '人工智能', '大数据', '云计算'],
    '通信': ['通信', '5G', '通信设备', '光通信'],
    '传媒': ['传媒', '影视', '游戏', '广告', '出版', '广电'],
    '电力设备': ['电力设备', '光伏', '风电', '储能', '电池', '锂电', '新能源'],
    '机械设备': ['机械', '工程机械', '机床', '仪器仪表', '专用设备', '通用设备'],
    '国防军工': ['军工', '航空', '航天', '兵器', '船舶'],
    '化工': ['化工', '化学', '化纤', '橡胶', '塑料', '氯碱', '聚氨酯'],
    '有色金属': ['有色金属', '锂', '铜', '铝', '锌', '稀土', '黄金'],
    '煤炭': ['煤炭', '焦炭'],
    '石油石化': ['石油', '石化', '油气', '油服'],
    '钢铁': ['钢铁', '特钢', '普钢'],
    '建筑材料': ['建材', '水泥', '玻璃', '装饰材料'],
    '建筑装饰': ['建筑装饰', '装修', '园林'],
    '公用事业': ['公用事业', '水务', '燃气', '环保', '电力', '水电', '火电'],
    '交通运输': ['交通运输', '航空', '机场', '港口', '高速', '铁路', '物流'],
    '商业贸易': ['商业', '贸易', '零售', '百货', '超市'],
    '休闲服务': ['休闲', '旅游', '酒店', '餐饮'],
    '农林牧渔': ['农业', '林业', '牧业', '渔业', '种业', '饲料'],
    '轻工制造': ['轻工', '造纸', '包装', '家具', '文具'],
    '纺织服饰': ['纺织', '服装', '鞋帽', '纺织制造'],
    '美容护理': ['美容', '化妆品', '护肤'],
    '非银金融': ['信托', '期货', '多元金融'],
}

# ==================== 市场分类 ====================
MARKET_CATEGORIES = {
    'sh_main': {'name': '沪市主板', 'prefix': ['600', '601', '603', '605']},
    'sh_star': {'name': '科创板', 'prefix': ['688']},
    'sz_main': {'name': '深市主板', 'prefix': ['000', '001']},
    'sz_sme': {'name': '中小板', 'prefix': ['002']},
    'sz_chinext': {'name': '创业板', 'prefix': ['300', '301']},
    'bj_main': {'name': '北交所', 'prefix': ['8', '4']},
}

def get_market_by_code(code: str) -> str:
    """根据股票代码判断市场"""
    if code.startswith(('600', '601', '603', '605')):
        return 'sh_main'
    elif code.startswith('688'):
        return 'sh_star'
    elif code.startswith(('000', '001')):
        return 'sz_main'
    elif code.startswith('002'):
        return 'sz_sme'
    elif code.startswith(('300', '301')):
        return 'sz_chinext'
    elif code.startswith(('8', '4')):
        return 'bj_main'
    return 'unknown'

def get_industry_by_name(name: str) -> str:
    """根据股票名称推断行业"""
    for industry, keywords in INDUSTRY_CATEGORIES.items():
        for keyword in keywords:
            if keyword in name:
                return industry
    return '其他'

class StockListManager:
    """股票列表管理器"""
    
    def __init__(self):
        self.cache = None
        self.cache_time = 0
        self.cache_duration = 3600  # 1小时缓存
    
    def get_all_stocks(self, use_cache: bool = True) -> pd.DataFrame:
        """
        获取所有A股股票列表
        
        Returns:
            pd.DataFrame: 股票列表，包含代码、名称、市场、行业等
        """
        # 检查缓存
        if use_cache and self.cache is not None:
            if time.time() - self.cache_time < self.cache_duration:
                return self.cache
        
        try:
            # 从akshare获取A股股票列表
            df = ak.stock_info_a_code_name()
            
            # 添加市场分类
            df['market'] = df['code'].apply(get_market_by_code)
            df['market_name'] = df['market'].apply(
                lambda x: MARKET_CATEGORIES.get(x, {}).get('name', '未知')
            )
            
            # 添加行业分类（简化版，基于名称推断）
            df['industry'] = df['name'].apply(get_industry_by_name)
            
            # 缓存结果
            self.cache = df
            self.cache_time = time.time()
            
            return df
            
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            # 返回空DataFrame
            return pd.DataFrame(columns=['code', 'name', 'market', 'market_name', 'industry'])
    
    def get_stocks_by_market(self, market: str) -> pd.DataFrame:
        """按市场获取股票"""
        df = self.get_all_stocks()
        return df[df['market'] == market]
    
    def get_stocks_by_industry(self, industry: str) -> pd.DataFrame:
        """按行业获取股票"""
        df = self.get_all_stocks()
        return df[df['industry'] == industry]
    
    def get_market_statistics(self) -> Dict:
        """获取市场统计信息"""
        df = self.get_all_stocks()
        
        stats = {
            'total': len(df),
            'by_market': {},
            'by_industry': {}
        }
        
        # 按市场统计
        for market_code, market_info in MARKET_CATEGORIES.items():
            count = len(df[df['market'] == market_code])
            if count > 0:
                stats['by_market'][market_code] = {
                    'name': market_info['name'],
                    'count': count
                }
        
        # 按行业统计
        industry_counts = df['industry'].value_counts()
        for industry, count in industry_counts.items():
            stats['by_industry'][industry] = count
        
        return stats

# 全局实例
stock_list_manager = StockListManager()
