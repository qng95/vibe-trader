from datetime import date, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def fetch_stock_news(symbol: str) -> dict:
    """Fetch the latest news for a specific stock symbol.

    Args:
        symbol (str): The stock ticker symbol of the company, e.g., 'AAPL' for Apple.

    Returns:
        dict: A dictionary containing the status and news summary or error message.
    """
    import finnhub
    finnhub_client = finnhub.Client(api_key="d0oqbahr01qsib2e98qgd0oqbahr01qsib2e98r0")

    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    returned_result=finnhub_client.company_news(symbol, _from=yesterday.strftime("%Y-%m-%d"), to=today.strftime("%Y-%m-%d"))
    top_five_news = returned_result[:5]  # Get the top 5 news articles
    extracted_news = []
    for news in top_five_news:
        extracted_news.append({
            "headline": news['headline'],
            "summary": news['summary'],
            "source": news['source']
        })
    
    return extracted_news

print(fetch_stock_news("AAPL"))


def buy_stock(symbol: str, quantity: float) -> dict:
    """Simulate buying a stock.

    Args:
        symbol (str): The stock ticker symbol of the company.
        quantity (float): The number of shares to buy.

    Returns:
        dict: A dictionary containing the status and confirmation message.
    """
    # Simulate a stock purchase
    trading_client = TradingClient('PKIZP2WBBTT7C0I49WXE', 'PxR7A4qGFfVHCoKtxePrSJucmhtGEpZg32ZzGVH6')
    # preparing orders
    market_order_data = MarketOrderRequest(
        symbol=symbol,
        qty=quantity,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )

    # Market order
    market_order = trading_client.submit_order(
        order_data=market_order_data
    )
    
    return {
        "status": "success",
        "message": f"Successfully bought {quantity} shares of {symbol}.",
        "order_id": market_order.id
    }