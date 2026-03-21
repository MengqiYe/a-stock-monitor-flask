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
        # A股股票列表（覆盖各市场：沪市主板、深市主板、创业板、科创板）
        stocks = [
            # ========== 沪市主板 (600/601/603) ==========
            {'code': '600000', 'name': '浦发银行'}, {'code': '600004', 'name': '白云机场'},
            {'code': '600006', 'name': '东风汽车'}, {'code': '600007', 'name': '中国国贸'},
            {'code': '600008', 'name': '首创环保'}, {'code': '600009', 'name': '上海机场'},
            {'code': '600010', 'name': '包钢股份'}, {'code': '600011', 'name': '华能国际'},
            {'code': '600012', 'name': '皖通高速'}, {'code': '600015', 'name': '华夏银行'},
            {'code': '600016', 'name': '民生银行'}, {'code': '600017', 'name': '日照港'},
            {'code': '600018', 'name': '上港集团'}, {'code': '600019', 'name': '宝钢股份'},
            {'code': '600020', 'name': '中原高速'}, {'code': '600021', 'name': '上海电力'},
            {'code': '600022', 'name': '山东钢铁'}, {'code': '600023', 'name': '浙能电力'},
            {'code': '600025', 'name': '华能水电'}, {'code': '600026', 'name': '中远海能'},
            {'code': '600027', 'name': '华电国际'}, {'code': '600028', 'name': '中国石化'},
            {'code': '600029', 'name': '南方航空'}, {'code': '600030', 'name': '中信证券'},
            {'code': '600031', 'name': '三一重工'}, {'code': '600033', 'name': '福建高速'},
            {'code': '600035', 'name': '楚天高速'}, {'code': '600036', 'name': '招商银行'},
            {'code': '600037', 'name': '歌华有线'}, {'code': '600038', 'name': '中直股份'},
            {'code': '600039', 'name': '四川路桥'}, {'code': '600048', 'name': '保利发展'},
            {'code': '600050', 'name': '中国联通'}, {'code': '600056', 'name': '中国医药'},
            {'code': '600058', 'name': '五矿发展'}, {'code': '600059', 'name': '古越龙山'},
            {'code': '600060', 'name': '海信视像'}, {'code': '600061', 'name': '国投资本'},
            {'code': '600062', 'name': '华润双鹤'}, {'code': '600063', 'name': '皖维高新'},
            {'code': '600064', 'name': '南京高科'}, {'code': '600066', 'name': '宇通客车'},
            {'code': '600067', 'name': '冠城大通'}, {'code': '600068', 'name': '葛洲坝'},
            {'code': '600069', 'name': '银鸽投资'}, {'code': '600070', 'name': '浙江富润'},
            {'code': '600071', 'name': '凤凰光学'}, {'code': '600072', 'name': '中船科技'},
            {'code': '600073', 'name': '上海梅林'}, {'code': '600074', 'name': '退市保千'},
            {'code': '600075', 'name': '新疆天业'}, {'code': '600076', 'name': '康欣新材'},
            {'code': '600077', 'name': '宋都股份'}, {'code': '600078', 'name': '澄星股份'},
            {'code': '600079', 'name': '人福医药'}, {'code': '600080', 'name': '金花股份'},
            {'code': '600081', 'name': '东风科技'}, {'code': '600082', 'name': '海泰发展'},
            {'code': '600083', 'name': '博信股份'}, {'code': '600084', 'name': '中葡股份'},
            {'code': '600085', 'name': '同仁堂'}, {'code': '600086', 'name': '东方金钰'},
            {'code': '600088', 'name': '中视传媒'}, {'code': '600089', 'name': '特变电工'},
            {'code': '600090', 'name': '啤酒花'}, {'code': '600091', 'name': '明星电力'},
            {'code': '600092', 'name': '爱建集团'}, {'code': '600093', 'name': '易见股份'},
            {'code': '600095', 'name': '哈高科'}, {'code': '600096', 'name': '云天化'},
            {'code': '600097', 'name': '开创国际'}, {'code': '600098', 'name': '广州发展'},
            {'code': '600099', 'name': '林海股份'}, {'code': '600100', 'name': '同方股份'},
            {'code': '600101', 'name': '明星电力'}, {'code': '600102', 'name': '莱钢股份'},
            {'code': '600103', 'name': '青山纸业'}, {'code': '600104', 'name': '上汽集团'},
            {'code': '600105', 'name': '永鼎股份'}, {'code': '600106', 'name': '重庆路桥'},
            {'code': '600107', 'name': '美尔雅'}, {'code': '600108', 'name': '亚盛集团'},
            {'code': '600109', 'name': '国金证券'}, {'code': '600110', 'name': '诺德股份'},
            {'code': '600111', 'name': '北方稀土'}, {'code': '600112', 'name': '天成控股'},
            {'code': '600113', 'name': '浙江东日'}, {'code': '600114', 'name': '东睦股份'},
            {'code': '600115', 'name': '中国东航'}, {'code': '600116', 'name': '三峡水利'},
            {'code': '600117', 'name': '西宁特钢'}, {'code': '600118', 'name': '中国卫星'},
            {'code': '600119', 'name': '长江投资'}, {'code': '600120', 'name': '浙江东方'},
            {'code': '600121', 'name': '郑州煤电'}, {'code': '600122', 'name': '宏图高科'},
            {'code': '600123', 'name': '兰花科创'}, {'code': '600125', 'name': '铁龙物流'},
            {'code': '600126', 'name': '杭钢股份'}, {'code': '600127', 'name': '金健米业'},
            {'code': '600128', 'name': '弘业股份'}, {'code': '600129', 'name': '太极集团'},
            {'code': '600130', 'name': '波导股份'}, {'code': '600131', 'name': '岷江水电'},
            {'code': '600132', 'name': '重庆啤酒'}, {'code': '600133', 'name': '东湖高新'},
            {'code': '600135', 'name': '乐凯胶片'}, {'code': '600136', 'name': '当代文体'},
            {'code': '600137', 'name': '浪莎股份'}, {'code': '600138', 'name': '中青旅'},
            {'code': '600139', 'name': '西部资源'}, {'code': '600141', 'name': '兴发集团'},
            {'code': '600142', 'name': '华润材料'}, {'code': '600143', 'name': '金发科技'},
            {'code': '600145', 'name': '*ST金宇'}, {'code': '600146', 'name': '商赢环球'},
            {'code': '600148', 'name': '长春一东'}, {'code': '600149', 'name': '廊坊发展'},
            {'code': '600150', 'name': '中国船舶'}, {'code': '600151', 'name': '航天机电'},
            {'code': '600152', 'name': '维科技术'}, {'code': '600153', 'name': '建发股份'},
            {'code': '600155', 'name': '华创阳安'}, {'code': '600156', 'name': '华升股份'},
            {'code': '600157', 'name': '永泰能源'}, {'code': '600158', 'name': '中体产业'},
            {'code': '600159', 'name': '大龙地产'}, {'code': '600160', 'name': '巨化股份'},
            {'code': '600161', 'name': '天坛生物'}, {'code': '600162', 'name': '香江控股'},
            {'code': '600163', 'name': '中闽能源'}, {'code': '600165', 'name': '新日恒力'},
            {'code': '600166', 'name': '福田汽车'}, {'code': '600167', 'name': '联美控股'},
            {'code': '600168', 'name': '武汉控股'}, {'code': '600169', 'name': '太原重工'},
            {'code': '600170', 'name': '上海建工'}, {'code': '600171', 'name': '上海贝岭'},
            {'code': '600172', 'name': '黄河旋风'}, {'code': '600173', 'name': '卧龙地产'},
            {'code': '600175', 'name': '美都能源'}, {'code': '600176', 'name': '中国巨石'},
            {'code': '600177', 'name': '雅戈尔'}, {'code': '600178', 'name': '东安动力'},
            {'code': '600179', 'name': '安通控股'}, {'code': '600180', 'name': '瑞茂通'},
            {'code': '600182', 'name': 'S佳通'}, {'code': '600183', 'name': '生益科技'},
            {'code': '600184', 'name': '光电股份'}, {'code': '600185', 'name': '格力地产'},
            {'code': '600186', 'name': '莲花健康'}, {'code': '600187', 'name': '国中水务'},
            {'code': '600188', 'name': '兖州煤业'}, {'code': '600189', 'name': '吉林森工'},
            {'code': '600190', 'name': '锦州港'}, {'code': '600191', 'name': '华资实业'},
            {'code': '600192', 'name': '长城电工'}, {'code': '600193', 'name': '创兴资源'},
            {'code': '600195', 'name': '中牧股份'}, {'code': '600196', 'name': '复星医药'},
            {'code': '600197', 'name': '伊力特'}, {'code': '600198', 'name': '大唐电信'},
            {'code': '600199', 'name': '金种子酒'}, {'code': '600200', 'name': '江苏吴中'},
            # 更多沪市主板
            {'code': '600519', 'name': '贵州茅台'}, {'code': '600887', 'name': '伊利股份'},
            {'code': '600900', 'name': '长江电力'}, {'code': '601318', 'name': '中国平安'},
            {'code': '601398', 'name': '工商银行'}, {'code': '601857', 'name': '中国石油'},
            {'code': '601988', 'name': '中国银行'}, {'code': '601288', 'name': '农业银行'},
            {'code': '600276', 'name': '恒瑞医药'}, {'code': '600585', 'name': '海螺水泥'},
            {'code': '600690', 'name': '海尔智家'}, {'code': '600809', 'name': '山西汾酒'},
            {'code': '600309', 'name': '万华化学'}, {'code': '600406', 'name': '国电南瑞'},
            {'code': '600489', 'name': '中金黄金'}, {'code': '600660', 'name': '福耀玻璃'},
            
            # ========== 深市主板 (000/001) ==========
            {'code': '000001', 'name': '平安银行'}, {'code': '000002', 'name': '万科A'},
            {'code': '000004', 'name': '国华网安'}, {'code': '000005', 'name': 'ST星源'},
            {'code': '000006', 'name': '深振业A'}, {'code': '000007', 'name': '全新好'},
            {'code': '000008', 'name': '神州高铁'}, {'code': '000009', 'name': '中国宝安'},
            {'code': '000010', 'name': '美丽生态'}, {'code': '000011', 'name': '深物业A'},
            {'code': '000012', 'name': '南玻A'}, {'code': '000014', 'name': '沙河股份'},
            {'code': '000016', 'name': '深康佳A'}, {'code': '000017', 'name': '深中华A'},
            {'code': '000018', 'name': '神城A退'}, {'code': '000019', 'name': '深粮控股'},
            {'code': '000020', 'name': '深华发A'}, {'code': '000021', 'name': '深科技'},
            {'code': '000022', 'name': '深赤湾A'}, {'code': '000023', 'name': '深天地A'},
            {'code': '000025', 'name': '特力A'}, {'code': '000026', 'name': '飞亚达'},
            {'code': '000027', 'name': '深圳能源'}, {'code': '000028', 'name': '国药一致'},
            {'code': '000029', 'name': '深深房A'}, {'code': '000030', 'name': '富奥股份'},
            {'code': '000031', 'name': '大悦城'}, {'code': '000032', 'name': '深桑达A'},
            {'code': '000034', 'name': '神州数码'}, {'code': '000035', 'name': '中国天楹'},
            {'code': '000036', 'name': '华联控股'}, {'code': '000037', 'name': '深南电A'},
            {'code': '000038', 'name': '深大通'}, {'code': '000039', 'name': '中集集团'},
            {'code': '000040', 'name': '东旭蓝天'}, {'code': '000042', 'name': '中洲控股'},
            {'code': '000043', 'name': '中航地产'}, {'code': '000045', 'name': '深纺织A'},
            {'code': '000046', 'name': '泛海控股'}, {'code': '000048', 'name': '京基智农'},
            {'code': '000049', 'name': '德赛电池'}, {'code': '000050', 'name': '深天马A'},
            {'code': '000055', 'name': '方大集团'}, {'code': '000056', 'name': '皇庭国际'},
            {'code': '000058', 'name': '深赛格'}, {'code': '000059', 'name': '华锦股份'},
            {'code': '000060', 'name': '中金岭南'}, {'code': '000061', 'name': '农产品'},
            {'code': '000062', 'name': '深圳华强'}, {'code': '000063', 'name': '中兴通讯'},
            {'code': '000065', 'name': '北方国际'}, {'code': '000066', 'name': '中国长城'},
            {'code': '000068', 'name': '华控赛格'}, {'code': '000069', 'name': '华侨城A'},
            {'code': '000070', 'name': '特发信息'}, {'code': '000078', 'name': '海王生物'},
            {'code': '000088', 'name': '盐田港'}, {'code': '000089', 'name': '深圳机场'},
            {'code': '000090', 'name': '天健集团'}, {'code': '000096', 'name': '广聚能源'},
            {'code': '000099', 'name': '中信海直'}, {'code': '000100', 'name': 'TCL科技'},
            {'code': '000155', 'name': '川能动力'}, {'code': '000157', 'name': '中联重科'},
            {'code': '000158', 'name': '常山北明'}, {'code': '000159', 'name': '国际实业'},
            {'code': '000400', 'name': '许继电气'}, {'code': '000401', 'name': '冀东水泥'},
            {'code': '000402', 'name': '金融街'}, {'code': '000333', 'name': '美的集团'},
            {'code': '000651', 'name': '格力电器'}, {'code': '000725', 'name': '京东方A'},
            {'code': '000858', 'name': '五粮液'}, {'code': '000895', 'name': '双汇发展'},
            {'code': '000876', 'name': '新希望'}, {'code': '000776', 'name': '广发证券'},
            {'code': '000568', 'name': '泸州老窖'}, {'code': '000538', 'name': '云南白药'},
            {'code': '000066', 'name': '中国长城'}, {'code': '000708', 'name': '中信特钢'},
            {'code': '000768', 'name': '中航西飞'}, {'code': '000725', 'name': '京东方A'},
            {'code': '000002', 'name': '万科A'}, {'code': '000001', 'name': '平安银行'},
            
            # ========== 创业板 (300) ==========
            {'code': '300001', 'name': '特锐德'}, {'code': '300002', 'name': '神州泰岳'},
            {'code': '300003', 'name': '乐普医疗'}, {'code': '300004', 'name': '南风股份'},
            {'code': '300005', 'name': '探路者'}, {'code': '300006', 'name': '莱美药业'},
            {'code': '300007', 'name': '汉威科技'}, {'code': '300008', 'name': '天海防务'},
            {'code': '300009', 'name': '安科生物'}, {'code': '300010', 'name': '立思辰'},
            {'code': '300011', 'name': '鼎汉技术'}, {'code': '300012', 'name': '华测检测'},
            {'code': '300013', 'name': '新宁物流'}, {'code': '300014', 'name': '亿纬锂能'},
            {'code': '300015', 'name': '爱尔眼科'}, {'code': '300016', 'name': '北陆药业'},
            {'code': '300017', 'name': '网宿科技'}, {'code': '300018', 'name': '中元股份'},
            {'code': '300019', 'name': '硅宝科技'}, {'code': '300020', 'name': '银江股份'},
            {'code': '300022', 'name': '吉峰科技'}, {'code': '300023', 'name': '宝德股份'},
            {'code': '300024', 'name': '机器人'}, {'code': '300025', 'name': '华星创业'},
            {'code': '300026', 'name': '红日药业'}, {'code': '300027', 'name': '华谊兄弟'},
            {'code': '300028', 'name': '金亚科技'}, {'code': '300029', 'name': '天龙光电'},
            {'code': '300030', 'name': '阳普医疗'}, {'code': '300031', 'name': '宝通科技'},
            {'code': '300033', 'name': '同花顺'}, {'code': '300034', 'name': '钢研高纳'},
            {'code': '300035', 'name': '中科电气'}, {'code': '300036', 'name': '超图软件'},
            {'code': '300037', 'name': '新宙邦'}, {'code': '300038', 'name': '梅安森'},
            {'code': '300039', 'name': '上海凯宝'}, {'code': '300040', 'name': '九洲集团'},
            {'code': '300044', 'name': '赛为智能'}, {'code': '300045', 'name': '华力创通'},
            {'code': '300046', 'name': '台基股份'}, {'code': '300048', 'name': '金明精机'},
            {'code': '300049', 'name': '福瑞股份'}, {'code': '300050', 'name': '世纪鼎利'},
            {'code': '300051', 'name': '三五互联'}, {'code': '300052', 'name': '中青宝'},
            {'code': '300053', 'name': '欧比特'}, {'code': '300054', 'name': '鼎龙股份'},
            {'code': '300055', 'name': '万邦达'}, {'code': '300056', 'name': '三维丝'},
            {'code': '300057', 'name': '万顺新材'}, {'code': '300058', 'name': '蓝色光标'},
            {'code': '300059', 'name': '东方财富'}, {'code': '300060', 'name': '昆仑万维'},
            {'code': '300061', 'name': '旗天科技'}, {'code': '300062', 'name': '中能电气'},
            {'code': '300063', 'name': '天龙集团'}, {'code': '300065', 'name': '海兰信'},
            {'code': '300066', 'name': '三川智慧'}, {'code': '300067', 'name': '安诺其'},
            {'code': '300068', 'name': '南都电源'}, {'code': '300069', 'name': '金利华电'},
            {'code': '300070', 'name': '碧水源'}, {'code': '300071', 'name': '华谊嘉信'},
            {'code': '300072', 'name': '三聚环保'}, {'code': '300073', 'name': '当升科技'},
            {'code': '300074', 'name': '华铁应急'}, {'code': '300075', 'name': '数字政通'},
            {'code': '300076', 'name': 'GQY视讯'}, {'code': '300077', 'name': '国民技术'},
            {'code': '300078', 'name': '思创医惠'}, {'code': '300079', 'name': '数码科技'},
            {'code': '300080', 'name': '易成新能'}, {'code': '300081', 'name': '恒信东方'},
            {'code': '300082', 'name': '奥克股份'}, {'code': '300083', 'name': '创世纪'},
            {'code': '300084', 'name': '海默科技'}, {'code': '300085', 'name': '银之杰'},
            {'code': '300086', 'name': '康芝药业'}, {'code': '300087', 'name': '荃银高科'},
            {'code': '300088', 'name': '长信科技'}, {'code': '300089', 'name': '长城集团'},
            {'code': '300090', 'name': '盛运环保'}, {'code': '300091', 'name': '金通灵'},
            {'code': '300092', 'name': '科新机电'}, {'code': '300093', 'name': '金刚光伏'},
            {'code': '300094', 'name': '国联水产'}, {'code': '300095', 'name': '华伍股份'},
            {'code': '300096', 'name': '易联众'}, {'code': '300097', 'name': '智云股份'},
            {'code': '300098', 'name': '高新兴'}, {'code': '300099', 'name': '精准信息'},
            {'code': '300750', 'name': '宁德时代'}, {'code': '300760', 'name': '迈瑞医疗'},
            {'code': '300059', 'name': '东方财富'}, {'code': '300347', 'name': '泰格医药'},
            {'code': '300124', 'name': '汇川技术'}, {'code': '300122', 'name': '智飞生物'},
            {'code': '300142', 'name': '沃森生物'}, {'code': '300144', 'name': '宋城演艺'},
            {'code': '300408', 'name': '三环集团'}, {'code': '300450', 'name': '先导智能'},
            {'code': '300496', 'name': '中科创达'}, {'code': '300661', 'name': '圣邦股份'},
            {'code': '300782', 'name': '卓胜微'}, {'code': '300037', 'name': '新宙邦'},
            
            # ========== 科创板 (688) ==========
            {'code': '688001', 'name': '华兴源创'}, {'code': '688002', 'name': '睿创微纳'},
            {'code': '688003', 'name': '澜起科技'}, {'code': '688004', 'name': '博汇科技'},
            {'code': '688005', 'name': '容百科技'}, {'code': '688006', 'name': '奥比中光'},
            {'code': '688007', 'name': '光峰科技'}, {'code': '688008', 'name': '澜起科技'},
            {'code': '688009', 'name': '中国通号'}, {'code': '688010', 'name': '福光股份'},
            {'code': '688011', 'name': '新光光电'}, {'code': '688012', 'name': '中微公司'},
            {'code': '688015', 'name': '交控科技'}, {'code': '688016', 'name': '心脉医疗'},
            {'code': '688017', 'name': '绿的谐波'}, {'code': '688018', 'name': '乐鑫科技'},
            {'code': '688019', 'name': '安集科技'}, {'code': '688020', 'name': '方邦股份'},
            {'code': '688022', 'name': '瀚川智能'}, {'code': '688023', 'name': '安恒信息'},
            {'code': '688025', 'name': '杰普特'}, {'code': '688026', 'name': '洁特生物'},
            {'code': '688028', 'name': '沃尔德'}, {'code': '688029', 'name': '南微医学'},
            {'code': '688030', 'name': '山大地纬'}, {'code': '688032', 'name': '禾迈股份'},
            {'code': '688033', 'name': '天宜上佳'}, {'code': '688036', 'name': '传音控股'},
            {'code': '688037', 'name': '芯源微'}, {'code': '688038', 'name': '中科通达'},
            {'code': '688041', 'name': '海光信息'}, {'code': '688042', 'name': '高测股份'},
            {'code': '688043', 'name': '芯源微'}, {'code': '688045', 'name': '必易微'},
            {'code': '688046', 'name': '药康生物'}, {'code': '688047', 'name': '龙芯中科'},
            {'code': '688048', 'name': '长光华芯'}, {'code': '688050', 'name': '爱博医疗'},
            {'code': '688052', 'name': '纳芯微'}, {'code': '688055', 'name': '凯德石英'},
            {'code': '688056', 'name': '莱伯泰科'}, {'code': '688058', 'name': '宝兰德'},
            {'code': '688059', 'name': '华锐精密'}, {'code': '688060', 'name': '云路股份'},
            {'code': '688063', 'name': '澜起科技'}, {'code': '688065', 'name': '凯盛新材'},
            {'code': '688066', 'name': '航天宏图'}, {'code': '688067', 'name': '爱威科技'},
            {'code': '688068', 'name': '景业智能'}, {'code': '688069', 'name': '德林海'},
            {'code': '688070', 'name': '纵横股份'}, {'code': '688071', 'name': '华依科技'},
            {'code': '688072', 'name': '拓荆科技'}, {'code': '688076', 'name': '诺泰生物'},
            {'code': '688077', 'name': '大地熊'}, {'code': '688078', 'name': '龙软科技'},
            {'code': '688079', 'name': '华锐精密'}, {'code': '688080', 'name': '映翰通'},
            {'code': '688081', 'name': '兴图新科'}, {'code': '688082', 'name': '盛美上海'},
            {'code': '688083', 'name': '中望软件'}, {'code': '688085', 'name': '三友医疗'},
            {'code': '688086', 'name': '绿的谐波'}, {'code': '688088', 'name': '澜起科技'},
            {'code': '688089', 'name': '嘉楠科技'}, {'code': '688090', 'name': '瑞松科技'},
            {'code': '688098', 'name': '申联生物'}, {'code': '688099', 'name': '晶晨股份'},
            {'code': '688100', 'name': '威胜信息'}, {'code': '688101', 'name': '华达新材'},
            {'code': '688111', 'name': '金山办公'}, {'code': '688126', 'name': '沪硅产业'},
            {'code': '688169', 'name': '石头科技'}, {'code': '688180', 'name': '君实生物'},
            {'code': '688185', 'name': '康希诺'}, {'code': '688187', 'name': '时代电气'},
            {'code': '688223', 'name': '晶科能源'}, {'code': '688256', 'name': '寒武纪'},
            {'code': '688303', 'name': '大全能源'}, {'code': '688369', 'name': '致远互联'},
            {'code': '688396', 'name': '华润微'}, {'code': '688567', 'name': '孚能科技'},
            {'code': '688598', 'name': '金博股份'}, {'code': '688981', 'name': '中芯国际'},
            
            # ========== 中小板 (002) ==========
            {'code': '002001', 'name': '新和成'}, {'code': '002002', 'name': '鸿达兴业'},
            {'code': '002003', 'name': '伟星股份'}, {'code': '002004', 'name': '华邦健康'},
            {'code': '002005', 'name': 'ST德豪'}, {'code': '002006', 'name': '精功科技'},
            {'code': '002007', 'name': '华兰生物'}, {'code': '002008', 'name': '大族激光'},
            {'code': '002009', 'name': '索菲亚'}, {'code': '002010', 'name': '传化智联'},
            {'code': '002011', 'name': '盾安环境'}, {'code': '002012', 'name': '凯恩股份'},
            {'code': '002013', 'name': '中航机电'}, {'code': '002014', 'name': '永新股份'},
            {'code': '002015', 'name': '霞客环保'}, {'code': '002016', 'name': '世荣兆业'},
            {'code': '002017', 'name': '东信和平'}, {'code': '002018', 'name': '华星创业'},
            {'code': '002019', 'name': '亿帆医药'}, {'code': '002020', 'name': '京新药业'},
            {'code': '002021', 'name': '中捷资源'}, {'code': '002022', 'name': '科华生物'},
            {'code': '002023', 'name': '海特高新'}, {'code': '002024', 'name': '苏宁易购'},
            {'code': '002025', 'name': '航天电器'}, {'code': '002026', 'name': '山东威达'},
            {'code': '002027', 'name': '分众传媒'}, {'code': '002028', 'name': '思源电气'},
            {'code': '002029', 'name': '七匹狼'}, {'code': '002030', 'name': '达安基因'},
            {'code': '002031', 'name': '巨轮智能'}, {'code': '002032', 'name': '苏泊尔'},
            {'code': '002033', 'name': '丽江股份'}, {'code': '002034', 'name': '旺能环境'},
            {'code': '002035', 'name': '华帝股份'}, {'code': '002036', 'name': '联创电子'},
            {'code': '002037', 'name': '保利联合'}, {'code': '002038', 'name': '双鹭药业'},
            {'code': '002039', 'name': '黔源电力'}, {'code': '002040', 'name': '南京港'},
            {'code': '002041', 'name': '登海种业'}, {'code': '002042', 'name': '华孚时尚'},
            {'code': '002043', 'name': '兔宝宝'}, {'code': '002044', 'name': '美年健康'},
            {'code': '002045', 'name': '国光电器'}, {'code': '002046', 'name': '轴研科技'},
            {'code': '002047', 'name': '宝鹰股份'}, {'code': '002048', 'name': '宁波华翔'},
            {'code': '002049', 'name': '紫光国微'}, {'code': '002050', 'name': '三花智控'},
            {'code': '002051', 'name': '中工国际'}, {'code': '002052', 'name': '同洲电子'},
            {'code': '002053', 'name': '云南能投'}, {'code': '002054', 'name': '德美化工'},
            {'code': '002055', 'name': '得润电子'}, {'code': '002056', 'name': '横店东磁'},
            {'code': '002057', 'name': '中钢天源'}, {'code': '002058', 'name': '威尔药业'},
            {'code': '002059', 'name': '云南旅游'}, {'code': '002060', 'name': '粤水电'},
            {'code': '002061', 'name': '浙江交科'}, {'code': '002062', 'name': '宏润建设'},
            {'code': '002063', 'name': '远光软件'}, {'code': '002064', 'name': '华峰氨纶'},
            {'code': '002065', 'name': '东华软件'}, {'code': '002066', 'name': '瑞泰科技'},
            {'code': '002067', 'name': '景兴纸业'}, {'code': '002068', 'name': '黑猫股份'},
            {'code': '002069', 'name': '獐子岛'}, {'code': '002070', 'name': '众和退'},
            {'code': '002071', 'name': '长城影视'}, {'code': '002072', 'name': '凯瑞德'},
            {'code': '002073', 'name': '软控股份'}, {'code': '002074', 'name': '国轩高科'},
            {'code': '002075', 'name': '沙钢股份'}, {'code': '002076', 'name': '雪莱特'},
            {'code': '002077', 'name': '大港股份'}, {'code': '002078', 'name': '太阳纸业'},
            {'code': '002079', 'name': '苏州固锝'}, {'code': '002080', 'name': '中材科技'},
            {'code': '002081', 'name': '金螳螂'}, {'code': '002082', 'name': '万邦德'},
            {'code': '002083', 'name': '孚日股份'}, {'code': '002084', 'name': '海鸥住工'},
            {'code': '002085', 'name': '万丰奥威'}, {'code': '002086', 'name': '东方海洋'},
            {'code': '002087', 'name': '新野纺织'}, {'code': '002088', 'name': '鲁阳节能'},
            {'code': '002089', 'name': '新海宜'}, {'code': '002090', 'name': '金智科技'},
            {'code': '002091', 'name': '江苏国泰'}, {'code': '002092', 'name': '中泰化学'},
            {'code': '002093', 'name': '国脉科技'}, {'code': '002094', 'name': '青岛金王'},
            {'code': '002095', 'name': '生意宝'}, {'code': '002096', 'name': '南岭民爆'},
            {'code': '002097', 'name': '山河智能'}, {'code': '002098', 'name': '浔兴股份'},
            {'code': '002099', 'name': '海翔药业'}, {'code': '002100', 'name': '天康生物'},
            {'code': '002352', 'name': '顺丰控股'}, {'code': '002415', 'name': '海康威视'},
            {'code': '002475', 'name': '立讯精密'}, {'code': '002594', 'name': '比亚迪'},
            {'code': '002460', 'name': '赣锋锂业'}, {'code': '002493', 'name': '荣盛石化'},
            {'code': '002466', 'name': '天齐锂业'}, {'code': '002410', 'name': '广联达'},
            {'code': '002230', 'name': '科大讯飞'}, {'code': '002304', 'name': '洋河股份'},
            {'code': '002142', 'name': '宁波银行'}, {'code': '002714', 'name': '牧原股份'},
            {'code': '002475', 'name': '立讯精密'}, {'code': '002129', 'name': 'TCL中环'},
        ]
        
        data = []
        for stock in stocks:
            # 生成随机但合理的股价数据
            pre_close = random.uniform(10, 500)  # 昨收价
            change_pct = random.uniform(-9.9, 9.9)  # 涨跌幅（-10% ~ 10%）
            price = pre_close * (1 + change_pct / 100)  # 最新价
            
            data.append({
                'code': stock['code'],
                'name': stock['name'],
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
    
    def search_stocks(self, keyword: str) -> pd.DataFrame:
        """
        搜索股票
        
        根据关键词搜索股票，支持按代码或名称模糊匹配。
        
        Args:
            keyword (str): 搜索关键词（股票代码或名称的一部分）
        
        Returns:
            pd.DataFrame: 匹配的股票列表
        
        Example:
            >>> df = fetcher.search_stocks('茅台')
            >>> print(df[['code', 'name']])
        """
        try:
            df = self.get_realtime_quotes()
            
            # 按代码或名称进行模糊匹配
            mask = (
                df['code'].str.contains(keyword, case=False, na=False) |
                df['name'].str.contains(keyword, case=False, na=False)
            )
            
            return df[mask]
            
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
