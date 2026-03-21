#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A股即时监视系统 - Flask主应用
========================================

本项目是一个基于Flask的A股实时行情监控系统，提供以下核心功能：
1. 实时行情数据获取与展示
2. 多种智能选股策略
3. 热门股票排行榜
4. 个股详细信息查询

作者: MengqiYe
创建时间: 2024
版本: 1.0.0
"""

import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# 导入自定义模块
from modules.data_fetcher import fetcher    # 数据获取模块
from modules.strategies import engine       # 选股策略引擎模块
from modules.quant_engine import quant_engine  # 量化交易引擎模块


# ==================== Flask应用初始化 ====================

app = Flask(__name__)

# 启用跨域支持，允许前端跨域访问API
CORS(app)

# 应用配置
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON响应
app.config['SECRET_KEY'] = 'a-stock-monitor-secret-key'  # Session密钥


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """
    主页路由
    
    返回前端可视化界面，展示：
    - 实时行情监控面板
    - 选股策略分析
    - 热门股票排行
    - 股票搜索功能
    
    Returns:
        HTML: 渲染后的index.html模板
    """
    return render_template('index.html')


# ==================== 行情数据API ====================

@app.route('/api/realtime', methods=['GET'])
def get_realtime_quotes():
    """
    获取A股实时行情数据
    
    API接口: GET /api/realtime
    
    功能说明:
        获取所有A股股票的实时行情数据，包括：
        - 股票代码、名称
        - 最新价、涨跌幅、涨跌额
        - 成交量、成交额
        - 最高价、最低价、开盘价、昨收价
        - 振幅、换手率
        - 市盈率、市净率
        - 总市值、流通市值
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 股票数据列表
            - count: 股票总数
            - timestamp: 数据时间戳
    
    示例:
        curl http://localhost:5000/api/realtime
    """
    try:
        # 调用数据获取模块获取实时行情
        df = fetcher.get_realtime_quotes()
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': '获取数据失败'
            })
        
        # 将DataFrame转换为字典列表
        data = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/hot', methods=['GET'])
def get_hot_stocks():
    """
    获取热门股票排行榜
    
    API接口: GET /api/hot?top=N
    
    功能说明:
        获取各类热门股票排行榜，包括：
        - gainers: 涨幅榜（涨幅最大的股票）
        - losers: 跌幅榜（跌幅最大的股票）
        - volume_top: 成交额榜（成交额最大的股票）
        - turnover_top: 换手率榜（换手率最高的股票）
    
    Query Parameters:
        top (int, optional): 每个榜单返回的股票数量，默认为10
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 包含四个排行榜的字典
    
    示例:
        curl http://localhost:5000/api/hot?top=5
    """
    try:
        # 获取URL参数，默认返回前10名
        top = request.args.get('top', 10, type=int)
        
        # 调用数据获取模块获取热门股票
        data = fetcher.get_hot_stocks(top=top)
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/stock/<code>', methods=['GET'])
def get_stock_info(code):
    """
    获取个股详细信息
    
    API接口: GET /api/stock/<code>
    
    功能说明:
        获取指定股票代码的详细信息，包括：
        - 实时行情数据
        - 历史K线数据（最近60个交易日）
    
    URL Parameters:
        code (str): 股票代码（如：600519、000001）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 股票详细信息（含历史数据）
    
    示例:
        curl http://localhost:5000/api/stock/600519
    """
    try:
        # 调用数据获取模块获取个股信息
        data = fetcher.get_stock_info(code)
        
        if not data:
            return jsonify({
                'success': False,
                'message': '未找到该股票'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/search', methods=['GET'])
def search_stocks():
    """
    搜索股票
    
    API接口: GET /api/search?keyword=XXX
    
    功能说明:
        根据关键词搜索股票，支持：
        - 按股票代码搜索（模糊匹配）
        - 按股票名称搜索（模糊匹配）
    
    Query Parameters:
        keyword (str): 搜索关键词（股票代码或名称）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 匹配的股票列表
            - count: 匹配数量
    
    示例:
        curl http://localhost:5000/api/search?keyword=茅台
        curl http://localhost:5000/api/search?keyword=600
    """
    try:
        # 获取搜索关键词和结果数量限制
        keyword = request.args.get('keyword', '')
        limit = request.args.get('limit', 50, type=int)
        
        if not keyword:
            return jsonify({
                'success': False,
                'message': '请输入搜索关键词'
            }), 400
        
        # 调用数据获取模块进行搜索
        df = fetcher.search_stocks(keyword, limit=limit)
        data = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 选股策略API ====================

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """
    获取所有可选策略列表
    
    API接口: GET /api/strategies
    
    功能说明:
        获取系统中所有可用的选股策略列表及其描述
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 策略列表，每个策略包含：
                - id: 策略标识
                - name: 策略名称
                - description: 策略描述
    
    示例:
        curl http://localhost:5000/api/strategies
    """
    try:
        strategies = engine.get_all_strategies()
        
        return jsonify({
            'success': True,
            'data': strategies
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/strategy/<strategy_id>', methods=['GET'])
def run_strategy(strategy_id):
    """
    运行指定的选股策略
    
    API接口: GET /api/strategy/<strategy_id>
    
    功能说明:
        运行指定的选股策略，返回符合该策略条件的股票列表
    
    可用策略ID:
        - momentum: 动量策略（选择近期涨幅较大的股票）
        - mean_reversion: 均值回归策略（选择超跌反弹股票）
        - volume_price: 量价策略（选择量价齐升的股票）
        - technical: 技术指标策略（选择估值合理的股票）
        - breakout: 突破策略（选择创阶段新高的股票）
    
    URL Parameters:
        strategy_id (str): 策略标识
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 筛选出的股票列表
            - strategy: 策略ID
            - count: 股票数量
    
    示例:
        curl http://localhost:5000/api/strategy/momentum
    """
    try:
        # 调用策略引擎运行指定策略
        results = engine.run_strategy(strategy_id)
        
        return jsonify({
            'success': True,
            'data': results,
            'strategy': strategy_id,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/strategies/all', methods=['GET'])
def run_all_strategies():
    """
    运行所有选股策略
    
    API接口: GET /api/strategies/all
    
    功能说明:
        一次性运行所有选股策略，返回各策略的筛选结果
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 字典，键为策略ID，值为该策略筛选出的股票列表
    
    示例:
        curl http://localhost:5000/api/strategies/all
    """
    try:
        # 调用策略引擎运行所有策略
        results = engine.run_all_strategies()
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/strategy/<strategy_id>/params', methods=['GET'])
def get_strategy_params(strategy_id):
    """
    获取指定策略的参数配置
    
    API接口: GET /api/strategy/<strategy_id>/params
    
    功能说明:
        获取指定策略当前使用的参数配置
    
    URL Parameters:
        strategy_id (str): 策略标识
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 策略参数字典
    
    示例:
        curl http://localhost:5000/api/strategy/momentum/params
    """
    try:
        params = engine.get_strategy_params(strategy_id)
        
        if not params:
            return jsonify({
                'success': False,
                'message': '策略不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': params
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/strategy/<strategy_id>/params', methods=['POST'])
def update_strategy_params(strategy_id):
    """
    更新指定策略的参数配置
    
    API接口: POST /api/strategy/<strategy_id>/params
    
    功能说明:
        动态更新指定策略的参数配置，用于调整选股条件
    
    URL Parameters:
        strategy_id (str): 策略标识
    
    Request Body (JSON):
        需要更新的参数键值对，例如：
        {
            "min_change_pct": 3.0,
            "top_n": 30
        }
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 操作结果消息
    
    示例:
        curl -X POST -H "Content-Type: application/json" \
             -d '{"min_change_pct": 3.0}' \
             http://localhost:5000/api/strategy/momentum/params
    """
    try:
        # 获取请求体中的新参数
        new_params = request.get_json()
        
        # 调用策略引擎更新参数
        success = engine.update_strategy_params(strategy_id, new_params)
        
        if not success:
            return jsonify({
                'success': False,
                'message': '策略不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '参数更新成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 量化交易API ====================

@app.route('/api/quant/strategies', methods=['GET'])
def get_quant_strategies():
    """
    获取所有可用的量化策略
    
    API接口: GET /api/quant/strategies
    
    功能说明:
        获取所有内置的量化交易策略及其参数配置
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 量化策略列表
    
    示例:
        curl http://localhost:5000/api/quant/strategies
    """
    try:
        strategies = quant_engine.get_available_strategies()
        
        return jsonify({
            'success': True,
            'data': strategies
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/quant/backtest', methods=['POST'])
def run_quant_backtest():
    """
    运行量化策略回测
    
    API接口: POST /api/quant/backtest
    
    功能说明:
        对指定股票运行量化策略回测，返回回测结果
    
    Request Body (JSON):
        {
            "code": "600519",           // 股票代码
            "strategy_id": "sma",       // 策略ID
            "start_date": "2023-01-01", // 开始日期（可选）
            "end_date": "2023-12-31",   // 结束日期（可选）
            "initial_cash": 100000,     // 初始资金（可选）
            "commission_rate": 0.0003,  // 佣金率（可选）
            "strategy_params": {        // 策略参数（可选）
                "fast_period": 5,
                "slow_period": 20
            }
        }
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 回测结果，包含指标、资金曲线、交易记录
    
    示例:
        curl -X POST -H "Content-Type: application/json" \\
             -d '{"code":"600519","strategy_id":"sma"}' \\
             http://localhost:5000/api/quant/backtest
    """
    try:
        # 获取请求参数
        params = request.get_json()
        
        code = params.get('code')
        strategy_id = params.get('strategy_id')
        
        if not code or not strategy_id:
            return jsonify({
                'success': False,
                'message': '请提供股票代码和策略ID'
            }), 400
        
        # 获取股票历史数据
        history = fetcher.get_stock_history(code, days=250)
        
        if history.empty:
            return jsonify({
                'success': False,
                'message': '无法获取股票历史数据'
            }), 404
        
        # 运行回测
        result = quant_engine.run_backtest(
            data=history,
            strategy_id=strategy_id,
            symbol=code,
            initial_cash=params.get('initial_cash', 100000.0),
            commission_rate=params.get('commission_rate', 0.0003),
            stamp_tax_rate=params.get('stamp_tax_rate', 0.001),
            strategy_params=params.get('strategy_params'),
            start_time=params.get('start_date'),
            end_time=params.get('end_date')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/quant/indicators', methods=['POST'])
def calculate_quant_indicators():
    """
    计算技术指标
    
    API接口: POST /api/quant/indicators
    
    功能说明:
        对指定股票计算技术指标
    
    Request Body (JSON):
        {
            "code": "600519",                    // 股票代码
            "indicators": ["sma", "rsi", "macd"], // 要计算的指标
            "params": {                          // 指标参数（可选）
                "sma_period": 20,
                "rsi_period": 14
            }
        }
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 包含技术指标的数据
    
    示例:
        curl -X POST -H "Content-Type: application/json" \\
             -d '{"code":"600519","indicators":["sma","rsi"]}' \\
             http://localhost:5000/api/quant/indicators
    """
    try:
        # 获取请求参数
        params = request.get_json()
        
        code = params.get('code')
        indicators = params.get('indicators', [])
        
        if not code:
            return jsonify({
                'success': False,
                'message': '请提供股票代码'
            }), 400
        
        if not indicators:
            return jsonify({
                'success': False,
                'message': '请提供要计算的指标列表'
            }), 400
        
        # 获取股票历史数据
        history = fetcher.get_stock_history(code, days=120)
        
        if history.empty:
            return jsonify({
                'success': False,
                'message': '无法获取股票历史数据'
            }), 404
        
        # 计算指标
        result_df = quant_engine.calculate_indicators(
            data=history,
            indicators=indicators,
            params=params.get('params')
        )
        
        # 转换为字典列表（处理NaN值）
        result_data = result_df.where(pd.notnull(result_df), None).to_dict('records')
        
        return jsonify({
            'success': True,
            'data': result_data,
            'count': len(result_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/quant/backtest/compare', methods=['POST'])
def compare_quant_strategies():
    """
    比较多个量化策略的回测结果
    
    API接口: POST /api/quant/backtest/compare
    
    功能说明:
        对同一只股票运行多个策略，比较回测结果
    
    Request Body (JSON):
        {
            "code": "600519",
            "strategies": ["sma", "macd", "rsi"],
            "initial_cash": 100000
        }
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 各策略的回测结果对比
    
    示例:
        curl -X POST -H "Content-Type: application/json" \\
             -d '{"code":"600519","strategies":["sma","macd"]}' \\
             http://localhost:5000/api/quant/backtest/compare
    """
    try:
        params = request.get_json()
        
        code = params.get('code')
        strategies = params.get('strategies', [])
        
        if not code or not strategies:
            return jsonify({
                'success': False,
                'message': '请提供股票代码和策略列表'
            }), 400
        
        # 获取股票历史数据
        history = fetcher.get_stock_history(code, days=250)
        
        if history.empty:
            return jsonify({
                'success': False,
                'message': '无法获取股票历史数据'
            }), 404
        
        # 运行多个策略回测
        results = {}
        for strategy_id in strategies:
            try:
                result = quant_engine.run_backtest(
                    data=history,
                    strategy_id=strategy_id,
                    symbol=code,
                    initial_cash=params.get('initial_cash', 100000.0)
                )
                results[strategy_id] = result
            except Exception as e:
                results[strategy_id] = {
                    'success': False,
                    'message': str(e)
                }
        
        # 汇总对比数据
        comparison = []
        for strategy_id, result in results.items():
            if result.get('success'):
                metrics = result.get('metrics', {})
                comparison.append({
                    'strategy_id': strategy_id,
                    'total_return': metrics.get('total_return', 0),
                    'max_drawdown': metrics.get('max_drawdown', 0),
                    'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'total_trades': metrics.get('total_trades', 0)
                })
        
        # 按收益率排序
        comparison.sort(key=lambda x: x['total_return'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'code': code,
                'comparison': comparison,
                'details': results
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 市场全景与板块监控API ====================

@app.route('/api/market/statistics', methods=['GET'])
def get_market_statistics():
    """
    获取市场全景统计
    
    API接口: GET /api/market/statistics
    
    功能说明:
        获取A股市场整体统计数据，包括：
        - 涨跌分布（上涨/下跌/平盘数量）
        - 涨跌停统计
        - 平均涨跌幅
        - 总成交额/成交量
        - 市场情绪指标
        - 各市场（沪市/深市/创业板/科创板/北交所）统计
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 市场统计数据
    
    示例:
        curl http://localhost:5000/api/market/statistics
    """
    try:
        data = fetcher.get_market_statistics()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '获取市场统计失败'
            }), 500
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/market/classify', methods=['GET'])
def get_market_classify():
    """
    获取市场分类数据
    
    API接口: GET /api/market/classify
    
    功能说明:
        按交易所分类获取股票数据：
        - sh_main: 沪市主板
        - sz_main: 深市主板
        - gem: 创业板
        - star: 科创板
        - bse: 北交所
    
    Query Parameters:
        market (str, optional): 指定市场类型，不传则返回所有市场
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 各市场股票数据
    
    示例:
        curl http://localhost:5000/api/market/classify
        curl http://localhost:5000/api/market/classify?market=gem
    """
    try:
        markets = fetcher.classify_stocks_by_market()
        
        # 获取请求参数
        market = request.args.get('market')
        
        if market and market in markets:
            # 返回指定市场的数据
            df = markets[market]
            data = df.to_dict('records') if not df.empty else []
            return jsonify({
                'success': True,
                'data': data,
                'market': market,
                'count': len(data)
            })
        else:
            # 返回所有市场的统计信息
            result = {}
            for market_name, market_df in markets.items():
                result[market_name] = {
                    'count': len(market_df),
                    'up_count': len(market_df[market_df['change_pct'] > 0]) if not market_df.empty else 0,
                    'down_count': len(market_df[market_df['change_pct'] < 0]) if not market_df.empty else 0,
                    'avg_change': round(market_df['change_pct'].mean(), 2) if not market_df.empty else 0,
                    'top_gainers': market_df.nlargest(5, 'change_pct').to_dict('records') if not market_df.empty else []
                }
            
            return jsonify({
                'success': True,
                'data': result
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/board/industry', methods=['GET'])
def get_industry_board():
    """
    获取行业板块行情
    
    API接口: GET /api/board/industry
    
    功能说明:
        获取各行业板块的实时行情数据
    
    Query Parameters:
        top (int, optional): 返回的行业数量，默认为20
        sort (str, optional): 排序方式，'change'按涨跌幅，'amount'按成交额
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 行业板块数据列表
    
    示例:
        curl http://localhost:5000/api/board/industry
        curl http://localhost:5000/api/board/industry?top=10&sort=change
    """
    try:
        df = fetcher.get_industry_board()
        
        if df.empty:
            return jsonify({
                'success': True,
                'data': [],
                'message': '暂无行业板块数据'
            })
        
        # 获取排序参数
        top = request.args.get('top', 20, type=int)
        sort = request.args.get('sort', 'change')
        
        # 排序
        if sort == 'amount':
            df = df.sort_values('total_amount', ascending=False)
        else:
            df = df.sort_values('change_pct', ascending=False)
        
        # 取前N个
        data = df.head(top).to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/board/concept', methods=['GET'])
def get_concept_board():
    """
    获取概念板块行情
    
    API接口: GET /api/board/concept
    
    功能说明:
        获取各概念板块的实时行情数据
    
    Query Parameters:
        top (int, optional): 返回的概念数量，默认为20
        sort (str, optional): 排序方式，'change'按涨跌幅，'amount'按成交额
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 概念板块数据列表
    
    示例:
        curl http://localhost:5000/api/board/concept
        curl http://localhost:5000/api/board/concept?top=15&sort=amount
    """
    try:
        df = fetcher.get_concept_board()
        
        if df.empty:
            return jsonify({
                'success': True,
                'data': [],
                'message': '暂无概念板块数据'
            })
        
        # 获取排序参数
        top = request.args.get('top', 20, type=int)
        sort = request.args.get('sort', 'change')
        
        # 排序
        if sort == 'amount':
            df = df.sort_values('total_amount', ascending=False)
        else:
            df = df.sort_values('change_pct', ascending=False)
        
        # 取前N个
        data = df.head(top).to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/board/overview', methods=['GET'])
def get_board_overview():
    """
    获取板块概览
    
    API接口: GET /api/board/overview
    
    功能说明:
        获取行业和概念板块的综合概览，包括：
        - 行业涨幅/跌幅TOP10
        - 概念涨幅/跌幅TOP10
        - 热门行业/概念（按成交额）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 板块概览数据
    
    示例:
        curl http://localhost:5000/api/board/overview
    """
    try:
        data = fetcher.get_board_overview()
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    """
    404错误处理器
    
    当请求的资源不存在时，返回统一的JSON格式错误响应
    """
    return jsonify({
        'success': False,
        'message': '资源未找到'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """
    500错误处理器
    
    当服务器内部发生错误时，返回统一的JSON格式错误响应
    """
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


# ==================== 应用启动入口 ====================

if __name__ == '__main__':
    # 从环境变量获取端口号，默认为5000
    # 这允许在不同环境中灵活配置端口
    port = int(os.environ.get('DEPLOY_RUN_PORT', 5000))
    
    # 打印启动信息
    print(f"""
    ╔════════════════════════════════════════════╗
    ║      A股即时监视系统                       ║
    ║      A-Stock Monitor System                ║
    ╚════════════════════════════════════════════╝
    
    🚀 服务已启动: http://localhost:{port}
    
    📊 功能列表:
       - 实时行情监控 (GET /api/realtime)
       - 多种选股策略 (GET /api/strategy/<id>)
       - 热门股票排行 (GET /api/hot)
       - 个股详细信息 (GET /api/stock/<code>)
       - 股票搜索功能 (GET /api/search?keyword=xxx)
    
    📖 API文档: 参见项目根目录 API.md 文件
    
    按 Ctrl+C 停止服务
    """)
    
    # 启动Flask应用
    # host='0.0.0.0': 监听所有网络接口，允许外部访问
    # port: 监听端口
    # debug=True: 开启调试模式，代码修改后自动重启
    # threaded=True: 启用多线程处理并发请求
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )
