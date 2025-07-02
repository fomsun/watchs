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
        print(f"🔍 开始解析订单簿数据...")
        asks = []  # 卖单 (价格从低到高)
        bids = []  # 买单 (价格从高到低)

        # 抓取卖单 (asks) - 红色区域
        print(f"🔍 查找卖单容器...")
        asks_container = page.ele('@data-testid=orderbook-asks')
        if asks_container:
            print(f"✅ 找到卖单容器")
            print(f"   容器HTML: {asks_container.html[:200]}...")

            # 尝试多种选择器查找ask元素
            ask_selectors = [
                '@data-testid^ob-ask-',
                '@data-testid*ask',
                '.ask',
                '.sell',
                'tr',
                'div'
            ]

            ask_elements = None
            for selector in ask_selectors:
                try:
                    elements = page.eles(selector)
                    if elements:
                        print(f"   使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        ask_elements = elements
                        break
                except Exception as e:
                    print(f"   选择器 '{selector}' 失败: {e}")

            if ask_elements:
                print(f"找到 {len(ask_elements)} 个卖单元素")
                for i, ask_elem in enumerate(ask_elements[:10]):  # 只处理前10个
                    try:
                        print(f"   处理卖单元素 {i+1}: {ask_elem.html[:100]}...")
                        level = _parse_orderbook_level(ask_elem, OrderType.ASK)
                        if level:
                            asks.append(level)
                            print(f"   ✅ 解析卖单: ${level.price:.1f}")
                        else:
                            print(f"   ❌ 解析卖单失败")
                    except Exception as e:
                        print(f"   ❌ 处理卖单元素出错: {e}")
            else:
                print(f"❌ 未找到卖单元素")
        else:
            print(f"❌ 未找到卖单容器")

        # 抓取买单 (bids) - 绿色区域
        print(f"🔍 查找买单容器...")
        bids_container = page.ele('@data-testid=orderbook-bids')
        if bids_container:
            print(f"✅ 找到买单容器")
            print(f"   容器HTML: {bids_container.html[:200]}...")

            # 尝试多种选择器查找bid元素
            bid_selectors = [
                '@data-testid^ob-bid-',
                '@data-testid*bid',
                '.bid',
                '.buy',
                'tr',
                'div'
            ]

            bid_elements = None
            for selector in bid_selectors:
                try:
                    elements = page.eles(selector)
                    if elements:
                        print(f"   使用选择器 '{selector}' 找到 {len(elements)} 个元素")
                        bid_elements = elements
                        break
                except Exception as e:
                    print(f"   选择器 '{selector}' 失败: {e}")

            if bid_elements:
                print(f"找到 {len(bid_elements)} 个买单元素")
                for i, bid_elem in enumerate(bid_elements[:10]):  # 只处理前10个
                    try:
                        print(f"   处理买单元素 {i+1}: {bid_elem.html[:100]}...")
                        level = _parse_orderbook_level(bid_elem, OrderType.BID)
                        if level:
                            bids.append(level)
                            print(f"   ✅ 解析买单: ${level.price:.1f}")
                        else:
                            print(f"   ❌ 解析买单失败")
                    except Exception as e:
                        print(f"   ❌ 处理买单元素出错: {e}")
            else:
                print(f"❌ 未找到买单元素")
        else:
            print(f"❌ 未找到买单容器")

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
        print(f"      🔍 解析订单档位 ({order_type.value}):")
        print(f"         元素HTML: {element.html[:150]}...")

        # 尝试多种选择器查找价格、数量、总量
        price_selectors = ['@data-testid=price', '.price', 'span', 'div']
        size_selectors = ['@data-testid=size', '.size', '.amount', 'span', 'div']
        total_selectors = ['@data-testid=total-size', '.total', '.total-size', 'span', 'div']

        price_elem = None
        size_elem = None
        total_elem = None

        # 查找价格元素
        for selector in price_selectors:
            try:
                elem = element.ele(selector)
                if elem and elem.text.strip():
                    price_elem = elem
                    print(f"         ✅ 价格元素 (选择器: {selector}): {elem.text}")
                    break
            except:
                continue

        # 查找数量元素
        for selector in size_selectors:
            try:
                elem = element.ele(selector)
                if elem and elem.text.strip() and elem != price_elem:
                    size_elem = elem
                    print(f"         ✅ 数量元素 (选择器: {selector}): {elem.text}")
                    break
            except:
                continue

        # 查找总量元素
        for selector in total_selectors:
            try:
                elem = element.ele(selector)
                if elem and elem.text.strip() and elem != price_elem and elem != size_elem:
                    total_elem = elem
                    print(f"         ✅ 总量元素 (选择器: {selector}): {elem.text}")
                    break
            except:
                continue

        # 如果没有找到所有必需元素，尝试从文本中提取数字
        if not (price_elem and size_elem):
            print(f"         ⚠️  未找到所有必需元素，尝试从文本提取数字")
            text_content = element.text
            print(f"         文本内容: {text_content}")

            # 使用正则表达式提取数字
            import re
            numbers = re.findall(r'[\d,]+\.?\d*', text_content)
            print(f"         提取的数字: {numbers}")

            if len(numbers) >= 2:
                try:
                    price = float(numbers[0].replace(',', ''))
                    size = float(numbers[1].replace(',', ''))
                    total_size = float(numbers[2].replace(',', '')) if len(numbers) > 2 else size

                    print(f"         ✅ 从文本解析: 价格={price}, 数量={size}, 总量={total_size}")

                    return OrderBookLevel(
                        price=price,
                        size=size,
                        total_size=total_size,
                        order_type=order_type
                    )
                except Exception as e:
                    print(f"         ❌ 文本解析失败: {e}")
                    return None
            else:
                print(f"         ❌ 文本中数字不足")
                return None

        if not (price_elem and size_elem):
            print(f"         ❌ 缺少必需元素: price={price_elem is not None}, size={size_elem is not None}")
            return None

        # 清理文本并转换为数字
        price_text = price_elem.text.replace(',', '').strip()
        size_text = size_elem.text.replace(',', '').strip()
        total_text = total_elem.text.replace(',', '').strip() if total_elem else size_text

        print(f"         文本值: 价格='{price_text}', 数量='{size_text}', 总量='{total_text}'")

        price = float(price_text)
        size = float(size_text)
        total_size = float(total_text)

        print(f"         ✅ 解析成功: 价格={price}, 数量={size}, 总量={total_size}")

        return OrderBookLevel(
            price=price,
            size=size,
            total_size=total_size,
            order_type=order_type
        )

    except (ValueError, AttributeError) as e:
        print(f"         ❌ 解析档位失败: {e}")
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