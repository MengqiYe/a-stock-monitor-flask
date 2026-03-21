#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股监视系统模块包
========================================

本包包含A股监视系统的核心功能模块：

模块列表:
    - data_fetcher: A股数据获取模块
        - AStockDataFetcher: 数据获取器类
        - fetcher: 全局数据获取器实例
    
    - strategies: 选股策略引擎模块
        - StrategyEngine: 策略引擎类
        - engine: 全局策略引擎实例
        - MomentumStrategy: 动量策略
        - MeanReversionStrategy: 均值回归策略
        - VolumePriceStrategy: 量价策略
        - TechnicalIndicatorStrategy: 技术指标策略
        - BreakoutStrategy: 突破策略

使用示例:
    >>> from modules import fetcher, engine
    >>> 
    >>> # 获取实时行情
    >>> df = fetcher.get_realtime_quotes()
    >>> 
    >>> # 运行选股策略
    >>> results = engine.run_strategy('momentum')

作者: MengqiYe
版本: 1.0.0
"""

from .data_fetcher import fetcher, AStockDataFetcher
from .strategies import (
    engine, 
    StrategyEngine,
    MomentumStrategy,
    MeanReversionStrategy,
    VolumePriceStrategy,
    TechnicalIndicatorStrategy,
    BreakoutStrategy
)
from .quant_engine import quant_engine, QuantBacktestEngine

__all__ = [
    # 数据获取模块
    'fetcher',
    'AStockDataFetcher',
    
    # 选股策略引擎模块
    'engine',
    'StrategyEngine',
    'MomentumStrategy',
    'MeanReversionStrategy',
    'VolumePriceStrategy',
    'TechnicalIndicatorStrategy',
    'BreakoutStrategy',
    
    # 量化交易引擎模块
    'quant_engine',
    'QuantBacktestEngine'
]

__version__ = '1.0.0'
__author__ = 'MengqiYe'
