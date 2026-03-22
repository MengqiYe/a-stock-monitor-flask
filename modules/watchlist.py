#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自选股票管理模块
================

提供自选股票的存储和管理功能，支持增删查改和分组操作。

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

# 默认分组
DEFAULT_GROUPS = [
    {'id': 'default', 'name': '默认分组', 'color': '#1890ff', 'sort': 0},
]


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
                'groups': DEFAULT_GROUPS.copy(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
    
    def _load_data(self) -> Dict:
        """加载数据"""
        try:
            with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保groups存在
                if 'groups' not in data:
                    data['groups'] = DEFAULT_GROUPS.copy()
                return data
        except Exception:
            return {
                'stocks': [],
                'groups': DEFAULT_GROUPS.copy(),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
    
    def _save_data(self, data: Dict):
        """保存数据"""
        data['updated_at'] = datetime.now().isoformat()
        with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ==================== 分组管理 ====================
    
    def get_groups(self) -> List[Dict]:
        """
        获取所有分组
        
        Returns:
            List[Dict]: 分组列表
        """
        data = self._load_data()
        return data.get('groups', DEFAULT_GROUPS.copy())
    
    def add_group(self, name: str, color: str = '#1890ff') -> Dict:
        """
        添加分组
        
        Args:
            name: 分组名称
            color: 分组颜色
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        groups = data.get('groups', [])
        
        # 生成唯一ID
        group_id = f"group_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 检查名称是否重复
        for g in groups:
            if g['name'] == name:
                return {
                    'success': False,
                    'message': f'分组名称 "{name}" 已存在'
                }
        
        new_group = {
            'id': group_id,
            'name': name,
            'color': color,
            'sort': len(groups)
        }
        groups.append(new_group)
        data['groups'] = groups
        self._save_data(data)
        
        return {
            'success': True,
            'message': f'分组 "{name}" 添加成功',
            'data': new_group
        }
    
    def update_group(self, group_id: str, name: Optional[str] = None, 
                     color: Optional[str] = None) -> Dict:
        """
        更新分组信息
        
        Args:
            group_id: 分组ID
            name: 分组名称（可选）
            color: 分组颜色（可选）
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        groups = data.get('groups', [])
        
        for group in groups:
            if group['id'] == group_id:
                if name is not None:
                    # 检查名称是否重复
                    for g in groups:
                        if g['id'] != group_id and g['name'] == name:
                            return {
                                'success': False,
                                'message': f'分组名称 "{name}" 已存在'
                            }
                    group['name'] = name
                if color is not None:
                    group['color'] = color
                self._save_data(data)
                return {
                    'success': True,
                    'message': '分组更新成功',
                    'data': group
                }
        
        return {
            'success': False,
            'message': '分组不存在'
        }
    
    def delete_group(self, group_id: str) -> Dict:
        """
        删除分组
        
        Args:
            group_id: 分组ID
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        groups = data.get('groups', [])
        stocks = data.get('stocks', [])
        
        # 不允许删除默认分组
        if group_id == 'default':
            return {
                'success': False,
                'message': '默认分组不能删除'
            }
        
        # 查找分组
        group_name = None
        original_count = len(groups)
        groups = [g for g in groups if g['id'] != group_id]
        
        if len(groups) == original_count:
            return {
                'success': False,
                'message': '分组不存在'
            }
        
        # 将该分组的股票移到默认分组
        for stock in stocks:
            if stock.get('group_id') == group_id:
                stock['group_id'] = 'default'
        
        data['groups'] = groups
        data['stocks'] = stocks
        self._save_data(data)
        
        return {
            'success': True,
            'message': '分组已删除，股票已移至默认分组'
        }
    
    def get_group_stats(self) -> Dict:
        """
        获取分组统计信息
        
        Returns:
            Dict: 分组统计，包含每个分组的股票数量
        """
        data = self._load_data()
        groups = data.get('groups', [])
        stocks = data.get('stocks', [])
        
        stats = {}
        for group in groups:
            stats[group['id']] = {
                'name': group['name'],
                'color': group['color'],
                'count': 0
            }
        
        for stock in stocks:
            group_id = stock.get('group_id', 'default')
            if group_id in stats:
                stats[group_id]['count'] += 1
            elif 'default' in stats:
                stats['default']['count'] += 1
        
        return stats
    
    # ==================== 股票管理 ====================
    
    def get_all(self, group_id: Optional[str] = None) -> List[Dict]:
        """
        获取所有自选股票
        
        Args:
            group_id: 分组ID（可选，指定则只返回该分组的股票）
        
        Returns:
            List[Dict]: 自选股票列表
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        
        if group_id:
            stocks = [s for s in stocks if s.get('group_id', 'default') == group_id]
        
        return stocks
    
    def add(self, code: str, name: str = '', shares: int = 0, 
            cost_price: float = 0.0, note: str = '', group_id: str = 'default') -> Dict:
        """
        添加自选股票
        
        Args:
            code: 股票代码
            name: 股票名称
            shares: 持仓股数
            cost_price: 成本价
            note: 备注
            group_id: 分组ID
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        groups = data.get('groups', [])
        
        # 检查分组是否存在
        group_exists = any(g['id'] == group_id for g in groups)
        if not group_exists:
            group_id = 'default'
        
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
            'group_id': group_id,
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
               cost_price: Optional[float] = None, note: Optional[str] = None,
               group_id: Optional[str] = None) -> Dict:
        """
        更新自选股票信息
        
        Args:
            code: 股票代码
            shares: 持仓股数（可选）
            cost_price: 成本价（可选）
            note: 备注（可选）
            group_id: 分组ID（可选）
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        groups = data.get('groups', [])
        
        for stock in stocks:
            if stock['code'] == code:
                if shares is not None:
                    stock['shares'] = shares
                if cost_price is not None:
                    stock['cost_price'] = cost_price
                if note is not None:
                    stock['note'] = note
                if group_id is not None:
                    # 检查分组是否存在
                    if any(g['id'] == group_id for g in groups):
                        stock['group_id'] = group_id
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
    
    def move_to_group(self, codes: List[str], group_id: str) -> Dict:
        """
        批量移动股票到指定分组
        
        Args:
            codes: 股票代码列表
            group_id: 目标分组ID
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        stocks = data.get('stocks', [])
        groups = data.get('groups', [])
        
        # 检查分组是否存在
        if not any(g['id'] == group_id for g in groups):
            return {
                'success': False,
                'message': '目标分组不存在'
            }
        
        moved_count = 0
        for stock in stocks:
            if stock['code'] in codes:
                stock['group_id'] = group_id
                moved_count += 1
        
        self._save_data(data)
        
        return {
            'success': True,
            'message': f'已移动 {moved_count} 只股票'
        }
    
    def clear(self, group_id: Optional[str] = None) -> Dict:
        """
        清空自选股票
        
        Args:
            group_id: 分组ID（可选，指定则只清空该分组）
        
        Returns:
            Dict: 操作结果
        """
        data = self._load_data()
        
        if group_id:
            stocks = data.get('stocks', [])
            original_count = len(stocks)
            stocks = [s for s in stocks if s.get('group_id', 'default') != group_id]
            data['stocks'] = stocks
            self._save_data(data)
            return {
                'success': True,
                'message': f'已清空 {original_count - len(stocks)} 只股票'
            }
        else:
            original_count = len(data.get('stocks', []))
            data['stocks'] = []
            self._save_data(data)
            return {
                'success': True,
                'message': f'已清空 {original_count} 只自选股票'
            }
    
    def get_count(self, group_id: Optional[str] = None) -> int:
        """
        获取自选股票数量
        
        Args:
            group_id: 分组ID（可选）
        
        Returns:
            int: 自选股票数量
        """
        return len(self.get_all(group_id))


# 创建全局实例
watchlist_manager = WatchlistManager()
