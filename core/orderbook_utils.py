#!/usr/bin/env python3
"""
订单簿数据抓取工具函数
用于集成到主监控程序
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# 导入数据模型
from data.models import OrderBook, OrderBookLevel, OrderType

def parse_orderbook_from_page(page) -> Optional[OrderBook]:
    """
    从DrissionPage页面对象中解析订单簿数据

    Args:
        page: DrissionPage的页面对象

    Returns:
        OrderBook: 订单簿对象
    """
    try:
        asks = []  # 卖单 (价格从低到高)
        bids = []  # 买单 (价格从高到低)

        # 抓取卖单 (asks) - 红色区域
        asks_container = page.ele('@data-testid=orderbook-asks')
        if asks_container:
            # 使用正确的语法查找ask元素
            ask_elements = page.eles('@data-testid^ob-ask-')
            print(f"找到 {len(ask_elements)} 个卖单元素")
            for ask_elem in ask_elements:
                level = _parse_orderbook_level(ask_elem, OrderType.ASK)
                if level:
                    asks.append(level)
                    print(f"解析卖单: ${level.price:.1f}")

        # 抓取买单 (bids) - 绿色区域
        bids_container = page.ele('@data-testid=orderbook-bids')
        if bids_container:
            # 使用正确的语法查找bid元素
            bid_elements = page.eles('@data-testid^ob-bid-')
            print(f"找到 {len(bid_elements)} 个买单元素")
            for bid_elem in bid_elements:
                level = _parse_orderbook_level(bid_elem, OrderType.BID)
                if level:
                    bids.append(level)
                    print(f"解析买单: ${level.price:.1f}")

        # 排序
        asks = sorted(asks, key=lambda x: x.price)  # 卖单价格从低到高
        bids = sorted(bids, key=lambda x: x.price, reverse=True)  # 买单价格从高到低

        return OrderBook(
            asks=asks,
            bids=bids,
            timestamp=datetime.now()
        )

    except Exception as e:
        print(f"订单簿解析错误: {e}")
        return None

def _parse_orderbook_level(element, order_type: OrderType) -> Optional[OrderBookLevel]:
    """解析单个订单簿档位"""
    try:
        price_elem = element.ele('@data-testid=price')
        size_elem = element.ele('@data-testid=size')
        total_elem = element.ele('@data-testid=total-size')

        if not (price_elem and size_elem and total_elem):
            return None

        # 清理文本并转换为数字
        price_text = price_elem.text.replace(',', '').strip()
        size_text = size_elem.text.replace(',', '').strip()
        total_text = total_elem.text.replace(',', '').strip()

        price = float(price_text)
        size = float(size_text)
        total_size = float(total_text)

        return OrderBookLevel(
            price=price,
            size=size,
            total_size=total_size,
            order_type=order_type
        )

    except (ValueError, AttributeError) as e:
        return None

def get_best_prices(orderbook: OrderBook) -> Tuple[Optional[float], Optional[float]]:
    """
    获取最佳买卖价格
    
    Returns:
        Tuple[best_bid, best_ask]: 最高买价和最低卖价
    """
    if not orderbook:
        return None, None
    
    best_bid = orderbook.bids[0].price if orderbook.bids else None
    best_ask = orderbook.asks[0].price if orderbook.asks else None
    
    return best_bid, best_ask

def get_market_depth(orderbook: OrderBook, depth_levels: int = 5) -> Dict:
    """
    获取市场深度信息
    
    Args:
        orderbook: 订单簿数据
        depth_levels: 深度档位数量
        
    Returns:
        Dict: 包含买卖深度的字典
    """
    if not orderbook:
        return {'bid_depth': 0, 'ask_depth': 0}
    
    # 计算买单深度 (前N档总量)
    bid_depth = sum(level.size for level in orderbook.bids[:depth_levels])
    
    # 计算卖单深度 (前N档总量)  
    ask_depth = sum(level.size for level in orderbook.asks[:depth_levels])
    
    return {
        'bid_depth': bid_depth,
        'ask_depth': ask_depth,
        'total_depth': bid_depth + ask_depth
    }

def format_orderbook_summary(orderbook: OrderBook) -> str:
    """
    格式化订单簿摘要信息
    
    Returns:
        str: 格式化的摘要字符串
    """
    if not orderbook:
        return "订单簿数据不可用"
    
    summary_parts = []
    
    if orderbook.best_bid and orderbook.best_ask:
        summary_parts.append(f"买一: ${orderbook.best_bid:,.1f}")
        summary_parts.append(f"卖一: ${orderbook.best_ask:,.1f}")
        
        if orderbook.spread:
            summary_parts.append(f"点差: ${orderbook.spread:.1f}")
    
    depth = get_market_depth(orderbook)
    if depth['total_depth'] > 0:
        summary_parts.append(f"深度: {depth['total_depth']:.2f}")
    
    return " | ".join(summary_parts) if summary_parts else "数据解析中..."