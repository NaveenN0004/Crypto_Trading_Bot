import time
import hmac
import hashlib
import requests
import json
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional, List
from config.settings import API_KEY, API_SECRET, DEBUG_MODE

BASE_URL = "https://api.coindcx.com"

@dataclass
class Order:
    
    # data class representing an order
    
    order_id: str
    market: str       # trading pair
    side: str         # "buy" or "sell"
    order_type: str
    price_per_unit: float
    total_quantity: float
    timestamp: int
    status: str
    fee: float = 0.0
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    avg_price: float = 0.0
    stop_price: Optional[float] = None
    take_profit: Optional[float] = None

class OrderManagementSystem:
    
    # manages order placement, cancellation, and status retrieval via CoinDCX API
    
    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.active_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []

    def _generate_signature(self, payload: Dict) -> str:
        # enerate HMAC signature for a given payload

        payload_str = str(payload).replace("'", '"')
        return hmac.new(
            API_SECRET.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def _make_authenticated_request(self, endpoint: str, payload: Dict, method: str = "POST") -> Optional[Dict]:
        # make an authenticated request to the specified endpoint
        
        url = f"{self.base_url}{endpoint}"
        if 'timestamp' not in payload:
            payload['timestamp'] = int(time.time() * 1000)
        signature = self._generate_signature(payload)
        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": API_KEY,
            "X-AUTH-SIGNATURE": signature
        }
        if DEBUG_MODE:
            print(f"\n🔍 Making {method} request to {endpoint}")
            print(f"Payload: {payload}")
            print(f"Headers: {headers}")
        try:
            response = (requests.post(url, headers=headers, json=payload)
                        if method == "POST"
                        else requests.get(url, headers=headers, json=payload))
            if response.status_code in (200, 201):
                if DEBUG_MODE:
                    print(f"✅ API Request Successful: {response.status_code}")
                    print(f"Response: {response.json()}")
                return response.json()
            else:
                if DEBUG_MODE:
                    print(f"❌ API Request Failed: {response.status_code}")
                    print(f"Response: {response.text}")
                return None
        except Exception as e:
            if DEBUG_MODE:
                print(f"❌ Request Error: {e}")
            return None

    def _parse_order_response(self, response: Dict, payload: Dict) -> Optional[Order]:        
        # parse the API response which may contain the order details under the key "orders"
        
        order_data = None
        if "orders" in response and isinstance(response["orders"], list) and response["orders"]:
            order_data = response["orders"][0]
        else:
            # try to get the order directly from the response
            order_data = response
        
        order_id = order_data.get("id") or order_data.get("orderId")
        status = order_data.get("status", "").upper()

        if order_id or status in ("SUCCESS", "OPEN"):
            if not order_id:
                order_id = f"order_{payload['timestamp']}"
            return Order(
                order_id=order_id,
                market=payload.get("market"),
                side=payload.get("side"),
                order_type=payload.get("order_type"),
                price_per_unit=float(order_data.get("price_per_unit", 0)),
                total_quantity=payload.get("total_quantity"),
                status="OPEN",
                timestamp=payload["timestamp"],
                fee=float(order_data.get("fee", 0)),
                filled_quantity=float(order_data.get("filled_quantity", 0)),
                remaining_quantity=payload.get("total_quantity"),
                stop_price=payload.get("stop_loss"),
                take_profit=payload.get("take_profit")
            )
        return None

    def place_market_order(self, market: str, side: str, total_quantity: float,
                           stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Optional[Order]:
        # place a market order and return the created Order object
        
        payload = {
            "market": market,
            "side": side,
            "order_type": "market_order",
            "total_quantity": total_quantity
        }
        if stop_loss:
            payload["stop_loss"] = stop_loss
        if take_profit:
            payload["take_profit"] = take_profit

        response = self._make_authenticated_request("/exchange/v1/orders/create", payload)
        if response:
            order = self._parse_order_response(response, payload)
            if order:
                self.active_orders[order.order_id] = order
                return order
        return None

    def place_limit_order(self, market: str, side: str, price_per_unit: float,
                          total_quantity: float, stop_loss: Optional[float] = None,
                          take_profit: Optional[float] = None) -> Optional[Order]:
        # place a limit order and return the created Order object

        payload = {
            "market": market,
            "side": side,
            "order_type": "limit_order",
            "price_per_unit": price_per_unit,
            "total_quantity": total_quantity
        }
        if stop_loss:
            payload["stop_loss"] = stop_loss
        if take_profit:
            payload["take_profit"] = take_profit

        response = self._make_authenticated_request("/exchange/v1/orders/create", payload)
        if response:
            order = self._parse_order_response(response, payload)
            if order:
                self.active_orders[order.order_id] = order
                return order
        return None

    def cancel_order(self, order_id: str) -> bool:
        # cancel an on the basis order_id

        payload = {
            "order_id": order_id,
            "timestamp": int(time.time() * 1000)
        }
        response = self._make_authenticated_request("/exchange/v1/orders/cancel", payload)
        if response and response.get("status") == "SUCCESS":
            if order_id in self.active_orders:
                order = self.active_orders.pop(order_id)
                order.status = "CANCELLED"
                self.order_history.append(order)
            return True
        return False

    def get_order_status(self, order_id: str) -> Optional[Order]:
        # retrieve and update the status of an order
        
        payload = {
            "order_id": order_id,
            "timestamp": int(time.time() * 1000)
        }
        response = self._make_authenticated_request("/exchange/v1/orders/status", payload, method="GET")
        if response:
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                order.status = response.get("status", "UNKNOWN")
                order.filled_quantity = float(response.get("filled_quantity", 0))
                order.remaining_quantity = float(response.get("remaining_quantity", 0))
                order.avg_price = float(response.get("average_price", 0))
                order.fee = float(response.get("fee", 0))
                if order.status in ("COMPLETED", "CANCELLED"):
                    self.active_orders.pop(order_id)
                    self.order_history.append(order)
                return order
        return None

    def get_active_orders(self, market: Optional[str] = None) -> List[Order]:
        # retrieve all active orders, optionally filtering by market
        
        payload = {"timestamp": int(time.time() * 1000)}
        if market:
            payload["market"] = market
        response = self._make_authenticated_request("/exchange/v1/orders/active_orders", payload, method="GET")
        active_orders: List[Order] = []
        if response:
            for order_data in response:
                order_id = order_data.get("order_id") or order_data.get("orderId")
                order = Order(
                    order_id=order_id,
                    market=order_data.get("market"),
                    side=order_data.get("side"),
                    order_type=order_data.get("order_type"),
                    price_per_unit=float(order_data.get("price_per_unit", 0)),
                    total_quantity=float(order_data.get("total_quantity", 0)),
                    status=order_data.get("status", "UNKNOWN"),
                    timestamp=order_data.get("timestamp", 0),
                    filled_quantity=float(order_data.get("filled_quantity", 0)),
                    remaining_quantity=float(order_data.get("remaining_quantity", 0)),
                    avg_price=float(order_data.get("average_price", 0)),
                    fee=float(order_data.get("fee", 0))
                )
                self.active_orders[order_id] = order
                active_orders.append(order)
            return active_orders
        return []

    def get_order_history(self, market: Optional[str] = None) -> List[Order]:
        # retrieve the order history for a given market (if provided)

        payload = {"timestamp": int(time.time() * 1000)}
        if market:
            payload["market"] = market
        response = self._make_authenticated_request("/exchange/v1/orders/trade_history", payload, method="GET")
        order_history: List[Order] = []
        if response:
            for trade in response:
                order = Order(
                    order_id=trade.get("order_id") or trade.get("orderId"),
                    market=trade.get("market"),
                    side=trade.get("side"),
                    order_type=trade.get("order_type"),
                    price_per_unit=float(trade.get("price_per_unit", 0)),
                    total_quantity=float(trade.get("quantity", 0)),
                    status="COMPLETED",
                    timestamp=trade.get("timestamp", 0),
                    filled_quantity=float(trade.get("quantity", 0)),
                    remaining_quantity=0,
                    avg_price=float(trade.get("price_per_unit", 0)),
                    fee=float(trade.get("fee", 0))
                )
                order_history.append(order)
            return order_history
        return []
