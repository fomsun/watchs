#!/usr/bin/env python3
"""
数据模型定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class OrderType(Enum):
    """订单类型枚举"""
    BID = "bid"  # 买单
    ASK = "ask"  # 卖单


@dataclass
class OrderBookLevel:
    """订单簿档位"""
    price: float
    size: float
    total_size: float = 0.0
    order_type: OrderType = OrderType.BID


@dataclass
class OrderBook:
    """订单簿数据"""
    asks: List[OrderBookLevel] = field(default_factory=list)  # 卖单列表
    bids: List[OrderBookLevel] = field(default_factory=list)  # 买单列表
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def best_ask(self) -> Optional[float]:
        """最低卖价"""
        return self.asks[0].price if self.asks else None

    @property
    def best_bid(self) -> Optional[float]:
        """最高买价"""
        return self.bids[0].price if self.bids else None

    @property
    def mid_price(self) -> Optional[float]:
        """中间价"""
        if self.best_ask and self.best_bid:
            return (self.best_ask + self.best_bid) / 2
        return None

    @property
    def spread(self) -> Optional[float]:
        """价差"""
        if self.best_ask and self.best_bid:
            return self.best_ask - self.best_bid
        return None

    @property
    def spread_percent(self) -> Optional[float]:
        """价差百分比"""
        if self.spread and self.mid_price and self.mid_price > 0:
            return (self.spread / self.mid_price) * 100
        return None


@dataclass
class LighterData:
    """Lighter数据"""
    orderbook: Optional[OrderBook] = None
    timestamp: datetime = field(default_factory=datetime.now)
    connected: bool = False


@dataclass
class BinanceData:
    """币安数据"""
    symbol: str = "BTCUSDC"
    price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BackpackData:
    """Backpack数据"""
    symbol: str = "BTC_USDC_PERP"
    price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BTCPriceData:
    """BTC价格数据汇总"""
    binance: Optional[BinanceData] = None
    backpack: Optional[BackpackData] = None
    lighter: Optional[LighterData] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "timestamp": self.timestamp.isoformat(),
            "prices": {}
        }

        if self.binance:
            result["prices"]["binance"] = {
                "symbol": self.binance.symbol,
                "price": self.binance.price,
                "timestamp": self.binance.timestamp.isoformat()
            }

        if self.backpack:
            result["prices"]["backpack"] = {
                "symbol": self.backpack.symbol,
                "price": self.backpack.price,
                "timestamp": self.backpack.timestamp.isoformat()
            }

        if self.lighter and self.lighter.orderbook:
            result["prices"]["lighter"] = {
                "best_bid": self.lighter.orderbook.best_bid,
                "best_ask": self.lighter.orderbook.best_ask,
                "mid_price": self.lighter.orderbook.mid_price,
                "timestamp": self.lighter.timestamp.isoformat(),
                "connected": self.lighter.connected
            }

        return result