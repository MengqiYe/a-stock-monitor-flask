"""
A股数据获取模块
使用akshare获取实时股票数据
"""
import akshare as ak
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time


class AStockDataFetcher:
    """A股数据获取器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 60  # 缓存60秒
    
    def _get_cached_data(self, key: str):
        """获取缓存数据"""
        if key in self.cache and key in self.cache_time:
            if time.time() - self.cache_time[key] < self.cache_duration:
                return self.cache[key]
        return None
    
    def _set_cache(self, key: str, data):
        """设置缓存"""
        self.cache[key] = data
        self.cache_time[key] = time.time()
    
    def _get_mock_data(self) -> pd.DataFrame:
        """生成模拟数据用于演示"""
        import random
        import numpy as np
        
        # 模拟一些常见A股
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
            pre_close = random.uniform(10, 500)
            change_pct = random.uniform(-9.9, 9.9)
            price = pre_close * (1 + change_pct / 100)
            
            data.append({
                'code': stock['code'],
                'name': stock['name'],
                'price': round(price, 2),
                'change_pct': round(change_pct, 2),
                'change': round(price - pre_close, 2),
                'volume': random.randint(1000000, 100000000),
                'amount': random.randint(10000000, 1000000000),
                'amplitude': round(random.uniform(2, 15), 2),
                'high': round(price * (1 + random.uniform(0, 0.05)), 2),
                'low': round(price * (1 - random.uniform(0, 0.05)), 2),
                'open': round(price * (1 + random.uniform(-0.02, 0.02)), 2),
                'pre_close': round(pre_close, 2),
                'turnover_rate': round(random.uniform(0.5, 10), 2),
                'pe_ratio': round(random.uniform(5, 50), 2),
                'pb_ratio': round(random.uniform(0.5, 10), 2),
                'total_mv': random.randint(1000000000, 10000000000000),
                'circ_mv': random.randint(500000000, 8000000000000)
            })
        
        return pd.DataFrame(data)
    
    def get_realtime_quotes(self) -> pd.DataFrame:
        """获取A股实时行情数据"""
        cache_key = "realtime_quotes"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 尝试获取A股实时行情数据
            df = ak.stock_zh_a_spot_em()
            
            # 数据清洗和标准化
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
            
            # 处理百分比字符串
            if 'change_pct' in df.columns:
                df['change_pct'] = df['change_pct'].astype(str).str.replace('%', '').astype(float)
            
            self._set_cache(cache_key, df)
            return df
            
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            print("使用模拟数据进行演示...")
            # 使用模拟数据作为备用方案
            mock_df = self._get_mock_data()
            self._set_cache(cache_key, mock_df)
            return mock_df
    
    def get_stock_history(self, code: str, days: int = 60) -> pd.DataFrame:
        """获取股票历史数据"""
        cache_key = f"history_{code}_{days}"
        cached = self._get_cached_data(cache_key)
        if cached is not None:
            return cached
        
        try:
            # 计算日期范围
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                   start_date=start_date, end_date=end_date, 
                                   adjust="qfq")
            
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
                
                # 只取最近days天
                df = df.tail(days)
                
            self._set_cache(cache_key, df)
            return df
            
        except Exception as e:
            print(f"获取股票{code}历史数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_info(self, code: str) -> Dict:
        """获取个股详细信息"""
        try:
            # 获取实时行情
            realtime_df = self.get_realtime_quotes()
            stock_data = realtime_df[realtime_df['code'] == code]
            
            if stock_data.empty:
                return {}
            
            # 转换为字典
            info = stock_data.iloc[0].to_dict()
            
            # 获取历史数据用于计算技术指标
            history = self.get_stock_history(code, days=60)
            if not history.empty:
                info['history'] = history.to_dict('records')
            
            return info
            
        except Exception as e:
            print(f"获取股票{code}信息失败: {e}")
            return {}
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """搜索股票"""
        try:
            df = self.get_realtime_quotes()
            
            # 按代码或名称搜索
            mask = (df['code'].str.contains(keyword, case=False, na=False) |
                   df['name'].str.contains(keyword, case=False, na=False))
            
            return df[mask]
            
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return pd.DataFrame()
    
    def get_hot_stocks(self, top: int = 10) -> Dict:
        """获取热门股票（按涨幅、成交量等排序）"""
        try:
            df = self.get_realtime_quotes()
            
            # 涨幅榜
            gainers = df.nlargest(top, 'change_pct')
            
            # 跌幅榜
            losers = df.nsmallest(top, 'change_pct')
            
            # 成交额榜
            volume_top = df.nlargest(top, 'amount')
            
            # 换手率榜
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


# 全局实例
fetcher = AStockDataFetcher()
