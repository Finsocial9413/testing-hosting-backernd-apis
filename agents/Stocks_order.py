from typing import Dict, Any, Optional

def place_stock_order(symbol: str, quantity: float = 1, order_type: str = "market", 
                     side: str = "buy", limit_price: float = None, stop_price: float = None, 
                     time_in_force: str = "Day", account_id: str = None) -> str:
    """
    🎯 MAIN STOCK ORDER TOOL - Place any type of stock order
    
    Args:
        symbol: Stock symbol or company name (e.g., "AAPL", "Apple", "TSLA", "Tesla")
        quantity: Number of shares (default: 1)
        order_type: "market", "limit", "stop", "stop_limit" (default: "market")
        side: "buy" or "sell" (default: "buy")
        limit_price: Limit price for limit orders
        stop_price: Stop price for stop orders
        time_in_force: Order duration (default: "Day")
        account_id: Account ID for sell orders
    
    Returns:
        Order confirmation message
    """
    symbol = _normalize_symbol(symbol)
    
    confirmation_msg = f"""
🎉 **Order Placed Successfully!** ✅

📋 **Order Details:**
• Order Type: {side.title()} {order_type.title()} Order
• Symbol: {symbol.upper()}
• Quantity: {quantity} shares
• Side: {side.upper()}
• Time in Force: {time_in_force}
"""
    
    if order_type.lower() == "market":
        confirmation_msg += "• Execution: At Market Price\n"
    elif limit_price:
        confirmation_msg += f"• Limit Price: ${limit_price}\n"
    if stop_price:
        confirmation_msg += f"• Stop Price: ${stop_price}\n"
    if side.lower() == "sell" and account_id:
        confirmation_msg += f"• Account ID: {account_id}\n"
    
    confirmation_msg += "\n⚠️ **Note:** This is a simulation. No actual trade was executed."
    
    return confirmation_msg

def _normalize_symbol(symbol: str) -> str:
    """Convert company names to stock symbols"""
    symbol_map = {
        "apple": "AAPL", "tesla": "TSLA", "microsoft": "MSFT",
        "google": "GOOGL", "amazon": "AMZN", "meta": "META",
        "facebook": "META", "nvidia": "NVDA", "netflix": "NFLX"
    }
    return symbol_map.get(symbol.lower(), symbol)

class StockOrderTools:
    """Tools for creating and validating different types of stock trading orders"""
    
    def __init__(self):
        self.order_types = {
            'buy_market': ['symbol', 'unit', 'time_in_force'],
            'sell_market': ['account_id', 'symbol', 'unit'],
            'buy_limit': ['symbol', 'unit', 'limit_price', 'stop_price', 'time_in_force'],
            'sell_limit': ['symbol', 'unit', 'limit_price', 'stop_price', 'time_in_force'],
        }
        
        # Register the function as a tool
        self.place_stock_order = place_stock_order