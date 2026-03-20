"""
选股策略引擎
包含多种选股策略：动量策略、均值回归、量价关系、技术指标等
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from modules.data_fetcher import fetcher


class BaseStrategy:
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    def analyze(self, stock_data: pd.DataFrame) -> List[Dict]:
        """分析股票数据，返回符合条件的股票列表"""
        raise NotImplementedError


class MomentumStrategy(BaseStrategy):
    """
    动量策略
    选择近期涨幅较大的股票
    """
    
    def __init__(self):
        super().__init__("动量策略")
        self.params = {
            'min_change_pct': 2.0,  # 最小涨幅%
            'min_volume_ratio': 1.5,  # 最小成交量比
            'top_n': 20  # 返回前N只
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """分析动量股票"""
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        # 筛选条件
        df = realtime_df.copy()
        
        # 1. 涨幅大于阈值
        df = df[df['change_pct'] >= self.params['min_change_pct']]
        
        # 2. 成交量活跃（这里简化处理，使用成交额）
        if 'amount' in df.columns:
            df = df[df['amount'] > df['amount'].median()]
        
        # 3. 排序
        df = df.sort_values('change_pct', ascending=False)
        df = df.head(self.params['top_n'])
        
        # 添加策略标签
        results = df.to_dict('records')
        for stock in results:
            stock['strategy'] = self.name
            stock['reason'] = f"涨幅{stock['change_pct']:.2f}%，动量强劲"
        
        return results


class MeanReversionStrategy(BaseStrategy):
    """
    均值回归策略
    选择超跌反弹股票
    """
    
    def __init__(self):
        super().__init__("均值回归策略")
        self.params = {
            'min_change_pct': -3.0,  # 最大跌幅
            'max_change_pct': -1.0,  # 最小跌幅
            'min_volume': 1000000,  # 最小成交量
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """分析超跌股票"""
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选跌幅在一定范围的股票
        df = df[(df['change_pct'] >= self.params['min_change_pct']) &
                (df['change_pct'] <= self.params['max_change_pct'])]
        
        # 成交量放大（表示有资金关注）
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
    选择量价齐升的股票
    """
    
    def __init__(self):
        super().__init__("量价策略")
        self.params = {
            'min_change_pct': 1.0,  # 最小涨幅
            'min_turnover_rate': 5.0,  # 最小换手率
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """分析量价齐升股票"""
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选涨幅和换手率都较高的股票
        df = df[(df['change_pct'] >= self.params['min_change_pct'])]
        
        if 'turnover_rate' in df.columns:
            df = df[df['turnover_rate'] >= self.params['min_turnover_rate']]
        
        # 按换手率*涨幅排序（综合得分）
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
    技术指标策略
    基于技术指标选股
    """
    
    def __init__(self):
        super().__init__("技术指标策略")
        self.params = {
            'min_pe': 0,  # 最小市盈率
            'max_pe': 50,  # 最大市盈率
            'min_pb': 0.5,  # 最小市净率
            'max_pb': 10,  # 最大市净率
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """分析技术指标"""
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选估值合理的股票
        if 'pe_ratio' in df.columns and 'pb_ratio' in df.columns:
            # 过滤掉异常值
            df = df[(df['pe_ratio'] >= self.params['min_pe']) & 
                    (df['pe_ratio'] <= self.params['max_pe']) &
                    (df['pb_ratio'] >= self.params['min_pb']) & 
                    (df['pb_ratio'] <= self.params['max_pb'])]
            
            # 计算估值得分（越低越好）
            df['score'] = 100 - df['pe_ratio'] - df['pb_ratio'] * 10
            
            # 按得分排序
            df = df.sort_values('score', ascending=False)
            df = df.head(self.params['top_n'])
            
            results = df.to_dict('records')
            for stock in results:
                stock['strategy'] = self.name
                stock['reason'] = f"PE:{stock['pe_ratio']:.2f}，PB:{stock['pb_ratio']:.2f}，估值合理"
        else:
            results = []
        
        return results


class BreakoutStrategy(BaseStrategy):
    """
    突破策略
    选择创阶段新高的股票
    """
    
    def __init__(self):
        super().__init__("突破策略")
        self.params = {
            'min_change_pct': 2.0,  # 最小涨幅
            'min_amplitude': 5.0,  # 最小振幅
            'top_n': 20
        }
    
    def analyze(self, realtime_df: pd.DataFrame = None) -> List[Dict]:
        """分析突破股票"""
        if realtime_df is None:
            realtime_df = fetcher.get_realtime_quotes()
        
        if realtime_df.empty:
            return []
        
        df = realtime_df.copy()
        
        # 筛选涨幅和振幅都较大的股票
        df = df[df['change_pct'] >= self.params['min_change_pct']]
        
        if 'amplitude' in df.columns:
            df = df[df['amplitude'] >= self.params['min_amplitude']]
        
        # 按涨幅*振幅排序
        if 'amplitude' in df.columns:
            df['score'] = df['change_pct'] * df['amplitude']
            df = df.sort_values('score', ascending=False)
        else:
            df = df.sort_values('change_pct', ascending=False)
        
        df = df.head(self.params['top_n'])
        
        results = df.to_dict('records')
        for stock in results:
            stock['strategy'] = self.name
            amplitude_str = f"，振幅{stock.get('amplitude', 0):.2f}%" if 'amplitude' in stock else ""
            stock['reason'] = f"涨幅{stock['change_pct']:.2f}%{amplitude_str}，突破上涨"
        
        return results


class StrategyEngine:
    """策略引擎"""
    
    def __init__(self):
        self.strategies = {
            'momentum': MomentumStrategy(),
            'mean_reversion': MeanReversionStrategy(),
            'volume_price': VolumePriceStrategy(),
            'technical': TechnicalIndicatorStrategy(),
            'breakout': BreakoutStrategy()
        }
    
    def get_all_strategies(self) -> List[Dict]:
        """获取所有策略列表"""
        return [
            {
                'id': key,
                'name': strategy.name,
                'description': self._get_strategy_description(key)
            }
            for key, strategy in self.strategies.items()
        ]
    
    def _get_strategy_description(self, strategy_id: str) -> str:
        """获取策略描述"""
        descriptions = {
            'momentum': '选择近期涨幅较大、动量强劲的股票',
            'mean_reversion': '选择超跌反弹、可能出现均值回归的股票',
            'volume_price': '选择量价齐升、资金活跃的股票',
            'technical': '选择估值合理、基本面良好的股票',
            'breakout': '选择创阶段新高、突破上涨的股票'
        }
        return descriptions.get(strategy_id, '')
    
    def run_strategy(self, strategy_id: str) -> List[Dict]:
        """运行指定策略"""
        if strategy_id not in self.strategies:
            return []
        
        strategy = self.strategies[strategy_id]
        return strategy.analyze()
    
    def run_all_strategies(self) -> Dict[str, List[Dict]]:
        """运行所有策略"""
        results = {}
        for strategy_id, strategy in self.strategies.items():
            try:
                results[strategy_id] = strategy.analyze()
            except Exception as e:
                print(f"策略{strategy_id}执行失败: {e}")
                results[strategy_id] = []
        
        return results
    
    def get_strategy_params(self, strategy_id: str) -> Dict:
        """获取策略参数"""
        if strategy_id not in self.strategies:
            return {}
        
        return self.strategies[strategy_id].params
    
    def update_strategy_params(self, strategy_id: str, params: Dict) -> bool:
        """更新策略参数"""
        if strategy_id not in self.strategies:
            return False
        
        strategy = self.strategies[strategy_id]
        strategy.params.update(params)
        return True


# 全局实例
engine = StrategyEngine()
