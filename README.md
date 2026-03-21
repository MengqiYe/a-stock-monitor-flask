# A股即时监视系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**一个基于 Python Flask 的 A股实时行情监控系统，覆盖全市场5491只A股，提供多种智能选股策略**

[功能特性](#功能特性) • [快速开始](#快速开始) • [选股策略](#选股策略) • [API文档](docs/API.md)

</div>

---

## 📖 项目简介

A股即时监视系统是一个功能完整的股票行情监控平台，旨在帮助投资者：

- 📊 **全市场监控**：覆盖**5491只A股**和**135只港股**，按市场和行业分类浏览
- 📈 **指数追踪**：上证指数、深证成指、创业板指等9大A股指数 + 3大港股指数
- 🎯 **智能选股**：提供5种专业选股策略
- 🔥 **热门排行**：涨幅榜、跌幅榜、成交额榜、换手率榜
- 🔍 **股票搜索**：按代码或名称快速搜索股票

## ✨ 功能特性

### 1. 全市场股票浏览 ⭐ NEW
- **全部A股**：5,491只上市股票实时数据
- **市场分类**：
  - 沪市主板：1,703只
  - 科创板：603只
  - 深市主板：527只
  - 中小板：922只
  - 创业板：1,392只
- **行业分类**：医药生物、电子、银行、化工等30+行业
- **分页浏览**：支持按市场和行业筛选，分页展示

### 2. 指数数据中心 ⭐ NEW
**A股主要指数（9只）**：
- 上证指数、深证成指、创业板指
- 上证50、沪深300、中证500、中证1000
- 中小板指、创业板综

**港股指数（3只）**：
- 恒生指数
- 恒生国企指数
- 恒生科技指数

**成分股查看**：点击任意指数卡片，即可查看该指数的成分股列表

### 3. 港股市场 ⭐ NEW
- **港股股票**：135只主要蓝筹股
  - 科技股：腾讯、阿里、美团、京东、小米等
  - 金融股：中国移动、工商银行、招商银行等
  - 消费股：海底捞、安踏、周大福等
- **实时行情**：价格、涨跌幅、成交额、换手率

### 4. 实时行情监控
- 全市场A股实时行情数据
- 股票价格、涨跌幅、成交量等核心指标
- 自动刷新机制（每60秒）
- 数据缓存优化

### 2. 智能选股策略
系统提供5种经过优化的选股策略：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| 动量策略 | 选择近期涨幅较大的股票 | 趋势跟踪、短线交易 |
| 均值回归策略 | 选择超跌反弹股票 | 逆向投资、中长线 |
| 量价策略 | 选择量价齐升的股票 | 资金流向分析 |
| 技术指标策略 | 选择估值合理的股票 | 价值投资 |
| 突破策略 | 选择创阶段新高的股票 | 突破交易 |

### 3. 量化交易回测 ⭐ NEW
基于 akquant 框架实现量化交易功能：

**内置量化策略：**

| 策略 | 说明 | 参数 |
|------|------|------|
| 双均线策略 | 快慢均线金叉买入、死叉卖出 | 快线周期、慢线周期 |
| MACD策略 | MACD金叉死叉交易 | 快线、慢线、信号线周期 |
| RSI策略 | 超卖买入、超买卖出 | RSI周期、超买超卖阈值 |
| 布林带策略 | 触及下轨买入、上轨卖出 | 周期、标准差倍数 |

**回测功能：**
- 完整的策略回测引擎
- 回测指标计算（收益率、最大回撤、夏普比率、胜率等）
- 多策略对比分析
- 技术指标计算（SMA、EMA、RSI、MACD、布林带、ATR等）

### 4. 市场全景监控 ⭐ NEW
- 市场整体统计（涨跌分布、涨跌停统计）
- 市场情绪指标（基于涨跌比例计算）
- 各市场分类统计（沪市主板、深市主板、创业板、科创板、北交所）
- 平均涨跌幅、总成交额统计

### 5. 板块监控 ⭐ NEW
- 行业板块实时监控
  - 行业涨幅/跌幅排行
  - 行业领涨股票追踪
- 概念板块实时监控
  - 概念涨幅/跌幅排行
  - 热门概念资金流向

### 6. 热门股票排行
- 📈 涨幅榜：当日涨幅最大的股票
- 📉 跌幅榜：当日跌幅最大的股票
- 💰 成交额榜：成交额最大的股票
- 🔄 换手率榜：换手率最高的股票

### 4. 数据可视化
- 现代化响应式前端界面
- 实时数据更新
- 直观的数据展示

## 🚀 快速开始

### 环境要求
- Python 3.11+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/MengqiYe/a-stock-monitor-flask.git
cd a-stock-monitor-flask
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
python app.py
```

4. **访问系统**
打开浏览器访问：http://localhost:5000

### 使用 Docker（可选）

```bash
# 构建镜像
docker build -t a-stock-monitor .

# 运行容器
docker run -p 5000:5000 a-stock-monitor
```

## 📁 项目结构

```
a-stock-monitor-flask/
├── app.py                 # Flask主应用
├── requirements.txt       # Python依赖
├── README.md             # 项目说明文档
├── docs/
│   └── API.md            # API接口文档
├── modules/
│   ├── __init__.py       # 模块初始化
│   ├── data_fetcher.py   # 数据获取模块
│   ├── strategies.py     # 选股策略引擎
│   ├── quant_engine.py   # 量化交易引擎
│   ├── stock_list.py     # 指数和成分股数据 ⭐
│   └── full_stock_list.py # 全市场股票列表管理 ⭐
├── templates/
│   └── index.html        # 前端页面模板
└── static/               # 静态资源目录
```

## 📊 选股策略详解

### 1. 动量策略 (Momentum Strategy)

**核心思想**：强者恒强，选择近期涨幅较大的股票。

**筛选条件**：
- 涨幅 ≥ 2%
- 成交量活跃

**适用场景**：牛市或震荡向上的市场环境，趋势跟踪型投资者

### 2. 均值回归策略 (Mean Reversion Strategy)

**核心思想**：物极必反，选择超跌股票期待反弹。

**筛选条件**：
- 跌幅在 -3% 到 -1% 之间
- 成交量放大

**适用场景**：熊市末期或市场恐慌时，逆向投资型投资者

### 3. 量价策略 (Volume-Price Strategy)

**核心思想**：量在价先，选择量价齐升的股票。

**筛选条件**：
- 涨幅 ≥ 1%
- 换手率 ≥ 5%

**适用场景**：关注资金流向的投资者

### 4. 技术指标策略 (Technical Indicator Strategy)

**核心思想**：寻找估值合理的标的。

**筛选条件**：
- 市盈率在 0-50 之间
- 市净率在 0.5-10 之间

**适用场景**：价值投资型投资者，长线投资

### 5. 突破策略 (Breakout Strategy)

**核心思想**：捕捉突破行情。

**筛选条件**：
- 涨幅 ≥ 2%
- 振幅 ≥ 5%

**适用场景**：趋势跟踪型投资者，短线或波段交易

## 🔌 API 接口

详细API文档请参考：[API.md](docs/API.md)

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/realtime` | GET | 获取实时行情 |
| `/api/hot` | GET | 获取热门股票 |
| `/api/stock/<code>` | GET | 获取个股信息 |
| `/api/search` | GET | 搜索股票 |
| `/api/strategies` | GET | 获取策略列表 |
| `/api/strategy/<id>` | GET | 运行指定策略 |
| `/api/stocks/all` | GET | 获取全部A股列表（分页） ⭐ |
| `/api/stocks/categories` | GET | 获取股票分类统计 ⭐ |
| `/api/stocks/market/<market>` | GET | 按市场获取股票 ⭐ |
| `/api/stocks/industry/<industry>` | GET | 按行业获取股票 ⭐ |
| `/api/indices` | GET | 获取A股指数数据 ⭐ |
| `/api/index/<code>` | GET | 获取指数详情及成分股 ⭐ |
| `/api/hk/stocks` | GET | 获取港股股票列表 ⭐ |
| `/api/hk/indices` | GET | 获取港股指数数据 ⭐ |
| `/api/market/statistics` | GET | 获取市场全景统计 |
| `/api/market/classify` | GET | 获取市场分类数据 |
| `/api/board/industry` | GET | 获取行业板块行情 |
| `/api/board/concept` | GET | 获取概念板块行情 |
| `/api/board/overview` | GET | 获取板块概览 |
| `/api/quant/strategies` | GET | 获取量化策略列表 |
| `/api/quant/backtest` | POST | 运行量化回测 |
| `/api/quant/indicators` | POST | 计算技术指标 |

## ⚙️ 配置说明

### 策略参数调整

可以通过API动态调整策略参数：

```bash
# 更新动量策略的最小涨幅阈值
curl -X POST -H "Content-Type: application/json" \
     -d '{"min_change_pct": 3.0}' \
     http://localhost:5000/api/strategy/momentum/params
```

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEPLOY_RUN_PORT` | 服务端口 | 5000 |

## 📦 依赖说明

主要依赖：

- **Flask** (3.0.0)：Web框架
- **Flask-CORS** (4.0.0)：跨域支持
- **akshare** (≥1.18.0)：A股数据源
- **pandas** (≥2.0.0)：数据处理
- **numpy** (≥1.24.0)：数值计算

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## ⚠️ 免责声明

本项目仅供学习和研究使用，不构成任何投资建议。
股市有风险，投资需谨慎。使用本系统进行投资决策所造成的任何损失，作者不承担任何责任。

## 📮 联系方式

如有问题或建议，请提交 [Issue](https://github.com/MengqiYe/a-stock-monitor-flask/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star ⭐**

</div>
