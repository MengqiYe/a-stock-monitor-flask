#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股数据获取模块
========================================

本模块负责从数据源获取A股市场数据，主要功能包括：
1. 获取A股实时行情数据
2. 获取个股历史K线数据
3. 获取热门股票排行榜
4. 股票搜索功能

数据源说明:
    - 主要数据源: akshare库（聚合东方财富等数据源）
    - 备用方案: 当网络不可达时，使用模拟数据进行演示

依赖:
    - akshare: 开源金融数据接口库
    - pandas: 数据处理库
    - numpy: 数值计算库

作者: MengqiYe
版本: 1.0.0
"""

import akshare as ak
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
import random


class AStockDataFetcher:
    """
    A股数据获取器类
    
    负责从数据源获取A股市场数据，并提供缓存机制以减少API调用频率。
    
    Attributes:
        cache (dict): 数据缓存字典
        cache_time (dict): 缓存时间记录字典
        cache_duration (int): 缓存有效期（秒），默认60秒
    
    Example:
        >>> fetcher = AStockDataFetcher()
        >>> df = fetcher.get_realtime_quotes()
        >>> print(df.head())
    """
    
    def __init__(self):
        """
        初始化数据获取器
        
        设置缓存容器和缓存有效期
        """
        self.cache = {}           # 缓存数据
        self.cache_time = {}      # 缓存时间戳
        self.cache_duration = 60  # 缓存有效期（秒）
    
    def _get_cached_data(self, key: str):
        """
        获取缓存数据
        
        Args:
            key (str): 缓存键名
        
        Returns:
            缓存的数据，如果缓存不存在或已过期则返回None
        """
        if key in self.cache and key in self.cache_time:
            # 检查缓存是否过期
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
    
    def _get_mock_data(self) -> pd.DataFrame:
        """
        生成模拟数据用于演示
        
        当无法从真实数据源获取数据时，生成模拟数据以支持系统演示。
        模拟数据包含常见的A股蓝筹股和热门股票。
        
        Returns:
            pd.DataFrame: 模拟的股票行情数据
        
        Note:
            模拟数据仅供演示使用，不反映真实市场情况
        """
        # 常见A股股票列表（蓝筹股和热门股票）
        stocks = [
            {'code': '600000', 'name': '浦发银行'},
            {'code': '600036', 'name': '招商银行'},
            {'code': '600519', 'name': '贵州茅台'},
            {'code': '600887', 'name': '伊利股份'},
            {'code': '600900', 'name': '长江电力'},
            {'code': '601318', 'name': '中国平安'},
            {'code': '601398', 'name': '工商银行'},
            {'code': '601857', 'name': '中国石油'},
            {'code': '601988', 'name': '中国银行'},
            {'code': '601288', 'name': '农业银行'},
            {'code': '600030', 'name': '中信证券'},
            {'code': '600276', 'name': '恒瑞医药'},
            {'code': '600585', 'name': '海螺水泥'},
            {'code': '600690', 'name': '海尔智家'},
            {'code': '600809', 'name': '山西汾酒'},
            {'code': '000001', 'name': '平安银行'},
            {'code': '000002', 'name': '万科A'},
            {'code': '000063', 'name': '中兴通讯'},
            {'code': '000333', 'name': '美的集团'},
            {'code': '000651', 'name': '格力电器'},
            {'code': '000725', 'name': '京东方A'},
            {'code': '000858', 'name': '五粮液'},
            {'code': '002415', 'name': '海康威视'},
            {'code': '002594', 'name': '比亚迪'},
            {'code': '300750', 'name': '宁德时代'},
        ]
        
        data = []
        for stock in stocks:
            # 生成随机但合理的股价数据
            pre_close = random.uniform(10, 500)  # 昨收价
            change_pct = random.uniform(-9.9, 9.9)  # 涨跌幅（-10% ~ 10%）
            price = pre_close * (1 + change_pct / 100)  # 最新价
            
            data.append({
                'code': stock['code'],
                'name': stock['name'],
                'price': round(price, 2),                    # 最新价
                'change_pct': round(change_pct, 2),          # 涨跌幅
                'change': round(price - pre_close, 2),       # 涨跌额
                'volume': random.randint(1000000, 100000000),  # 成交量
                'amount': random.randint(10000000, 1000000000),  # 成交额
                'amplitude': round(random.uniform(2, 15), 2),   # 振幅
                'high': round(price * (1 + random.uniform(0, 0.05)), 2),  # 最高价
                'low': round(price * (1 - random.uniform(0, 0.05)), 2),   # 最低价
                'open': round(price * (1 + random.uniform(-0.02, 0.02)), 2),  # 开盘价
                'pre_close': round(pre_close, 2),            # 昨收价
                'turnover_rate': round(random.uniform(0.5, 10), 2),  # 换手率
                'pe_ratio': round(random.uniform(5, 50), 2),     # 市盈率
                'pb_ratio': round(random.uniform(0.5, 10), 2),   # 市净率
                'total_mv': random.randint(1000000000, 10000000000000),     # 总市值
                'circ_mv': random.randint(500000000, 8000000000000)         # 流通市值
            })
        
        return pd.DataFrame(data)
    
    def get_realtime_quotes(self) -> pd.DataFrame:
        """
        获取A股实时行情数据
        
        从数据源获取所有A股股票的实时行情数据。
        如果数据源不可用，则使用模拟数据作为备用方案。
        
        Returns:
            pd.DataFrame: 包含实时行情数据的DataFrame，列为：
                - code: 股票代码
                - name: 股票名称
                - price: 最新价
                - change_pct: 涨跌幅（%）
                - change: 涨跌额
                - volume: 成交量
                - amount: 成交额
                - amplitude: 振幅（%）
                - high: 最高价
                - low: 最低价
                - open: 开盘价
                - pre_close: 昨收价
                - turnover_rate: 换手率（%）
                - pe_ratio: 市盈率
                - pb_ratio: 市净率
                - total_mv: 总市值
                - circ_mv: 流通市值
        
        Example:
            >>> df = fetcher.get_realtime_quotes()
            >>> print(df[['code', 'name', 'price', 'change_pct']].head())
        """
        cache_key = "realtime_quotes"
        
        # 尝试从缓存获取数据
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 从akshare获取A股实时行情数据
            # 数据来源：东方财富网
            df = ak.stock_zh_a_spot_em()
            
            # 数据清洗：将中文列名转换为英文标准列名
            df = df.rename(columns={
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '最高': 'high',
                '最低': 'low',
                '今开': 'open',
                '昨收': 'pre_close',
                '换手率': 'turnover_rate',
                '市盈率-动态': 'pe_ratio',
                '市净率': 'pb_ratio',
                '总市值': 'total_mv',
                '流通市值': 'circ_mv'
            })
            
            # 处理百分比字符串（akshare返回的涨跌幅可能是字符串格式）
            if 'change_pct' in df.columns:
                df['change_pct'] = df['change_pct'].astype(str).str.replace('%', '').astype(float)
            
            # 存入缓存
            self._set_cache(cache_key, df)
            return df
            
        except Exception as e:
            # 数据源不可用时，使用模拟数据
            print(f"获取实时行情失败: {e}")
            print("使用模拟数据进行演示...")
            mock_df = self._get_mock_data()
            self._set_cache(cache_key, mock_df)
            return mock_df
    
    def get_stock_history(self, code: str, days: int = 60) -> pd.DataFrame:
        """
        获取股票历史K线数据
        
        获取指定股票的历史日线数据，用于技术分析和趋势判断。
        
        Args:
            code (str): 股票代码（如：600519）
            days (int, optional): 需要获取的历史天数，默认60天
        
        Returns:
            pd.DataFrame: 包含历史K线数据的DataFrame，列为：
                - date: 日期
                - open: 开盘价
                - close: 收盘价
                - high: 最高价
                - low: 最低价
                - volume: 成交量
                - amount: 成交额
                - amplitude: 振幅（%）
                - change_pct: 涨跌幅（%）
                - change: 涨跌额
                - turnover_rate: 换手率（%）
        
        Example:
            >>> df = fetcher.get_stock_history('600519', days=30)
            >>> print(df.tail())
        """
        cache_key = f"history_{code}_{days}"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            
            # 从akshare获取历史数据
            # period="daily": 日线数据
            # adjust="qfq": 前复权处理
            df = ak.stock_zh_a_hist(
                symbol=code, 
                period="daily", 
                start_date=start_date, 
                end_date=end_date, 
                adjust="qfq"  # 前复权，处理分红送股
            )
            
            if not df.empty:
                # 重命名列
                df = df.rename(columns={
                    '日期': 'date',
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume',
                    '成交额': 'amount',
                    '振幅': 'amplitude',
                    '涨跌幅': 'change_pct',
                    '涨跌额': 'change',
                    '换手率': 'turnover_rate'
                })
                
                # 只取最近指定天数的数据
                df = df.tail(days)
                
            self._set_cache(cache_key, df)
            return df
            
        except Exception as e:
            print(f"获取股票{code}历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, code: str) -> Dict:
        """
        获取个股详细信息
        
        获取指定股票的完整信息，包括实时行情和历史数据。
        
        Args:
            code (str): 股票代码（如：600519）
        
        Returns:
            Dict: 包含股票完整信息的字典：
                - 实时行情数据（价格、涨跌幅等）
                - history: 历史K线数据列表
        
        Example:
            >>> info = fetcher.get_stock_info('600519')
            >>> print(info['name'], info['price'])
        """
        try:
            # 获取实时行情
            realtime_df = self.get_realtime_quotes()
            stock_data = realtime_df[realtime_df['code'] == code]
            
            if stock_data.empty:
                return {}
            
            # 转换为字典
            info = stock_data.iloc[0].to_dict()
            
            # 获取历史数据
            history = self.get_stock_history(code, days=60)
            if not history.empty:
                info['history'] = history.to_dict('records')
            
            return info
            
        except Exception as e:
            print(f"获取股票{code}信息失败: {e}")
            return {}
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """
        搜索股票
        
        根据关键词搜索股票，支持按代码或名称模糊匹配。
        
        Args:
            keyword (str): 搜索关键词（股票代码或名称的一部分）
        
        Returns:
            pd.DataFrame: 匹配的股票列表
        
        Example:
            >>> df = fetcher.search_stocks('茅台')
            >>> print(df[['code', 'name']])
        """
        try:
            df = self.get_realtime_quotes()
            
            # 按代码或名称进行模糊匹配
            mask = (
                df['code'].str.contains(keyword, case=False, na=False) |
                df['name'].str.contains(keyword, case=False, na=False)
            )
            
            return df[mask]
            
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return pd.DataFrame()
    
    def get_hot_stocks(self, top: int = 10) -> Dict:
        """
        获取热门股票排行榜
        
        根据不同维度获取热门股票排行榜，包括涨幅榜、跌幅榜、
        成交额榜和换手率榜。
        
        Args:
            top (int, optional): 每个榜单返回的股票数量，默认10
        
        Returns:
            Dict: 包含四个排行榜的字典：
                - gainers: 涨幅榜（涨幅最大的股票）
                - losers: 跌幅榜（跌幅最大的股票）
                - volume_top: 成交额榜（成交额最大的股票）
                - turnover_top: 换手率榜（换手率最高的股票）
        
        Example:
            >>> hot = fetcher.get_hot_stocks(top=5)
            >>> print(hot['gainers'][0]['name'])  # 涨幅第一的股票
        """
        try:
            df = self.get_realtime_quotes()
            
            # 涨幅榜：按涨跌幅降序排列
            gainers = df.nlargest(top, 'change_pct')
            
            # 跌幅榜：按涨跌幅升序排列
            losers = df.nsmallest(top, 'change_pct')
            
            # 成交额榜：按成交额降序排列
            volume_top = df.nlargest(top, 'amount')
            
            # 换手率榜：按换手率降序排列
            turnover_top = df.nlargest(top, 'turnover_rate')
            
            return {
                'gainers': gainers.to_dict('records'),
                'losers': losers.to_dict('records'),
                'volume_top': volume_top.to_dict('records'),
                'turnover_top': turnover_top.to_dict('records')
            }
            
        except Exception as e:
            print(f"获取热门股票失败: {e}")
            return {
                'gainers': [],
                'losers': [],
                'volume_top': [],
                'turnover_top': []
            }


# ==================== 全局实例 ====================

# 创建全局单例实例，供其他模块导入使用
fetcher = AStockDataFetcher()
