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
import threading
import time
import pandas as pd
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# 导入自定义模块
from modules.data_fetcher import fetcher    # 数据获取模块
from modules.strategies import engine       # 选股策略引擎模块
from modules.quant_engine import quant_engine  # 量化交易引擎模块
from modules.stock_list import MAIN_INDICES, get_index_info, get_index_components  # 指数数据
from modules.full_stock_list import stock_list_manager, MARKET_CATEGORIES, INDUSTRY_CATEGORIES  # 完整股票列表
from modules.watchlist import watchlist_manager  # 自选股票管理
from modules.futures import futures_fetcher, EXCHANGE_INFO, PRODUCT_CATEGORIES  # 期货市场数据


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


# ==================== 自选股票API ====================

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """
    获取自选股票列表
    
    API接口: GET /api/watchlist?group_id=xxx
    
    Args:
        - group_id: 分组ID（可选，指定则只返回该分组股票）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 自选股票列表（包含实时行情）
            - count: 自选股票数量
            - groups: 分组统计信息
    """
    try:
        # 获取分组ID参数
        group_id = request.args.get('group_id', None)
        
        # 获取自选股票列表
        watchlist = watchlist_manager.get_all(group_id)
        groups_stats = watchlist_manager.get_group_stats()
        
        if not watchlist:
            return jsonify({
                'success': True,
                'data': [],
                'count': 0,
                'groups': groups_stats,
                'message': '暂无自选股票'
            })
        
        # 获取实时行情数据
        codes = [s['code'] for s in watchlist]
        realtime_df = fetcher.get_realtime_quotes()
        
        # 合并数据
        result_stocks = []
        for stock in watchlist:
            code = stock['code']
            stock_data = {
                'code': code,
                'name': stock.get('name', ''),
                'shares': stock.get('shares', 0),
                'cost_price': stock.get('cost_price', 0),
                'note': stock.get('note', ''),
                'group_id': stock.get('group_id', 'default'),
                'added_at': stock.get('added_at', '')
            }
            
            # 如果有实时行情，添加行情数据
            if not realtime_df.empty and code in realtime_df['code'].values:
                row = realtime_df[realtime_df['code'] == code].iloc[0]
                
                # 安全获取数值
                def safe_float(val, default=0):
                    try:
                        return float(val) if val is not None and str(val) != '-' and str(val) != 'nan' else default
                    except:
                        return default
                
                def safe_str(val, default='-'):
                    try:
                        return str(val) if val is not None and str(val) != 'nan' else default
                    except:
                        return default
                
                current_price = safe_float(row.get('price', 0), 0)
                cost_price = stock.get('cost_price', 0)
                
                stock_data.update({
                    'name': safe_str(row.get('name', stock_data['name']), stock_data['name']),
                    'current_price': current_price,
                    'change_pct': safe_float(row.get('change_pct', 0), 0),
                    'change_amount': safe_float(row.get('change', 0), 0),
                    'volume': safe_str(row.get('volume', '-'), '-'),
                    'amount': safe_str(row.get('amount', '-'), '-'),
                    'high': safe_float(row.get('high', 0), 0),
                    'low': safe_float(row.get('low', 0), 0),
                    'open': safe_float(row.get('open', 0), 0),
                    'prev_close': safe_float(row.get('pre_close', 0), 0),
                    'market_value': safe_str(row.get('total_mv', '-'), '-'),
                    'pe': safe_str(row.get('pe_ratio', '-'), '-'),
                    'pb': safe_str(row.get('pb_ratio', '-'), '-')
                })
                
                # 计算盈亏
                if cost_price > 0 and current_price > 0:
                    profit_pct = round((current_price - cost_price) / cost_price * 100, 2)
                    profit_amount = round((current_price - cost_price) * stock.get('shares', 0), 2)
                    stock_data['profit_pct'] = profit_pct
                    stock_data['profit_amount'] = profit_amount
                else:
                    stock_data['profit_pct'] = 0
                    stock_data['profit_amount'] = 0
            else:
                # 无实时数据
                stock_data.update({
                    'current_price': '-',
                    'change_pct': '-',
                    'profit_pct': '-',
                    'profit_amount': '-'
                })
            
            result_stocks.append(stock_data)
        
        return jsonify({
            'success': True,
            'data': result_stocks,
            'count': len(result_stocks),
            'groups': groups_stats,
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """
    添加股票到自选
    
    API接口: POST /api/watchlist/add
    
    Request Body:
        - code: 股票代码（必填）
        - name: 股票名称（可选，自动获取）
        - shares: 持仓股数（可选，默认100）
        - cost_price: 成本价（可选，自动获取当前价）
        - note: 备注（可选）
        - group_id: 分组ID（可选，默认default）
        - auto_fill: 是否自动填充（默认True，自动获取当前价作为成本价）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json() or {}
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({
                'success': False,
                'message': '股票代码不能为空'
            }), 400
        
        # 获取股票名称（如果未提供）
        name = data.get('name', '')
        if not name:
            # 尝试从股票列表获取名称
            stock_info = stock_list_manager.get_stock_by_code(code)
            if stock_info:
                name = stock_info.get('name', '')
        
        # 是否自动填充
        auto_fill = data.get('auto_fill', True)
        
        # 分组ID
        group_id = data.get('group_id', 'default')
        
        # 默认持仓和成本价
        shares = int(data.get('shares', 0)) if data.get('shares') is not None else 0
        cost_price = float(data.get('cost_price', 0)) if data.get('cost_price') is not None else 0
        
        # 自动获取当前价格作为成本价
        if auto_fill and cost_price == 0:
            try:
                realtime_df = fetcher.get_realtime_quotes()
                if not realtime_df.empty and code in realtime_df['code'].values:
                    row = realtime_df[realtime_df['code'] == code].iloc[0]
                    current_price = row.get('price', 0)
                    if current_price and str(current_price) not in ['-', 'nan', '']:
                        cost_price = float(current_price)
                        # 如果名称也为空，顺便更新
                        if not name:
                            name = str(row.get('name', name))
            except Exception as e:
                print(f"获取实时价格失败: {e}")
        
        # 默认持仓100股
        if shares == 0:
            shares = 100
        
        result = watchlist_manager.add(
            code=code,
            name=name,
            shares=shares,
            cost_price=cost_price,
            note=data.get('note', ''),
            group_id=group_id
        )
        
        # 返回自动填充的信息
        if result.get('success'):
            result['auto_filled'] = {
                'shares': shares,
                'cost_price': cost_price
            }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """
    从自选中移除股票
    
    API接口: POST /api/watchlist/remove
    
    Request Body:
        - code: 股票代码（必填）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({
                'success': False,
                'message': '股票代码不能为空'
            }), 400
        
        result = watchlist_manager.remove(code)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/watchlist/update', methods=['POST'])
def update_watchlist():
    """
    更新自选股票信息
    
    API接口: POST /api/watchlist/update
    
    Request Body:
        - code: 股票代码（必填）
        - shares: 持仓股数（可选）
        - cost_price: 成本价（可选）
        - note: 备注（可选）
        - group_id: 分组ID（可选）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({
                'success': False,
                'message': '股票代码不能为空'
            }), 400
        
        result = watchlist_manager.update(
            code=code,
            shares=data.get('shares'),
            cost_price=data.get('cost_price'),
            note=data.get('note'),
            group_id=data.get('group_id')
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/watchlist/clear', methods=['POST'])
def clear_watchlist():
    """
    清空自选股票
    
    API接口: POST /api/watchlist/clear
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        result = watchlist_manager.clear()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/watchlist/count', methods=['GET'])
def get_watchlist_count():
    """
    获取自选股票数量
    
    API接口: GET /api/watchlist/count
    
    Returns:
        JSON响应:
            - success: 是否成功
            - count: 自选股票数量
    """
    try:
        count = watchlist_manager.get_count()
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 分组管理API ====================

@app.route('/api/groups', methods=['GET'])
def get_groups():
    """
    获取所有分组
    
    API接口: GET /api/groups
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 分组列表
    """
    try:
        groups = watchlist_manager.get_groups()
        stats = watchlist_manager.get_group_stats()
        
        # 添加统计信息
        result = []
        for group in groups:
            group_data = group.copy()
            group_data['count'] = stats.get(group['id'], {}).get('count', 0)
            result.append(group_data)
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/groups/add', methods=['POST'])
def add_group():
    """
    添加分组
    
    API接口: POST /api/groups/add
    
    Request Body:
        - name: 分组名称（必填）
        - color: 分组颜色（可选，默认#1890ff）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        color = data.get('color', '#1890ff')
        
        if not name:
            return jsonify({
                'success': False,
                'message': '分组名称不能为空'
            }), 400
        
        result = watchlist_manager.add_group(name, color)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/groups/update', methods=['POST'])
def update_group():
    """
    更新分组
    
    API接口: POST /api/groups/update
    
    Request Body:
        - id: 分组ID（必填）
        - name: 分组名称（可选）
        - color: 分组颜色（可选）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json() or {}
        group_id = data.get('id', '').strip()
        
        if not group_id:
            return jsonify({
                'success': False,
                'message': '分组ID不能为空'
            }), 400
        
        result = watchlist_manager.update_group(
            group_id=group_id,
            name=data.get('name'),
            color=data.get('color')
        )
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/groups/delete', methods=['POST'])
def delete_group():
    """
    删除分组
    
    API接口: POST /api/groups/delete
    
    Request Body:
        - id: 分组ID（必填）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json() or {}
        group_id = data.get('id', '').strip()
        
        if not group_id:
            return jsonify({
                'success': False,
                'message': '分组ID不能为空'
            }), 400
        
        result = watchlist_manager.delete_group(group_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/watchlist/move', methods=['POST'])
def move_stocks_to_group():
    """
    移动股票到指定分组
    
    API接口: POST /api/watchlist/move
    
    Request Body:
        - codes: 股票代码列表（必填）
        - group_id: 目标分组ID（必填）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - message: 提示信息
    """
    try:
        data = request.get_json() or {}
        codes = data.get('codes', [])
        group_id = data.get('group_id', '')
        
        if not codes:
            return jsonify({
                'success': False,
                'message': '请选择要移动的股票'
            }), 400
        
        if not group_id:
            return jsonify({
                'success': False,
                'message': '请选择目标分组'
            }), 400
        
        result = watchlist_manager.move_to_group(codes, group_id)
        return jsonify(result)
        
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


# ==================== 指数和港股API ====================

@app.route('/api/indices', methods=['GET'])
def get_indices():
    """
    获取主要指数数据
    
    API接口: GET /api/indices
    
    功能说明:
        获取A股主要指数的实时数据，包括：
        - 上证指数
        - 深证成指
        - 创业板指
        - 上证50
        - 沪深300
        - 中证500
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 指数数据列表
    """
    try:
        df = fetcher._get_mock_indices()
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


@app.route('/api/hk/stocks', methods=['GET'])
def get_hk_stocks():
    """
    获取港股实时行情数据
    
    API接口: GET /api/hk/stocks
    
    功能说明:
        获取港股主要股票的实时行情数据
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 港股数据列表
            - count: 股票总数
    """
    try:
        df = fetcher._get_mock_hk_stocks()
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


@app.route('/api/hk/indices', methods=['GET'])
def get_hk_indices():
    """
    获取港股指数数据
    
    API接口: GET /api/hk/indices
    
    功能说明:
        获取港股主要指数的实时数据，包括：
        - 恒生指数
        - 恒生国企指数
        - 恒生科技指数
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 港股指数数据列表
    """
    try:
        df = fetcher._get_mock_hk_indices()
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


@app.route('/api/index/<index_code>', methods=['GET'])
def get_index_detail(index_code):
    """
    获取指数详细信息及成分股
    
    API接口: GET /api/index/<index_code>
    
    功能说明:
        获取指定指数的详细信息和成分股列表
    
    URL Parameters:
        index_code (str): 指数代码（如：000016-上证50, 000905-中证500）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 指数信息及成分股列表
    """
    try:
        # 获取指数信息
        index_info = get_index_info(index_code)
        
        if not index_info:
            return jsonify({
                'success': False,
                'message': '未找到该指数'
            }), 404
        
        # 获取成分股的实时行情
        components = index_info['components']
        component_codes = [s['code'] for s in components]
        
        # 获取实时行情数据
        df = fetcher.get_realtime_quotes()
        
        # 筛选出成分股的行情
        component_quotes = []
        for _, row in df.iterrows():
            if row['code'] in component_codes:
                quote = row.to_dict()
                # 匹配股票名称
                for c in components:
                    if c['code'] == row['code']:
                        quote['name'] = c['name']
                        break
                component_quotes.append(quote)
        
        # 获取指数当前价格（模拟）
        import random
        for idx in MAIN_INDICES:
            if idx['code'] == index_code:
                pre_close = random.uniform(1000, 15000)
                change_pct = random.uniform(-3, 3)
                price = pre_close * (1 + change_pct / 100)
                index_info['price'] = round(price, 2)
                index_info['change_pct'] = round(change_pct, 2)
                index_info['change'] = round(price - pre_close, 2)
                break
        
        return jsonify({
            'success': True,
            'data': {
                'index': index_info,
                'components': component_quotes,
                'component_count': len(component_quotes)
            },
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 完整股票列表API ====================

@app.route('/api/stocks/all', methods=['GET'])
def get_all_stocks_list():
    """
    获取所有A股股票列表
    
    API接口: GET /api/stocks/all
    
    Query Parameters:
        page (int): 页码，默认1
        size (int): 每页数量，默认100，最大500
        market (str): 市场筛选（sh_main, sh_star, sz_main, sz_sme, sz_chinext）
        industry (str): 行业筛选
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 股票列表
            - pagination: 分页信息
    """
    try:
        page = request.args.get('page', 1, type=int)
        size = min(request.args.get('size', 100, type=int), 500)
        market_filter = request.args.get('market', '')
        industry_filter = request.args.get('industry', '')
        
        # 获取完整股票列表
        df = stock_list_manager.get_all_stocks()
        
        # 应用筛选
        if market_filter:
            df = df[df['market'] == market_filter]
        if industry_filter:
            df = df[df['industry'] == industry_filter]
        
        # 计算分页
        total = len(df)
        total_pages = (total + size - 1) // size
        start = (page - 1) * size
        end = start + size
        
        # 获取当前页数据
        page_data = df.iloc[start:end]
        
        # 转换为字典列表
        stocks = page_data.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': stocks,
            'pagination': {
                'page': page,
                'size': size,
                'total': total,
                'total_pages': total_pages
            },
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/stocks/categories', methods=['GET'])
def get_stock_categories():
    """
    获取股票分类信息
    
    API接口: GET /api/stocks/categories
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 包含市场分类和行业分类的统计信息
    """
    try:
        # 获取统计信息
        stats = stock_list_manager.get_market_statistics()
        
        # 构建分类信息
        categories = {
            'markets': [],
            'industries': []
        }
        
        # 市场分类
        for market_code, market_info in MARKET_CATEGORIES.items():
            count = stats['by_market'].get(market_code, {}).get('count', 0)
            categories['markets'].append({
                'code': market_code,
                'name': market_info['name'],
                'count': count
            })
        
        # 行业分类
        for industry, count in stats['by_industry'].items():
            categories['industries'].append({
                'name': industry,
                'count': count
            })
        
        # 按数量排序
        categories['industries'].sort(key=lambda x: x['count'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': categories,
            'total_stocks': stats['total'],
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/stocks/market/<market>', methods=['GET'])
def get_stocks_by_market(market):
    """
    按市场获取股票列表
    
    API接口: GET /api/stocks/market/<market>
    
    URL Parameters:
        market (str): 市场代码（sh_main, sh_star, sz_main, sz_sme, sz_chinext）
    
    Query Parameters:
        page (int): 页码
        size (int): 每页数量
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 股票列表
            - market_name: 市场名称
    """
    try:
        page = request.args.get('page', 1, type=int)
        size = min(request.args.get('size', 100, type=int), 500)
        
        # 验证市场代码
        if market not in MARKET_CATEGORIES:
            return jsonify({
                'success': False,
                'message': f'无效的市场代码: {market}'
            }), 400
        
        market_info = MARKET_CATEGORIES[market]
        
        # 获取股票列表
        df = stock_list_manager.get_stocks_by_market(market)
        
        # 分页
        total = len(df)
        total_pages = (total + size - 1) // size
        start = (page - 1) * size
        end = start + size
        
        page_data = df.iloc[start:end]
        stocks = page_data.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': stocks,
            'market': market,
            'market_name': market_info['name'],
            'pagination': {
                'page': page,
                'size': size,
                'total': total,
                'total_pages': total_pages
            },
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/stocks/industry/<industry>', methods=['GET'])
def get_stocks_by_industry(industry):
    """
    按行业获取股票列表
    
    API接口: GET /api/stocks/industry/<industry>
    
    URL Parameters:
        industry (str): 行业名称
    
    Query Parameters:
        page (int): 页码
        size (int): 每页数量
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 股票列表
    """
    try:
        page = request.args.get('page', 1, type=int)
        size = min(request.args.get('size', 100, type=int), 500)
        
        # 获取股票列表
        df = stock_list_manager.get_stocks_by_industry(industry)
        
        # 分页
        total = len(df)
        total_pages = (total + size - 1) // size
        start = (page - 1) * size
        end = start + size
        
        page_data = df.iloc[start:end]
        stocks = page_data.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': stocks,
            'industry': industry,
            'pagination': {
                'page': page,
                'size': size,
                'total': total,
                'total_pages': total_pages
            },
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/all_markets', methods=['GET'])
def get_all_markets():
    """
    获取所有市场数据（A股、港股、指数）
    
    API接口: GET /api/all_markets
    
    功能说明:
        一次性获取所有市场的行情数据，包括：
        - A股指数（上证、深证、创业板等）
        - A股股票（按市场分类）
        - 港股指数
        - 港股股票
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 包含各市场数据的字典
    """
    try:
        # 获取A股数据
        a_df = fetcher.get_realtime_quotes()
        a_data = a_df.to_dict('records')
        
        # 按市场分类A股
        a_by_market = {
            'sh_main': [],      # 沪市主板
            'sz_main': [],      # 深市主板
            'sme': [],          # 中小板
            'chinext': [],      # 创业板
            'star': [],         # 科创板
        }
        
        for stock in a_data:
            market_name = stock.get('market_name', '')
            if market_name == '沪市':
                a_by_market['sh_main'].append(stock)
            elif market_name == '深市主板':
                a_by_market['sz_main'].append(stock)
            elif market_name == '中小板':
                a_by_market['sme'].append(stock)
            elif market_name == '创业板':
                a_by_market['chinext'].append(stock)
            elif market_name == '科创板':
                a_by_market['star'].append(stock)
            else:
                # 根据代码判断
                code = stock.get('code', '')
                if code.startswith('6'):
                    a_by_market['sh_main'].append(stock)
                elif code.startswith('000') or code.startswith('001'):
                    a_by_market['sz_main'].append(stock)
                elif code.startswith('002'):
                    a_by_market['sme'].append(stock)
                elif code.startswith('300'):
                    a_by_market['chinext'].append(stock)
                elif code.startswith('688'):
                    a_by_market['star'].append(stock)
        
        # 获取指数数据
        indices_df = fetcher._get_mock_indices()
        indices_data = indices_df.to_dict('records')
        
        # 获取港股数据
        hk_df = fetcher._get_mock_hk_stocks()
        hk_data = hk_df.to_dict('records')
        
        # 获取港股指数
        hk_indices_df = fetcher._get_mock_hk_indices()
        hk_indices_data = hk_indices_df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': {
                'a_indices': indices_data,
                'a_stocks': a_by_market,
                'a_stocks_total': len(a_data),
                'hk_indices': hk_indices_data,
                'hk_stocks': hk_data,
                'hk_stocks_total': len(hk_data),
            },
            'timestamp': pd.Timestamp.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== 期货市场API ====================

@app.route('/api/futures/realtime', methods=['GET'])
def get_futures_realtime():
    """
    获取期货实时行情
    
    API接口: GET /api/futures/realtime
    
    Query参数:
        exchange (str, 可选): 交易所代码（shfe/dce/czce/cffex/gfex/ine）
        category (str, 可选): 品种分类（有色金属/贵金属/黑色系等）
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 期货数据列表
            - count: 合约总数
            - timestamp: 数据时间戳
    """
    try:
        exchange = request.args.get('exchange', '')
        category = request.args.get('category', '')
        
        if exchange:
            df = futures_fetcher.get_quotes_by_exchange(exchange)
        elif category:
            df = futures_fetcher.get_quotes_by_category(category)
        else:
            df = futures_fetcher.get_realtime_quotes()
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': '获取期货数据失败'
            })
        
        # 转换数据
        data = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data,
            'count': len(data),
            'timestamp': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/futures/main', methods=['GET'])
def get_futures_main():
    """
    获取主力合约列表
    
    API接口: GET /api/futures/main
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 主力合约列表
            - count: 合约总数
    """
    try:
        df = futures_fetcher.get_main_contracts()
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': '获取主力合约失败'
            })
        
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


@app.route('/api/futures/stats', methods=['GET'])
def get_futures_stats():
    """
    获取期货市场统计
    
    API接口: GET /api/futures/stats
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 市场统计数据
                - total_contracts: 合约总数
                - up_count: 上涨合约数
                - down_count: 下跌合约数
                - flat_count: 平盘合约数
                - limit_up: 涨停数
                - limit_down: 跌停数
                - exchange_stats: 各交易所统计
    """
    try:
        stats = futures_fetcher.get_market_stats()
        exchange_stats = futures_fetcher.get_exchange_stats()
        
        stats['exchange_stats'] = exchange_stats
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/futures/top', methods=['GET'])
def get_futures_top():
    """
    获取期货排行榜
    
    API接口: GET /api/futures/top
    
    Query参数:
        type (str): 排行类型（gainers/losers/volume/position）
        n (int): 返回数量，默认10
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 排行数据
            - type: 排行类型
    """
    try:
        top_type = request.args.get('type', 'gainers')
        n = int(request.args.get('n', 10))
        
        if top_type == 'gainers':
            df = futures_fetcher.get_top_gainers(n)
        elif top_type == 'losers':
            df = futures_fetcher.get_top_losers(n)
        elif top_type == 'volume':
            df = futures_fetcher.get_top_volume(n)
        elif top_type == 'position':
            df = futures_fetcher.get_top_position(n)
        else:
            df = futures_fetcher.get_top_gainers(n)
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': '获取排行数据失败'
            })
        
        data = df.to_dict('records')
        
        return jsonify({
            'success': True,
            'data': data,
            'type': top_type,
            'count': len(data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/futures/exchanges', methods=['GET'])
def get_futures_exchanges():
    """
    获取交易所信息
    
    API接口: GET /api/futures/exchanges
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 交易所信息列表
    """
    try:
        exchanges = []
        for code, info in EXCHANGE_INFO.items():
            exchanges.append({
                'code': code,
                'name': info['name'],
                'short_name': info['short_name'],
                'products': info['products']
            })
        
        return jsonify({
            'success': True,
            'data': exchanges
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/futures/categories', methods=['GET'])
def get_futures_categories():
    """
    获取品种分类信息
    
    API接口: GET /api/futures/categories
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 品种分类信息
    """
    try:
        categories = []
        for name, products in PRODUCT_CATEGORIES.items():
            categories.append({
                'name': name,
                'products': products
            })
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/futures/global', methods=['GET'])
def get_futures_global():
    """
    获取全球期货行情
    
    API接口: GET /api/futures/global
    
    Returns:
        JSON响应:
            - success: 是否成功
            - data: 全球期货数据列表
            - count: 合约总数
    """
    try:
        df = futures_fetcher.get_global_futures()
        
        if df.empty:
            return jsonify({
                'success': False,
                'message': '获取全球期货数据失败'
            })
        
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
    
    # ==================== 缓存预热 ====================
    def warmup_cache():
        """
        后台预热数据缓存
        
        在应用启动后异步加载常用数据到缓存中，
        避免用户第一次访问时等待数据获取
        """
        print("🔄 正在预热数据缓存...")
        try:
            # 预热股票列表缓存
            start = time.time()
            stock_list_manager.get_all_stocks()
            print(f"   ✅ 股票列表缓存预热完成 ({time.time()-start:.2f}s)")
            
            # 预热实时行情缓存
            start = time.time()
            fetcher.get_realtime_quotes()
            print(f"   ✅ 实时行情缓存预热完成 ({time.time()-start:.2f}s)")
            
            # 预热期货数据缓存
            start = time.time()
            futures_fetcher.get_realtime_quotes()
            futures_fetcher.get_main_contracts()
            print(f"   ✅ 期货数据缓存预热完成 ({time.time()-start:.2f}s)")
            
            print("🎉 缓存预热完成！所有数据已就绪")
        except Exception as e:
            print(f"   ⚠️ 缓存预热失败: {e}")
    
    # 在后台线程中预热缓存
    warmup_thread = threading.Thread(target=warmup_cache, daemon=True)
    warmup_thread.start()
    
    # 打印启动信息
    print(f"""
    ╔════════════════════════════════════════════╗
    ║      A股即时监视系统                       ║
    ║      A-Stock Monitor System                ║
    ╚════════════════════════════════════════════╝
    
    🚀 服务已启动: http://localhost:{port}
    
    📊 功能列表:
       - 实时行情监控 (GET /api/realtime)
       - 自选持仓管理 (GET /api/watchlist)
       - 全部股票分类 (GET /api/stocks/categories)
       - 港股市场行情 (GET /api/hk/stocks)
       - 期货市场行情 (GET /api/futures/realtime)
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
