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
from modules.stock_list import ALL_STOCKS, SZ50_STOCKS, ZZ500_STOCKS, HK_STOCKS, MAIN_INDICES, HK_INDICES, get_index_components, get_index_info


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
        模拟数据包含A股各市场的代表性股票。
        
        Returns:
            pd.DataFrame: 模拟的股票行情数据
        
        Note:
            模拟数据仅供演示使用，不反映真实市场情况
        """
        # 使用上证50和中证500所有成分股
        stocks = ALL_STOCKS
        
        data = []
        for stock in stocks:
            # 根据股票代码判断市场
            code = stock['code']
            if code.startswith('6'):
                market = 'sh'  # 上海
                market_name = '沪市'
            elif code.startswith('000') or code.startswith('001'):
                market = 'sz'  # 深市主板
                market_name = '深市主板'
            elif code.startswith('002'):
                market = 'sz'  # 中小板
                market_name = '中小板'
            elif code.startswith('300'):
                market = 'sz'  # 创业板
                market_name = '创业板'
            elif code.startswith('688'):
                market = 'sh'  # 科创板
                market_name = '科创板'
            else:
                market = 'sz'
                market_name = '深市'
            
            # 生成随机但合理的股价数据
            pre_close = random.uniform(10, 500)  # 昨收价
            change_pct = random.uniform(-9.9, 9.9)  # 涨跌幅（-10% ~ 10%）
            price = pre_close * (1 + change_pct / 100)  # 最新价
            
            data.append({
                'code': code,
                'name': stock['name'],
                'market': market,
                'market_name': market_name,
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
    
    def _get_mock_indices(self) -> pd.DataFrame:
        """
        生成模拟指数数据
        
        Returns:
            pd.DataFrame: 模拟的指数行情数据
        """
        data = []
        for idx in MAIN_INDICES:
            pre_close = random.uniform(1000, 15000)  # 指数点位
            change_pct = random.uniform(-3, 3)  # 指数涨跌幅一般较小
            price = pre_close * (1 + change_pct / 100)
            
            data.append({
                'code': idx['code'],
                'name': idx['name'],
                'market': idx['market'],
                'price': round(price, 2),
                'change_pct': round(change_pct, 2),
                'change': round(price - pre_close, 2),
                'high': round(price * (1 + random.uniform(0, 0.02)), 2),
                'low': round(price * (1 - random.uniform(0, 0.02)), 2),
                'open': round(price * (1 + random.uniform(-0.01, 0.01)), 2),
                'pre_close': round(pre_close, 2),
                'volume': random.randint(100000000, 10000000000),
                'amount': random.randint(10000000000, 1000000000000),
            })
        
        return pd.DataFrame(data)
    
    def _get_mock_hk_stocks(self) -> pd.DataFrame:
        """
        生成模拟港股数据
        
        Returns:
            pd.DataFrame: 模拟的港股行情数据
        """
        data = []
        for stock in HK_STOCKS:
            pre_close = random.uniform(5, 500)  # 港股股价
            change_pct = random.uniform(-9.9, 9.9)
            price = pre_close * (1 + change_pct / 100)
            
            data.append({
                'code': stock['code'],
                'name': stock['name'],
                'market': 'hk',
                'market_name': '港股',
                'price': round(price, 2),
                'change_pct': round(change_pct, 2),
                'change': round(price - pre_close, 2),
                'volume': random.randint(1000000, 100000000),
                'amount': random.randint(10000000, 10000000000),  # 港股成交额较大
                'amplitude': round(random.uniform(2, 15), 2),
                'high': round(price * (1 + random.uniform(0, 0.05)), 2),
                'low': round(price * (1 - random.uniform(0, 0.05)), 2),
                'open': round(price * (1 + random.uniform(-0.02, 0.02)), 2),
                'pre_close': round(pre_close, 2),
                'turnover_rate': round(random.uniform(0.1, 10), 2),
            })
        
        return pd.DataFrame(data)
    
    def _get_mock_hk_indices(self) -> pd.DataFrame:
        """
        生成模拟港股指数数据
        
        Returns:
            pd.DataFrame: 模拟的港股指数数据
        """
        data = []
        for idx in HK_INDICES:
            if idx['code'] == 'HSI':
                pre_close = random.uniform(15000, 25000)  # 恒生指数
            elif idx['code'] == 'HSCEI':
                pre_close = random.uniform(5000, 10000)  # 国企指数
            else:
                pre_close = random.uniform(3000, 5000)  # 科技指数
            
            change_pct = random.uniform(-3, 3)
            price = pre_close * (1 + change_pct / 100)
            
            data.append({
                'code': idx['code'],
                'name': idx['name'],
                'market': 'hk',
                'price': round(price, 2),
                'change_pct': round(change_pct, 2),
                'change': round(price - pre_close, 2),
                'high': round(price * (1 + random.uniform(0, 0.02)), 2),
                'low': round(price * (1 - random.uniform(0, 0.02)), 2),
                'open': round(price * (1 + random.uniform(-0.01, 0.01)), 2),
                'pre_close': round(pre_close, 2),
                'volume': random.randint(100000000, 10000000000),
                'amount': random.randint(10000000000, 200000000000),
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
    
    def search_stocks(self, keyword: str, limit: int = 50) -> pd.DataFrame:
        """
        搜索股票
        
        根据关键词搜索股票，支持按代码或名称模糊匹配。
        结果按匹配优先级排序：完全匹配 > 前缀匹配 > 包含匹配
        
        Args:
            keyword (str): 搜索关键词（股票代码或名称的一部分）
            limit (int, optional): 返回结果数量限制，默认50
        
        Returns:
            pd.DataFrame: 匹配的股票列表，按相关性排序
        
        Example:
            >>> df = fetcher.search_stocks('茅台')
            >>> print(df[['code', 'name']])
        """
        try:
            df = self.get_realtime_quotes()
            
            if not keyword or df.empty:
                return pd.DataFrame()
            
            keyword_lower = keyword.lower()
            
            # 计算匹配分数和筛选结果
            results = []
            for idx, row in df.iterrows():
                code = str(row.get('code', '')).lower()
                name = str(row.get('name', '')).lower()
                score = 0
                
                # 完全匹配（最高优先级）
                if code == keyword_lower or name == keyword_lower:
                    score = 100
                # 代码前缀匹配
                elif code.startswith(keyword_lower):
                    score = 90
                # 名称前缀匹配
                elif name.startswith(keyword_lower):
                    score = 80
                # 代码包含匹配
                elif keyword_lower in code:
                    score = 70
                # 名称包含匹配
                elif keyword_lower in name:
                    score = 60
                
                if score > 0:
                    results.append((idx, score))
            
            # 按分数排序
            results.sort(key=lambda x: x[1], reverse=True)
            
            # 获取排序后的索引
            sorted_indices = [r[0] for r in results[:limit]]
            
            if sorted_indices:
                return df.loc[sorted_indices]
            else:
                return pd.DataFrame()
            
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
    
    def classify_stocks_by_market(self, df: pd.DataFrame = None) -> Dict:
        """
        按市场分类股票
        
        将股票按交易所和板块进行分类，包括沪市主板、深市主板、
        创业板、科创板、北交所等。
        
        Args:
            df (pd.DataFrame, optional): 股票数据，如果为None则获取实时数据
        
        Returns:
            Dict: 包含各市场股票数据的字典：
                - sh_main: 沪市主板（代码以600、601、603开头）
                - sz_main: 深市主板（代码以000、001开头）
                - gem: 创业板（代码以300开头）
                - star: 科创板（代码以688开头）
                - bse: 北交所（代码以8开头）
        
        Example:
            >>> markets = fetcher.classify_stocks_by_market()
            >>> print(f"沪市主板: {len(markets['sh_main'])}只")
        """
        if df is None:
            df = self.get_realtime_quotes()
        
        result = {
            'sh_main': pd.DataFrame(),    # 沪市主板
            'sz_main': pd.DataFrame(),    # 深市主板
            'gem': pd.DataFrame(),        # 创业板
            'star': pd.DataFrame(),       # 科创板
            'bse': pd.DataFrame()         # 北交所
        }
        
        try:
            # 沪市主板：600、601、603开头
            result['sh_main'] = df[df['code'].str.match(r'^(600|601|603)')]
            
            # 深市主板：000、001开头
            result['sz_main'] = df[df['code'].str.match(r'^(000|001)')]
            
            # 创业板：300开头
            result['gem'] = df[df['code'].str.match(r'^300')]
            
            # 科创板：688开头
            result['star'] = df[df['code'].str.match(r'^688')]
            
            # 北交所：8开头（通常为83、87、88）
            result['bse'] = df[df['code'].str.match(r'^8')]
            
        except Exception as e:
            print(f"市场分类失败: {e}")
        
        return result
    
    def get_market_statistics(self) -> Dict:
        """
        获取市场全景统计
        
        计算整个A股市场的统计指标，包括涨跌分布、成交额、
        市值等关键指标。
        
        Returns:
            Dict: 市场统计数据：
                - total_stocks: 股票总数
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - flat_count: 平盘股票数
                - limit_up: 涨停股票数
                - limit_down: 跌停股票数
                - avg_change: 平均涨跌幅
                - total_amount: 总成交额
                - total_volume: 总成交量
                - market_sentiment: 市场情绪指标（0-100）
                - market_stats: 各市场统计
                - new_high_count: 创新高股票数
                - new_low_count: 创新低股票数
        
        Example:
            >>> stats = fetcher.get_market_statistics()
            >>> print(f"上涨: {stats['up_count']}, 下跌: {stats['down_count']}")
        """
        cache_key = "market_statistics"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            df = self.get_realtime_quotes()
            markets = self.classify_stocks_by_market(df)
            
            # 基础统计
            total_stocks = len(df)
            up_count = len(df[df['change_pct'] > 0])
            down_count = len(df[df['change_pct'] < 0])
            flat_count = len(df[df['change_pct'] == 0])
            
            # 涨跌停统计（涨跌幅接近10%或20%）
            # 主板涨跌停约10%，创业板/科创板约20%
            limit_up = len(df[df['change_pct'] >= 9.5])
            limit_down = len(df[df['change_pct'] <= -9.5])
            
            # 平均涨跌幅
            avg_change = df['change_pct'].mean()
            
            # 总成交额和成交量
            total_amount = df['amount'].sum()
            total_volume = df['volume'].sum()
            
            # 市场情绪指标（基于涨跌比例计算）
            if total_stocks > 0:
                market_sentiment = round(up_count / total_stocks * 100, 2)
            else:
                market_sentiment = 50
            
            # 各市场统计
            market_stats = {}
            for market_name, market_df in markets.items():
                if len(market_df) > 0:
                    market_stats[market_name] = {
                        'count': len(market_df),
                        'up_count': len(market_df[market_df['change_pct'] > 0]),
                        'down_count': len(market_df[market_df['change_pct'] < 0]),
                        'avg_change': round(market_df['change_pct'].mean(), 2),
                        'total_amount': float(market_df['amount'].sum()),
                        'top_gainer': market_df.nlargest(1, 'change_pct').to_dict('records')[0] if len(market_df) > 0 else None,
                        'top_loser': market_df.nsmallest(1, 'change_pct').to_dict('records')[0] if len(market_df) > 0 else None
                    }
            
            # 创新高/新低统计（使用振幅判断）
            new_high_count = len(df[df['high'] == df['high'].rolling(60, min_periods=1).max()])
            new_low_count = len(df[df['low'] == df['low'].rolling(60, min_periods=1).min()])
            
            result = {
                'total_stocks': total_stocks,
                'up_count': up_count,
                'down_count': down_count,
                'flat_count': flat_count,
                'limit_up': limit_up,
                'limit_down': limit_down,
                'avg_change': round(avg_change, 2),
                'total_amount': float(total_amount),
                'total_volume': float(total_volume),
                'market_sentiment': market_sentiment,
                'market_stats': market_stats,
                'new_high_count': new_high_count,
                'new_low_count': new_low_count,
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"获取市场统计失败: {e}")
            return {}
    
    def get_industry_board(self) -> pd.DataFrame:
        """
        获取行业板块行情
        
        获取各行业板块的实时行情数据，包括涨跌幅、成交额等。
        
        Returns:
            pd.DataFrame: 行业板块数据，列为：
                - name: 板块名称
                - change_pct: 涨跌幅
                - up_count: 上涨股票数
                - down_count: 下跌股票数
                - lead_stock: 领涨股票
                - total_amount: 成交额
        
        Example:
            >>> df = fetcher.get_industry_board()
            >>> print(df.nlargest(5, 'change_pct'))
        """
        cache_key = "industry_board"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 从akshare获取行业板块行情
            df = ak.stock_board_industry_name_em()
            
            # 获取每个行业的详细数据
            result_list = []
            for _, row in df.head(100).iterrows():  # 限制前100个行业
                try:
                    industry_name = row['板块名称']
                    # 获取行业成分股
                    cons_df = ak.stock_board_industry_cons_em(symbol=industry_name)
                    
                    if not cons_df.empty:
                        # 计算行业统计数据
                        up_count = len(cons_df[cons_df['涨跌幅'] > 0])
                        down_count = len(cons_df[cons_df['涨跌幅'] < 0])
                        avg_change = cons_df['涨跌幅'].mean()
                        total_amount = cons_df['成交额'].sum() if '成交额' in cons_df.columns else 0
                        
                        # 领涨股票
                        lead_stock = cons_df.nlargest(1, '涨跌幅')
                        lead_stock_name = lead_stock['股票名称'].values[0] if not lead_stock.empty else ''
                        
                        result_list.append({
                            'name': industry_name,
                            'change_pct': round(avg_change, 2),
                            'up_count': up_count,
                            'down_count': down_count,
                            'lead_stock': lead_stock_name,
                            'total_amount': float(total_amount),
                            'stock_count': len(cons_df)
                        })
                except Exception as inner_e:
                    continue
            
            result_df = pd.DataFrame(result_list)
            self._set_cache(cache_key, result_df)
            return result_df
            
        except Exception as e:
            print(f"获取行业板块失败: {e}")
            return pd.DataFrame()
    
    def get_concept_board(self) -> pd.DataFrame:
        """
        获取概念板块行情
        
        获取各概念板块的实时行情数据。
        
        Returns:
            pd.DataFrame: 概念板块数据
        
        Example:
            >>> df = fetcher.get_concept_board()
            >>> print(df.nlargest(10, 'change_pct'))
        """
        cache_key = "concept_board"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 从akshare获取概念板块行情
            df = ak.stock_board_concept_name_em()
            
            # 获取热门概念的详细数据
            result_list = []
            for _, row in df.head(80).iterrows():  # 限制前80个概念
                try:
                    concept_name = row['板块名称']
                    # 获取概念成分股
                    cons_df = ak.stock_board_concept_cons_em(symbol=concept_name)
                    
                    if not cons_df.empty:
                        # 计算概念统计数据
                        up_count = len(cons_df[cons_df['涨跌幅'] > 0])
                        down_count = len(cons_df[cons_df['涨跌幅'] < 0])
                        avg_change = cons_df['涨跌幅'].mean()
                        total_amount = cons_df['成交额'].sum() if '成交额' in cons_df.columns else 0
                        
                        # 领涨股票
                        lead_stock = cons_df.nlargest(1, '涨跌幅')
                        lead_stock_name = lead_stock['股票名称'].values[0] if not lead_stock.empty else ''
                        
                        result_list.append({
                            'name': concept_name,
                            'change_pct': round(avg_change, 2),
                            'up_count': up_count,
                            'down_count': down_count,
                            'lead_stock': lead_stock_name,
                            'total_amount': float(total_amount),
                            'stock_count': len(cons_df)
                        })
                except Exception:
                    continue
            
            result_df = pd.DataFrame(result_list)
            self._set_cache(cache_key, result_df)
            return result_df
            
        except Exception as e:
            print(f"获取概念板块失败: {e}")
            return pd.DataFrame()
    
    def get_board_overview(self) -> Dict:
        """
        获取板块概览
        
        获取行业和概念板块的综合概览数据，包括涨幅排行、
        资金流向等。
        
        Returns:
            Dict: 板块概览数据：
                - industry_top: 行业涨幅TOP10
                - industry_bottom: 行业跌幅TOP10
                - concept_top: 概念涨幅TOP10
                - concept_bottom: 概念跌幅TOP10
                - hot_industries: 热门行业（成交额TOP）
                - hot_concepts: 热门概念（成交额TOP）
        
        Example:
            >>> overview = fetcher.get_board_overview()
            >>> print(overview['industry_top'])
        """
        cache_key = "board_overview"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 获取行业和概念板块数据
            industry_df = self.get_industry_board()
            concept_df = self.get_concept_board()
            
            result = {
                'industry_top': [],
                'industry_bottom': [],
                'concept_top': [],
                'concept_bottom': [],
                'hot_industries': [],
                'hot_concepts': []
            }
            
            # 行业涨幅榜
            if not industry_df.empty:
                result['industry_top'] = industry_df.nlargest(10, 'change_pct').to_dict('records')
                result['industry_bottom'] = industry_df.nsmallest(10, 'change_pct').to_dict('records')
                result['hot_industries'] = industry_df.nlargest(10, 'total_amount').to_dict('records')
            
            # 概念涨幅榜
            if not concept_df.empty:
                result['concept_top'] = concept_df.nlargest(10, 'change_pct').to_dict('records')
                result['concept_bottom'] = concept_df.nsmallest(10, 'change_pct').to_dict('records')
                result['hot_concepts'] = concept_df.nlargest(10, 'total_amount').to_dict('records')
            
            self._set_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"获取板块概览失败: {e}")
            return {
                'industry_top': [],
                'industry_bottom': [],
                'concept_top': [],
                'concept_bottom': [],
                'hot_industries': [],
                'hot_concepts': []
            }


# ==================== 全局实例 ====================

# 创建全局单例实例，供其他模块导入使用
fetcher = AStockDataFetcher()
