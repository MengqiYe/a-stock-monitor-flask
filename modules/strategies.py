#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
选股策略引擎模块
========================================

本模块实现了多种量化选股策略，用于从A股市场筛选符合特定条件的股票。

策略列表:
    1. 动量策略 (Momentum Strategy)
       - 筛选近期涨幅较大的股票
       - 适合趋势跟踪型投资者
    
    2. 均值回归策略 (Mean Reversion Strategy)
       - 筛选超跌股票，期待反弹
       - 适合逆向投资型投资者
    
    3. 量价策略 (Volume-Price Strategy)
       - 筛选量价齐升的股票
       - 关注资金流入情况
    
    4. 技术指标策略 (Technical Indicator Strategy)
       - 基于估值指标筛选股票
       - 适合价值投资型投资者
    
    5. 突破策略 (Breakout Strategy)
       - 筛选创阶段新高的股票
       - 适合突破交易型投资者

使用示例:
    >>> from modules.strategies import engine
    >>> # 获取所有策略列表
    >>> strategies = engine.get_all_strategies()
    >>> # 运行动量策略
    >>> results = engine.run_strategy('momentum')
    >>> # 运行所有策略
    >>> all_results = engine.run_all_strategies()

作者: MengqiYe
版本: 1.0.0
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from modules.data_fetcher import fetcher


