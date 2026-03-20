"""
A股即时监视系统 - Flask主应用
提供实时行情监控和多种选股策略
"""
import os
import pandas as pd
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from modules.data_fetcher import fetcher
from modules.strategies import engine


app = Flask(__name__)
CORS(app)

# 配置
app.config['JSON_AS_ASCII'] = False  # 支持中文JSON
app.config['SECRET_KEY'] = 'a-stock-monitor-secret-key'


# ==================== 页面路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


# ==================== API接口 ====================

@app.route('/api/realtime', methods=['GET'])
def get_realtime_quotes():
    """获取实时行情"""
    try:
        df = fetcher.get_realtime_quotes()
        if df.empty:
            return jsonify({
                'success': False,
                'message': '获取数据失败'
            })
        
        # 转换为列表
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
    """获取热门股票"""
    try:
        top = request.args.get('top', 10, type=int)
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
    """获取个股信息"""
    try:
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
    """搜索股票"""
    try:
        keyword = request.args.get('keyword', '')
        if not keyword:
            return jsonify({
                'success': False,
                'message': '请输入搜索关键词'
            }), 400
        
        df = fetcher.search_stocks(keyword)
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


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """获取所有策略列表"""
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
    """运行指定策略"""
    try:
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
    """运行所有策略"""
    try:
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
    """获取策略参数"""
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
    """更新策略参数"""
    try:
        new_params = request.get_json()
        
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


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': '资源未找到'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': '服务器内部错误'
    }), 500


# ==================== 启动应用 ====================

if __name__ == '__main__':
    # 获取端口（从环境变量或默认5000）
    port = int(os.environ.get('DEPLOY_RUN_PORT', 5000))
    
    print(f"""
    ╔════════════════════════════════════════════╗
    ║      A股即时监视系统                       ║
    ║      A-Stock Monitor System                ║
    ╚════════════════════════════════════════════╝
    
    🚀 服务已启动: http://localhost:{port}
    📊 功能列表:
       - 实时行情监控
       - 多种选股策略
       - 热门股票排行
       - 个股详细信息
    
    按 Ctrl+C 停止服务
    """)
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        threaded=True
    )
