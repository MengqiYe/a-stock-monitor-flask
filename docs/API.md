# API 接口文档

本文档详细说明A股即时监视系统提供的所有API接口。

## 基础信息

- **Base URL**: `http://localhost:5000`
- **响应格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

所有API接口返回统一的JSON格式：

```json
{
    "success": true|false,    // 请求是否成功
    "message": "错误信息",     // 仅在失败时返回
    "data": {},               // 响应数据
    "timestamp": "ISO时间戳"   // 部分接口返回
}
```

---

## 行情数据接口

### 1. 获取实时行情

获取所有A股股票的实时行情数据。

**请求**

```
GET /api/realtime
```

**参数**

无

**响应示例**

```json
{
    "success": true,
    "count": 5000,
    "timestamp": "2024-03-21T10:30:00",
    "data": [
        {
            "code": "600519",
            "name": "贵州茅台",
            "price": 1850.00,
            "change_pct": 2.35,
            "change": 42.50,
            "volume": 3500000,
            "amount": 6475000000,
            "amplitude": 3.21,
            "high": 1860.00,
            "low": 1810.00,
            "open": 1820.00,
            "pre_close": 1807.50,
            "turnover_rate": 0.28,
            "pe_ratio": 35.6,
            "pb_ratio": 12.3,
            "total_mv": 2325000000000,
            "circ_mv": 2325000000000
        }
        // ... 更多股票
    ]
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码 |
| name | string | 股票名称 |
| price | float | 最新价（元） |
| change_pct | float | 涨跌幅（%） |
| change | float | 涨跌额（元） |
| volume | int | 成交量（股） |
| amount | int | 成交额（元） |
| amplitude | float | 振幅（%） |
| high | float | 最高价（元） |
| low | float | 最低价（元） |
| open | float | 开盘价（元） |
| pre_close | float | 昨收价（元） |
| turnover_rate | float | 换手率（%） |
| pe_ratio | float | 市盈率（动态） |
| pb_ratio | float | 市净率 |
| total_mv | int | 总市值（元） |
| circ_mv | int | 流通市值（元） |

---

### 2. 获取热门股票

获取各类热门股票排行榜。

**请求**

```
GET /api/hot?top=10
```

**参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| top | int | 否 | 10 | 每个榜单返回的股票数量 |

**响应示例**

```json
{
    "success": true,
    "data": {
        "gainers": [
            {
                "code": "300001",
                "name": "特锐德",
                "price": 25.60,
                "change_pct": 10.02
                // ... 其他字段
            }
            // ... 更多股票
        ],
        "losers": [
            {
                "code": "600001",
                "name": "邯郸钢铁",
                "price": 3.45,
                "change_pct": -9.87
                // ... 其他字段
            }
            // ... 更多股票
        ],
        "volume_top": [
            // 成交额榜前N只
        ],
        "turnover_top": [
            // 换手率榜前N只
        ]
    }
}
```

**榜单说明**

| 榜单 | 说明 |
|------|------|
| gainers | 涨幅榜：涨幅最大的股票 |
| losers | 跌幅榜：跌幅最大的股票 |
| volume_top | 成交额榜：成交额最大的股票 |
| turnover_top | 换手率榜：换手率最高的股票 |

---

### 3. 获取个股信息

获取指定股票的详细信息。

**请求**

```
GET /api/stock/{code}
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码（如：600519） |

**响应示例**

```json
{
    "success": true,
    "data": {
        "code": "600519",
        "name": "贵州茅台",
        "price": 1850.00,
        "change_pct": 2.35,
        // ... 其他实时行情字段
        "history": [
            {
                "date": "2024-03-20",
                "open": 1805.00,
                "close": 1807.50,
                "high": 1815.00,
                "low": 1798.00,
                "volume": 3200000,
                "amount": 5780000000
            }
            // ... 最近60个交易日数据
        ]
    }
}
```

---

### 4. 搜索股票

根据关键词搜索股票。

**请求**