class BaseStrategy:
    """
    策略基类
    
    所有选股策略的抽象基类，定义了策略的基本接口。
    具体策略需要实现analyze方法。
    
    Attributes:
        name (str): 策略名称
        params (dict): 策略参数配置
    
    Example:
        >>> class MyStrategy(BaseStrategy):
        ...     def analyze(self, stock_data):
        ...         # 实现具体的选股逻辑
        ...         return results
    """
    
    def __init__(self, name: str):
        """
        初始化策略
        
        Args:
            name (str): 策略名称
        """
        self.name = name
    
    def analyze(self, stock_data: pd.DataFrame) -> List[Dict]:
        """
        分析股票数据，返回符合条件的股票列表
        
        Args:
            stock_data (pd.DataFrame): 股票数据DataFrame
        
        Returns:
            List[Dict]: 符合条件的股票列表
        
        Note:
            子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现analyze方法")


class MomentumStrategy(BaseStrategy):
    """
    动量策略
    
    策略说明:
        选择近期涨幅较大的股票，基于"强者恒强"的市场规律。
        动量策略假设过去表现良好的股票在未来一段时间内
        仍将继续保持良好表现。
    
    适用场景:
        - 牛市或震荡向上的市场环境
        - 趋势跟踪型投资者
        - 短线或中线交易
    
    筛选条件:
        - 涨幅大于最小阈值（默认2%）
        - 成交量活跃（成交额高于中位数）
    
    参数配置:
        - min_change_pct: 最小涨幅阈值（默认2.0%）
        - min_volume_ratio: 最小成交量比率（默认1.5）
        - top_n: 返回股票数量（默认20只）
    """
    
    def __init__(self):
        """初始化动量策略"""
        super().__init__("动量策略")
        self.params = {
            'min_change_pct': 2.0,    # 最小涨幅%
            'min_volume_ratio': 1.5,  # 最小成交量比
            'top_n': 20               # 返回前N只
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """
        分析并筛选动量股票
        
        Args:
            realtime_df (pd.DataFrame, optional): 实时行情数据，如不提供则自动获取
        
        Returns:
            List[Dict]: 符合动量条件的股票列表，每个股票包含：
                - 基本行情信息
                - strategy: 策略名称
                - reason: 选入理由
        """
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选条件1: 涨幅大于阈值
        df = df[df['change_pct'] >= self.params['min_change_pct']]
        
        # 筛选条件2: 成交量活跃
        if 'amount' in df.columns:
            df = df[df['amount'] > df['amount'].median()]
        
        # 按涨幅降序排列，取前N只
        df = df.sort_values('change_pct', ascending=False)
        df = df.head(self.params['top_n'])
        
        # 添加策略标签和选入理由
        results = df.to_dict('records')
        for stock in results:
            stock['strategy'] = self.name
            stock['reason'] = f"涨幅{stock['change_pct']:.2f}%，动量强劲"
        
        return results


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略
    
    策略说明:
        选择超跌的股票，期待均值回归带来的反弹。
        该策略基于"物极必反"的投资理念，认为过度下跌
        的股票终将回归其合理价值。
    
    适用场景:
        - 熊市末期或市场恐慌时
        - 逆向投资型投资者
        - 中长线交易
    
    筛选条件:
        - 跌幅在一定范围内（默认-3%到-1%）
        - 成交量放大（表示有资金关注）
    
    参数配置:
        - min_change_pct: 最大跌幅（默认-3.0%）
        - max_change_pct: 最小跌幅（默认-1.0%）
        - min_volume: 最小成交量（默认1000000）
        - top_n: 返回股票数量（默认20只）
    """
    
    def __init__(self):
        """初始化均值回归策略"""
        super().__init__("均值回归策略")
        self.params = {
            'min_change_pct': -3.0,   # 最大跌幅
            'max_change_pct': -1.0,   # 最小跌幅
            'min_volume': 1000000,    # 最小成交量
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """
        分析并筛选超跌股票
        
        Args:
            realtime_df (pd.DataFrame, optional): 实时行情数据
        
        Returns:
            List[Dict]: 符合超跌条件的股票列表
        """
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选跌幅在一定范围的股票（避免极端跌幅）
        df = df[
            (df['change_pct'] >= self.params['min_change_pct']) &
            (df['change_pct'] <= self.params['max_change_pct'])
        ]
        
        # 成交量放大（表示有资金关注，可能反弹）
        if 'volume' in df.columns:
            df = df[df['volume'] >= self.params['min_volume']]
        
        # 按跌幅排序（跌幅越大越靠前）
        df = df.sort_values('change_pct', ascending=True)
        df = df.head(self.params['top_n'])
        
        results = df.to_dict('records')
        for stock in results:
            stock['strategy'] = self.name
            stock['reason'] = f"跌幅{stock['change_pct']:.2f}%，可能出现反弹"
        
        return results


class VolumePriceStrategy(BaseStrategy):
    """
    量价策略
    
    策略说明:
        选择量价齐升的股票，关注资金流入情况。
        "量在价先"，成交量的放大往往预示着股价的上涨。
        该策略寻找成交量和价格同步上涨的股票。
    
    适用场景:
        - 量价分析爱好者
        - 关注资金流向的投资者
        - 短中线交易
    
    筛选条件:
        - 涨幅大于阈值（默认1%）
        - 换手率较高（默认大于5%）
    
    参数配置:
        - min_change_pct: 最小涨幅（默认1.0%）
        - min_turnover_rate: 最小换手率（默认5.0%）
        - top_n: 返回股票数量（默认20只）
    """
    
    def __init__(self):
        """初始化量价策略"""
        super().__init__("量价策略")
        self.params = {
            'min_change_pct': 1.0,      # 最小涨幅
            'min_turnover_rate': 5.0,   # 最小换手率
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """
        分析并筛选量价齐升股票
        
        Args:
            realtime_df (pd.DataFrame, optional): 实时行情数据
        
        Returns:
            List[Dict]: 符合量价条件的股票列表
        """
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选涨幅和换手率都较高的股票
        df = df[df['change_pct'] >= self.params['min_change_pct']]
        
        if 'turnover_rate' in df.columns:
            df = df[df['turnover_rate'] >= self.params['min_turnover_rate']]
        
        # 计算综合得分：涨幅 * 换手率
        df['score'] = df['change_pct'] * df['turnover_rate']
        df = df.sort_values('score', ascending=False)
        df = df.head(self.params['top_n'])
        
        results = df.to_dict('records')
        for stock in results:
            stock['strategy'] = self.name
            stock['reason'] = f"涨幅{stock['change_pct']:.2f}%，换手率{stock['turnover_rate']:.2f}%，量价齐升"
        
        return results


class TechnicalIndicatorStrategy(BaseStrategy):
    """
    技术指标策略（估值策略）
    
    策略说明:
        基于估值指标筛选股票，寻找估值合理的标的。
        主要使用市盈率(PE)和市净率(PB)作为估值指标。
        低估值股票通常具有更高的安全边际。
    
    适用场景:
        - 价值投资型投资者
        - 长线投资
        - 防御型投资
    
    筛选条件:
        - 市盈率在合理区间（默认0-50）
        - 市净率在合理区间（默认0.5-10）
    
    参数配置:
        - min_pe: 最小市盈率（默认0）
        - max_pe: 最大市盈率（默认50）
        - min_pb: 最小市净率（默认0.5）
        - max_pb: 最大市净率（默认10）
        - top_n: 返回股票数量（默认20只）
    """
    
    def __init__(self):
        """初始化技术指标策略"""
        super().__init__("技术指标策略")
        self.params = {
            'min_pe': 0,    # 最小市盈率
            'max_pe': 50,   # 最大市盈率
            'min_pb': 0.5,  # 最小市净率
            'max_pb': 10,   # 最大市净率
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """
        分析并筛选估值合理的股票
        
        Args:
            realtime_df (pd.DataFrame, optional): 实时行情数据
        
        Returns:
            List[Dict]: 符合估值条件的股票列表
        """
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 检查是否包含估值数据
        if 'pe_ratio' not in df.columns or 'pb_ratio' not in df.columns:
            return []
        
        # 过滤掉异常值，筛选估值合理的股票
        df = df[
            (df['pe_ratio'] >= self.params['min_pe']) & 
            (df['pe_ratio'] <= self.params['max_pe']) &
            (df['pb_ratio'] >= self.params['min_pb']) & 
            (df['pb_ratio'] <= self.params['max_pb'])
        ]
        
        # 计算估值得分（越低越好）
        # 得分 = 100 - PE - PB*10
        df['score'] = 100 - df['pe_ratio'] - df['pb_ratio'] * 10
        
        # 按得分排序
        df = df.sort_values('score', ascending=False)
        df = df.head(self.params['top_n'])
        
        results = df.to_dict('records')
        for stock in results:
            stock['strategy'] = self.name
            stock['reason'] = f"PE:{stock['pe_ratio']:.2f}，PB:{stock['pb_ratio']:.2f}，估值合理"
        
        return results


class BreakoutStrategy(BaseStrategy):
    """
    突破策略
    
    策略说明:
        选择创阶段新高的股票，捕捉突破行情。
        当股票突破前期高点时，往往意味着新的上涨空间打开。
        该策略寻找正在突破的强势股票。
    
    适用场景:
        - 趋势跟踪型投资者
        - 短线或波段交易
        - 追涨策略爱好者
    
    筛选条件:
        - 涨幅大于阈值（默认2%）
        - 振幅较大（默认大于5%）
    
    参数配置:
        - min_change_pct: 最小涨幅（默认2.0%）
        - min_amplitude: 最小振幅（默认5.0%）
        - top_n: 返回股票数量（默认20只）
    """
    
    def __init__(self):
        """初始化突破策略"""
        super().__init__("突破策略")
        self.params = {
            'min_change_pct': 2.0,   # 最小涨幅
            'min_amplitude': 5.0,    # 最小振幅
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """
        分析并筛选突破股票
        
        Args:
            realtime_df (pd.DataFrame, optional): 实时行情数据
        
        Returns:
            List[Dict]: 符合突破条件的股票列表
        """
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选涨幅和振幅都较大的股票
        df = df[df['change_pct'] >= self.params['min_change_pct']]
        
        if 'amplitude' in df.columns:
            df = df[df['amplitude'] >= self.params['min_amplitude']]
        
        # 计算综合得分：涨幅 * 振幅
        if 'amplitude' in df.columns:
            df['score'] = df['change_pct'] * df['amplitude']
            df = df.sort_values('score', ascending=False)
        else:
            df = df.sort_values('change_pct', ascending=False)
        
        df = df.head(self.params['top_n'])
        
        results = df.to_dict('records')
        for stock in results:
            amplitude_str = f"，振幅{stock.get('amplitude', 0):.2f}%" if 'amplitude' in stock else ""
            stock['strategy'] = self.name
            stock['reason'] = f"涨幅{stock['change_pct']:.2f}%{amplitude_str}，突破上涨"
        
        return results


class StrategyEngine:
    """
    策略引擎
    
    管理和运行所有选股策略的核心引擎。
    提供策略注册、运行、参数调整等功能。
    
    Attributes:
        strategies (dict): 策略字典，键为策略ID，值为策略实例
    
    Example:
        >>> engine = StrategyEngine()
        >>> # 获取所有策略
        >>> strategies = engine.get_all_strategies()
        >>> # 运行指定策略
        >>> results = engine.run_strategy('momentum')
        >>> # 运行所有策略
        >>> all_results = engine.run_all_strategies()
    """
    
    def __init__(self):
        """
        初始化策略引擎
        
        注册所有可用的选股策略
        """
        self.strategies = {
            'momentum': MomentumStrategy(),           # 动量策略
            'mean_reversion': MeanReversionStrategy(),  # 均值回归策略
            'volume_price': VolumePriceStrategy(),    # 量价策略
            'technical': TechnicalIndicatorStrategy(),  # 技术指标策略
            'breakout': BreakoutStrategy()            # 突破策略
        }
    
    def get_all_strategies(self) -> List[Dict]:
        """
        获取所有可用策略列表
        
        Returns:
            List[Dict]: 策略列表，每个策略包含：
                - id: 策略标识
                - name: 策略名称
                - description: 策略描述
        """
        return [
            {
                'id': key,
                'name': strategy.name,
                'description': self._get_strategy_description(key)
            }
            for key, strategy in self.strategies.items()
        ]
    
    def _get_strategy_description(self, strategy_id: str) -> str:
        """
        获取策略的详细描述
        
        Args:
            strategy_id (str): 策略ID
        
        Returns:
            str: 策略描述文本
        """
        descriptions = {
            'momentum': '选择近期涨幅较大、动量强劲的股票',
            'mean_reversion': '选择超跌反弹、可能出现均值回归的股票',
            'volume_price': '选择量价齐升、资金活跃的股票',
            'technical': '选择估值合理、基本面良好的股票',
            'breakout': '选择创阶段新高、突破上涨的股票'
        }
        return descriptions.get(strategy_id, '')
    
    def run_strategy(self, strategy_id: str) -> List[Dict]:
        """
        运行指定的选股策略
        
        Args:
            strategy_id (str): 策略ID
        
        Returns:
            List[Dict]: 筛选出的股票列表
        
        Raises:
            如果策略不存在，返回空列表
        """
        if strategy_id not in self.strategies:
            return []
        
        strategy = self.strategies[strategy_id]
        return strategy.analyze()
    
    def run_all_strategies(self) -> Dict[str, List[Dict]]:
        """
        运行所有选股策略
        
        Returns:
            Dict[str, List[Dict]]: 各策略的筛选结果
                - 键: 策略ID
                - 值: 股票列表
        """
        results = {}
        for strategy_id, strategy in self.strategies.items():
            try:
                results[strategy_id] = strategy.analyze()
            except Exception as e:
                print(f"策略{strategy_id}执行失败: {e}")
                results[strategy_id] = []
        
        return results
    
    def get_strategy_params(self, strategy_id: str) -> Dict:
        """
        获取指定策略的参数配置
        
        Args:
            strategy_id (str): 策略ID
        
        Returns:
            Dict: 策略参数字典，如果策略不存在返回空字典
        """
        if strategy_id not in self.strategies:
            return {}
        
        return self.strategies[strategy_id].params
    
    def update_strategy_params(self, strategy_id: str, params: Dict) -> bool:
        """
        更新指定策略的参数配置
        
        Args:
            strategy_id (str): 策略ID
            params (Dict): 新的参数配置
        
        Returns:
            bool: 更新是否成功
        """
        if strategy_id not in self.strategies:
            return False
        
        strategy = self.strategies[strategy_id]
        strategy.params.update(params)
        return True


# ==================== 全局实例 ====================

# 创建全局策略引擎实例，供其他模块导入使用
engine = StrategyEngine()
