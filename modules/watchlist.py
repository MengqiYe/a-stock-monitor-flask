#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自选股票管理模块
================

提供自选股票的存储和管理功能，支持增删查改操作。

数据存储：使用JSON文件存储，路径为 data/watchlist.json
"""

import os
import json
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
WATCHLIST_FILE = os.path.join(DATA_DIR, 'watchlist.json')


class WatchlistManager:
    """自选股票管理器"""
    
    def __init__(self):
        """初始化管理器，确保数据目录和文件存在"""
        self._ensure_data_dir()
        self._ensure_data_file()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
    
    def _ensure_data_file(self):
        """确保数据文件存在"""
        if not os.path.exists(WATCHLIST_FILE):
            self._save_data({
                'stocks': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
    
    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                'stocks': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
    
    def _save_data(self, data: Dict):
        """保存数据"""
        data['updated_at'] = datetime.now().isoformat()
        with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_all(self) -> List[Dict]:
        """
        获取所有自选股票
        
        Returns:
            List[Dict]: 自选股票列表，每项包含 code, name, added_at 等字段
        """
        data = self._load_data()
        return data.get('stocks', [])
    
    def add(self, code: str, name: str = '', shares: int = 0, cost_price: float = 0.0, note: str = '') -> Dict:
        """
        添加自选股票
        
        Args:
            code: 股票代码
            name: 股票名称
            shares: 持仓股数
            cost_price: 成本价
            note: 备注
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        
        # 检查是否已存在
        for stock in stocks:
            if stock['code'] == code:
                return {
                    'success': False,
                    'message': f'股票 {code} 已在自选中'
                }
        
        # 添加新股票
        new_stock = {
            'code': code,
            'name': name,
            'shares': shares,
            'cost_price': cost_price,
            'note': note,
            'added_at': datetime.now().isoformat()
        }
        stocks.append(new_stock)
        data['stocks'] = stocks
        self._save_data(data)
        
        return {
            'success': True,
            'message': f'股票 {code} 添加成功',
            'data': new_stock
        }
    
    def remove(self, code: str) -> Dict:
        """
        移除自选股票
        
        Args:
            code: 股票代码
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        
        # 查找并移除
        original_count = len(stocks)
        stocks = [s for s in stocks if s['code'] != code]
        
        if len(stocks) == original_count:
            return {
                'success': False,
                'message': f'股票 {code} 不在自选中'
            }
        
        data['stocks'] = stocks
        self._save_data(data)
        
        return {
            'success': True,
            'message': f'股票 {code} 已移除'
        }
    
    def update(self, code: str, shares: Optional[int] = None, 
               cost_price: Optional[float] = None, note: Optional[str] = None) -> Dict:
        """
        更新自选股票信息
        
        Args:
            code: 股票代码
            shares: 持仓股数（可选）
            cost_price: 成本价（可选）
            note: 备注（可选）
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        
        # 查找并更新
        for stock in stocks:
            if stock['code'] == code:
                if shares is not None:
                    stock['shares'] = shares
                if cost_price is not None:
                    stock['cost_price'] = cost_price
                if note is not None:
                    stock['note'] = note
                stock['updated_at'] = datetime.now().isoformat()
                
                self._save_data(data)
                return {
                    'success': True,
                    'message': f'股票 {code} 更新成功',
                    'data': stock
                }
        
        return {
            'success': False,
            'message': f'股票 {code} 不在自选中'
        }
    
    def clear(self) -> Dict:
        """
        清空所有自选股票
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        original_count = len(data.get('stocks', []))
        data['stocks'] = []
        self._save_data(data)
        
        return {
            'success': True,
            'message': f'已清空 {original_count} 只自选股票'
        }
    
    def get_count(self) -> int:
        """
        获取自选股票数量
        
        Returns:
            int: 自选股票数量
        """
        return len(self.get_all())


# 创建全局实例
watchlist_manager = WatchlistManager()