```
GET /api/search?keyword=茅台
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词（股票代码或名称） |

**响应示例**

```json
{
    "success": true,
    "count": 1,
    "data": [
        {
            "code": "600519",
            "name": "贵州茅台",
            "price": 1850.00,
            "change_pct": 2.35
            // ... 其他字段
        }
    ]
}
```

---

## 选股策略接口

### 5. 获取策略列表

获取所有可用的选股策略。

**请求**

```
GET /api/strategies
```

**响应示例**

```json
{
    "success": true,
    "data": [
        {
            "id": "momentum",
            "name": "动量策略",
            "description": "选择近期涨幅较大、动量强劲的股票"
        },
        {
            "id": "mean_reversion",
            "name": "均值回归策略",
            "description": "选择超跌反弹、可能出现均值回归的股票"
        },
        {
            "id": "volume_price",
            "name": "量价策略",
            "description": "选择量价齐升、资金活跃的股票"
        },
        {
            "id": "technical",
            "name": "技术指标策略",
            "description": "选择估值合理、基本面良好的股票"
        },
        {
            "id": "breakout",
            "name": "突破策略",
            "description": "选择创阶段新高、突破上涨的股票"
        }
    ]
}
```

---

### 6. 运行指定策略

运行指定的选股策略，返回符合条件的股票。

**请求**

```
GET /api/strategy/{strategy_id}
```

**参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| strategy_id | string | 是 | 策略ID |

**可用策略ID**

| ID | 策略名称 |
|------|------|
| momentum | 动量策略 |
| mean_reversion | 均值回归策略 |
| volume_price | 量价策略 |
| technical | 技术指标策略 |
| breakout | 突破策略 |

**响应示例**

```json
{
    "success": true,
    "strategy": "momentum",
    "count": 15,
    "data": [
        {
            "code": "600519",
            "name": "贵州茅台",
            "price": 1850.00,
            "change_pct": 5.35,
            "strategy": "动量策略",
            "reason": "涨幅5.35%，动量强劲"
            // ... 其他字段
        }
        // ... 更多股票
    ]
}
```

---

### 7. 运行所有策略

一次性运行所有选股策略。

**请求**

```
GET /api/strategies/all
```

**响应示例**

```json
{
    "success": true,
    "data": {
        "momentum": [
            // 动量策略结果
        ],
        "mean_reversion": [
            // 均值回归策略结果
        ],
        "volume_price": [
            // 量价策略结果
        ],
        "technical": [
            // 技术指标策略结果
        ],
        "breakout": [
            // 突破策略结果
        ]
    }
}
```

---

### 8. 获取策略参数

获取指定策略的参数配置。

**请求**

```
GET /api/strategy/{strategy_id}/params
```

**响应示例**

```json
{
    "success": true,
    "data": {
        "min_change_pct": 2.0,
        "min_volume_ratio": 1.5,
        "top_n": 20
    }
}
```

---

### 9. 更新策略参数

动态更新指定策略的参数配置。

**请求**

```
POST /api/strategy/{strategy_id}/params
Content-Type: application/json
```

**请求体**

```json
{
    "min_change_pct": 3.0,
    "top_n": 30
}
```

**响应示例**

```json
{
    "success": true,
    "message": "参数更新成功"
}
```

**示例**

```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"min_change_pct": 3.0, "top_n": 30}' \
     http://localhost:5000/api/strategy/momentum/params
