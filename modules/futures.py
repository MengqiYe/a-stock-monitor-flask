#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
国内期货市场数据模块
========================================

提供国内期货市场实时行情、品种分类、全球期货等功能

数据来源：akshare

主要交易所：
- 上海期货交易所 (SHFE): 铜、铝、锌、铅、镍、锡、黄金、白银、原油等
- 大连商品交易所 (DCE): 豆粕、豆油、玉米、铁矿石、焦炭、焦煤等
- 郑州商品交易所 (CZCE): PTA、棉花、白糖、菜油、动力煤等
- 中国金融期货交易所 (CFFEX): 股指期货、国债期货
- 广州期货交易所 (GFEX): 工业硅、碳酸锂等
- 上海国际能源交易中心 (INE): 原油、20号胶等
"""

import akshare as ak
import pandas as pd
from typing import Dict, List, Optional, Tuple
import time


# ==================== 交易所分类 ====================
EXCHANGE_INFO = {
    'SHFE': {
        'name': '上海期货交易所',
        'short_name': '上期所',
        'products': ['铜', '铝', '锌', '铅', '镍', '锡', '黄金', '白银', '螺纹钢', '热卷', '燃料油', '沥青', '橡胶', '纸浆', '不锈钢']
    },
    'DCE': {
        'name': '大连商品交易所',
        'short_name': '大商所',
        'products': ['豆一', '豆二', '豆粕', '豆油', '玉米', '玉米淀粉', '铁矿石', '焦炭', '焦煤', '聚乙烯', '聚丙烯', 'PVC', '棕榈油', '鸡蛋', '纤维板', '胶合板', '苯乙烯', '乙二醇', '液化石油气', '生猪']
    },
    'CZCE': {
        'name': '郑州商品交易所',
        'short_name': '郑商所',
        'products': ['PTA', '棉花', '白糖', '菜油', '菜粕', '动力煤', '玻璃', '纯碱', '尿素', '甲醇', '短纤', '红枣', '花生', '苹果', '锰硅', '硅铁', '棉纱']
    },
    'CFFEX': {
        'name': '中国金融期货交易所',
        'short_name': '中金所',
        'products': ['沪深300', '上证50', '中证500', '中证1000', '2年国债', '5年国债', '10年国债', '30年国债']
    },
    'GFEX': {
        'name': '广州期货交易所',
        'short_name': '广期所',
        'products': ['工业硅', '碳酸锂']
    },
    'INE': {
        'name': '上海国际能源交易中心',
        'short_name': '能源中心',
        'products': ['原油', '20号胶']
    }
}

# ==================== 品种分类 ====================
PRODUCT_CATEGORIES = {
    '有色金属': ['铜', '铝', '锌', '铅', '镍', '锡', '工业硅', '碳酸锂'],
    '贵金属': ['黄金', '白银'],
    '黑色系': ['螺纹钢', '热卷', '铁矿石', '焦炭', '焦煤', '硅铁', '锰硅', '不锈钢'],
    '能源化工': ['原油', '燃料油', '沥青', '橡胶', 'PTA', '甲醇', '聚乙烯', '聚丙烯', 'PVC', '纯碱', '玻璃', '尿素', '乙二醇', '苯乙烯', '液化石油气', '纸浆', '20号胶', '动力煤'],
    '农产品': ['豆一', '豆二', '豆粕', '豆油', '玉米', '玉米淀粉', '棕榈油', '棉花', '白糖', '菜油', '菜粕', '鸡蛋', '红枣', '花生', '苹果', '棉纱'],
    '软商品': ['白糖', '棉花', '橡胶', '纸浆'],
    '油脂油料': ['豆一', '豆二', '豆粕', '豆油', '菜油', '菜粕', '棕榈油'],
    '金融期货': ['沪深300', '上证50', '中证500', '中证1000', '国债'],
}


class FuturesDataFetcher:
    """
    期货数据获取器
    
    提供国内期货市场的实时行情、品种分类等功能
    
    Attributes:
        cache (dict): 数据缓存字典
        cache_time (dict): 缓存时间记录字典
        cache_duration (int): 缓存有效期（秒）
    """
    
    def __init__(self):
        """
        初始化期货数据获取器
        
        设置缓存容器和缓存有效期
        """
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 30  # 期货数据更新快，缓存30秒
    
    def _get_cached_data(self, key: str):
        """
        获取缓存数据
        
        Args:
            key (str): 缓存键名
        
        Returns:
            缓存的数据，如果缓存不存在或已过期则返回None
        """
        if key in self.cache and key in self.cache_time:
            if time.time() - self.cache_time[key] < self.cache_duration:
                return self.cache[key]
        return None
    
    def _set_cache(self, key: str, data):
        """
        设置缓存数据
        
        Args:
            key (str): 缓存键名
            data: 要缓存的数据
        """
        self.cache[key] = data
        self.cache_time[key] = time.time()
    
    def get_realtime_quotes(self) -> pd.DataFrame:
        """
        获取期货实时行情
        
        Returns:
            pd.DataFrame: 期货行情数据，包含：
                - symbol: 合约代码
                - exchange: 交易所
                - name: 合约名称
                - trade: 最新价
                - settlement: 结算价
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - close: 收盘价
                - volume: 成交量
                - position: 持仓量
                - changepercent: 涨跌幅
        """
        cached = self._get_cached_data('realtime_quotes')
        if cached is not None:
            return cached
        
        try:
            df = ak.futures_zh_realtime()
            
            # 添加交易所中文名
            exchange_map = {
                'shfe': '上期所',
                'dce': '大商所',
                'czce': '郑商所',
                'cffex': '中金所',
                'gfex': '广期所',
                'ine': '能源中心'
            }
            df['exchange_name'] = df['exchange'].map(lambda x: exchange_map.get(x.lower(), x))
            
            # 添加涨跌幅计算（基于昨结算价）
            if 'presettlement' in df.columns and 'trade' in df.columns:
                df['change_pct'] = ((df['trade'] - df['presettlement']) / df['presettlement'] * 100).round(2)
            
            self._set_cache('realtime_quotes', df)
            return df
            
        except Exception as e:
            print(f"获取期货实时行情失败: {e}")
            return pd.DataFrame()
    
    def get_main_contracts(self) -> pd.DataFrame:
        """
        获取主力合约列表
        
        Returns:
            pd.DataFrame: 主力合约列表
        """
        cached = self._get_cached_data('main_contracts')
        if cached is not None:
            return cached
        
        try:
            df = ak.futures_display_main_sina()
            
            # 添加交易所中文名
            exchange_map = {
                'shfe': '上期所',
                'dce': '大商所',
                'czce': '郑商所',
                'cffex': '中金所',
                'gfex': '广期所',
                'ine': '能源中心'
            }
            df['exchange_name'] = df['exchange'].map(lambda x: exchange_map.get(x.lower(), x))
            
            self._set_cache('main_contracts', df)
            return df
            
        except Exception as e:
            print(f"获取主力合约列表失败: {e}")
            return pd.DataFrame()
    
    def get_global_futures(self) -> pd.DataFrame:
        """
        获取全球期货行情
        
        Returns:
            pd.DataFrame: 全球期货行情数据
        """
        cached = self._get_cached_data('global_futures')
        if cached is not None:
            return cached
        
        try:
            df = ak.futures_global_spot_em()
            self._set_cache('global_futures', df)
            return df
            
        except Exception as e:
            print(f"获取全球期货行情失败: {e}")
            return pd.DataFrame()
    
    def get_product_symbols(self) -> pd.DataFrame:
        """
        获取期货品种标记
        
        Returns:
            pd.DataFrame: 品种标记数据
        """
        cached = self._get_cached_data('product_symbols')
        if cached is not None:
            return cached
        
        try:
            df = ak.futures_symbol_mark()
            self._set_cache('product_symbols', df)
            return df
            
        except Exception as e:
            print(f"获取期货品种标记失败: {e}")
            return pd.DataFrame()
    
    def get_quotes_by_exchange(self, exchange: str) -> pd.DataFrame:
        """
        按交易所获取期货行情
        
        Args:
            exchange (str): 交易所代码（shfe/dce/czce/cffex/gfex/ine）
        
        Returns:
            pd.DataFrame: 指定交易所的期货行情
        """
        df = self.get_realtime_quotes()
        if df.empty:
            return df
        
        return df[df['exchange'].str.lower() == exchange.lower()]
    
    def get_quotes_by_category(self, category: str) -> pd.DataFrame:
        """
        按品种分类获取期货行情
        
        Args:
            category (str): 品种分类（有色金属/贵金属/黑色系等）
        
        Returns:
            pd.DataFrame: 指定分类的期货行情
        """
        df = self.get_realtime_quotes()
        if df.empty:
            return df
        
        keywords = PRODUCT_CATEGORIES.get(category, [])
        if not keywords:
            return df
        
        # 匹配名称中包含关键词的合约
        mask = df['name'].apply(lambda x: any(kw in str(x) for kw in keywords))
        return df[mask]
    
    def get_market_stats(self) -> Dict:
        """
        获取期货市场统计
        
        Returns:
            Dict: 市场统计数据
        """
        df = self.get_realtime_quotes()
        if df.empty:
            return {
                'total_contracts': 0,
                'up_count': 0,
                'down_count': 0,
                'flat_count': 0,
                'limit_up': 0,
                'limit_down': 0
            }
        
        # 统计涨跌
        if 'change_pct' in df.columns:
            up_count = len(df[df['change_pct'] > 0])
            down_count = len(df[df['change_pct'] < 0])
            flat_count = len(df[df['change_pct'] == 0])
            
            # 涨停跌停统计（假设涨跌幅超过5%为涨停/跌停）
            limit_up = len(df[df['change_pct'] >= 5])
            limit_down = len(df[df['change_pct'] <= -5])
        else:
            up_count = down_count = flat_count = limit_up = limit_down = 0
        
        return {
            'total_contracts': len(df),
            'up_count': up_count,
            'down_count': down_count,
            'flat_count': flat_count,
            'limit_up': limit_up,
            'limit_down': limit_down
        }
    
    def get_exchange_stats(self) -> List[Dict]:
        """
        获取各交易所统计
        
        Returns:
            List[Dict]: 各交易所统计数据
        """
        df = self.get_realtime_quotes()
        if df.empty:
            return []
        
        stats = []
        for code, info in EXCHANGE_INFO.items():
            exchange_df = df[df['exchange'].str.lower() == code.lower()]
            if exchange_df.empty:
                continue
            
            if 'change_pct' in exchange_df.columns:
                up_count = len(exchange_df[exchange_df['change_pct'] > 0])
                down_count = len(exchange_df[exchange_df['change_pct'] < 0])
                avg_change = exchange_df['change_pct'].mean()
            else:
                up_count = down_count = 0
                avg_change = 0
            
            stats.append({
                'code': code,
                'name': info['name'],
                'short_name': info['short_name'],
                'contract_count': len(exchange_df),
                'up_count': up_count,
                'down_count': down_count,
                'avg_change': round(avg_change, 2) if avg_change else 0
            })
        
        return stats
    
    def get_top_gainers(self, n: int = 10) -> pd.DataFrame:
        """
        获取涨幅最大的合约
        
        Args:
            n (int): 返回数量
        
        Returns:
            pd.DataFrame: 涨幅TOP N合约
        """
        df = self.get_realtime_quotes()
        if df.empty or 'change_pct' not in df.columns:
            return pd.DataFrame()
        
        # 过滤主力合约（以0结尾的合约代码）
        main_df = df[df['symbol'].str.endswith('0')]
        
        return main_df.nlargest(n, 'change_pct')
    
    def get_top_losers(self, n: int = 10) -> pd.DataFrame:
        """
        获取跌幅最大的合约
        
        Args:
            n (int): 返回数量
        
        Returns:
            pd.DataFrame: 跌幅TOP N合约
        """
        df = self.get_realtime_quotes()
        if df.empty or 'change_pct' not in df.columns:
            return pd.DataFrame()
        
        # 过滤主力合约
        main_df = df[df['symbol'].str.endswith('0')]
        
        return main_df.nsmallest(n, 'change_pct')
    
    def get_top_volume(self, n: int = 10) -> pd.DataFrame:
        """
        获取成交量最大的合约
        
        Args:
            n (int): 返回数量
        
        Returns:
            pd.DataFrame: 成交量TOP N合约
        """
        df = self.get_realtime_quotes()
        if df.empty or 'volume' not in df.columns:
            return pd.DataFrame()
        
        return df.nlargest(n, 'volume')
    
    def get_top_position(self, n: int = 10) -> pd.DataFrame:
        """
        获取持仓量最大的合约
        
        Args:
            n (int): 返回数量
        
        Returns:
            pd.DataFrame: 持仓量TOP N合约
        """
        df = self.get_realtime_quotes()
        if df.empty or 'position' not in df.columns:
            return pd.DataFrame()
        
        return df.nlargest(n, 'position')


# 创建全局实例
futures_fetcher = FuturesDataFetcher()