```

---

## 量化交易接口

### 10. 获取量化策略列表

获取所有可用的量化交易策略。

**请求**

```
GET /api/quant/strategies
```

**响应示例**

```json
{
    "success": true,
    "data": [
        {
            "id": "sma",
            "name": "双均线策略",
            "description": "使用快慢两条移动平均线，金叉买入死叉卖出",
            "params": {
                "fast_period": {"type": "int", "default": 5, "min": 2, "max": 50},
                "slow_period": {"type": "int", "default": 20, "min": 5, "max": 200}
            }
        }
        // ... 更多策略
    ]
}
```

---

### 11. 运行量化策略回测

对指定股票运行量化策略回测。

**请求**

```
POST /api/quant/backtest
Content-Type: application/json
```

**请求体**

```json
{
    "code": "600519",
    "strategy_id": "sma",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_cash": 100000,
    "commission_rate": 0.0003,
    "strategy_params": {
        "fast_period": 5,
        "slow_period": 20
    }
}
```

**响应示例**

```json
{
    "success": true,
    "data": {
        "symbol": "600519",
        "metrics": {
            "total_return": 25.6,
            "annual_return": 30.7,
            "max_drawdown": 12.3,
            "sharpe_ratio": 1.45,
            "win_rate": 58.3,
            "profit_factor": 1.8,
            "total_trades": 24,
            "winning_trades": 14,
            "losing_trades": 10
        },
        "equity_curve": [],
        "trades": []
    }
}
```

---

### 12. 策略对比分析

对同一只股票运行多个策略进行对比。

**请求**

```
POST /api/quant/backtest/compare
Content-Type: application/json
```

**请求体**

```json
{
    "code": "600519",
    "strategies": ["sma", "macd", "rsi", "bollinger"],
    "initial_cash": 100000
}
```

**响应示例**

```json
{
    "success": true,
    "data": {
        "code": "600519",
        "comparison": [
            {
                "strategy_id": "macd",
                "total_return": 32.5,
                "max_drawdown": 10.2,
                "sharpe_ratio": 1.8,
                "win_rate": 62.5,
                "total_trades": 16
            }
            // ... 更多策略结果
        ]
    }
}
```

---

### 13. 计算技术指标

计算股票的技术指标。

**请求**

```
POST /api/quant/indicators
Content-Type: application/json
```

**请求体**

```json
{
    "code": "600519",
    "indicators": ["sma", "rsi", "macd", "bollinger"],
    "params": {
        "sma_period": 20,
        "rsi_period": 14
    }
}
```

**响应示例**

```json
{
    "success": true,
    "count": 120,
    "data": [
        {
            "date": "2023-12-01",
            "close": 1850.00,
            "sma": 1820.50,
            "rsi": 65.3,
            "macd": 12.5,
            "macd_signal": 10.2,
            "bb_upper": 1900.0,
            "bb_lower": 1750.0
        }
        // ... 更多数据
    ]
}
```

---

## 错误响应

当请求失败时，API返回以下格式的错误信息：

```json
{
    "success": false,
    "message": "错误描述"
}
```

**常见错误码**

| HTTP状态码 | 说明 |
|------------|------|
| 400 | 请求参数错误 |
| 404 | 资源未找到 |
| 500 | 服务器内部错误 |

---

## 使用示例

### Python 示例

```python
import requests

BASE_URL = "http://localhost:5000"

# 获取实时行情
response = requests.get(f"{BASE_URL}/api/realtime")
data = response.json()
print(f"共获取 {data['count']} 只股票数据")

# 运动动量策略
response = requests.get(f"{BASE_URL}/api/strategy/momentum")
data = response.json()
for stock in data['data'][:5]:
    print(f"{stock['code']} {stock['name']}: {stock['reason']}")
```

### JavaScript 示例

```javascript
const BASE_URL = "http://localhost:5000";

// 获取实时行情
async function getRealtimeQuotes() {
    const response = await fetch(`${BASE_URL}/api/realtime`);
    const data = await response.json();
    console.log(`共获取 ${data.count} 只股票数据`);
    return data;
}

// 运行动量策略
async function runMomentumStrategy() {
    const response = await fetch(`${BASE_URL}/api/strategy/momentum`);
    const data = await response.json();
    data.data.slice(0, 5).forEach(stock => {
        console.log(`${stock.code} ${stock.name}: ${stock.reason}`);
    });
}
```

### cURL 示例

```bash
# 获取实时行情
curl http://localhost:5000/api/realtime

# 获取热门股票
curl http://localhost:5000/api/hot?top=5

# 搜索股票
curl "http://localhost:5000/api/search?keyword=茅台"

# 运行动量策略
curl http://localhost:5000/api/strategy/momentum

# 更新策略参数
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"min_change_pct": 3.0}' \
     http://localhost:5000/api/strategy/momentum/params
```

---

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2024-03 | 初始版本 |
