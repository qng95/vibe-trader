from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import matplotlib.pyplot as plt
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus

def preview_and_trade():
    # Request API credentials from user
    api_key = input("Enter your Alpaca API Key: ").strip()
    api_secret = input("Enter your Alpaca API Secret: ").strip()

    # Prompt user for stock symbols (comma separated)
    symbols = input("Enter stock symbols separated by commas (e.g., AAPL,MSFT): ").strip().upper().replace(" ", "").split(',')

    # Prompt user for start and end dates
    start_str = input("Enter start date (YYYY-MM-DD): ").strip()
    end_str = input("Enter end date (YYYY-MM-DD): ").strip()
    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Initialize the data client (no feed argument here)
    data_client = StockHistoricalDataClient(api_key, api_secret)

    # Prepare the request with feed='iex' for free/historical data
    stock_historical_request = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Day,
        start=start_date,
        end=end_date,
        feed='iex'
    )

    try:
        bars = data_client.get_stock_bars(stock_historical_request)
        stock_dataframe = bars.df
        if stock_dataframe.empty:
            print(f"No historical data found for {symbols}.")
            return
        # Plot the closing prices for each symbol
        plt.figure(figsize=(14, 7))
        for symbol in symbols:
            plt.plot(
                stock_dataframe.xs(symbol, level='symbol')['close'],
                label=symbol
            )
        plt.title(f"{', '.join(symbols)} Closing Prices ({start_str} to {end_str})")
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid()
        plt.show()
    except Exception as e:
        print(f"Error fetching or plotting data: {e}")
        return

    # Ask user if they want to place a BUY order
    buy_choice = input("Would you like to place a BUY order for any of these stocks? (yes/no): ").strip().lower()
    if buy_choice != 'yes':
        print("No order placed.")
        return

    # Prompt for which symbol to buy and quantity
    buy_symbol = input(f"Enter the symbol you want to buy from {symbols}: ").strip().upper()
    if buy_symbol not in symbols:
        print(f"{buy_symbol} was not in your original selection.")
        return
    try:
        qty = float(input(f"Enter the quantity of {buy_symbol} you want to buy: "))
    except ValueError:
        print("Invalid quantity. Please enter a numeric value.")
        return

    # Initialize trading client
    trading_client = TradingClient(api_key, api_secret, paper=True)

    # Prepare and submit order
    market_order_info = MarketOrderRequest(
        symbol=buy_symbol,
        qty=qty,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
    try:
        market_order = trading_client.submit_order(order_data=market_order_info)
        print(f"Market order submitted: {market_order}")
    except Exception as e:
        print(f"Error submitting order: {e}")
        return

    # Fetch and print recent orders
    get_orders_request = GetOrdersRequest(
        status=QueryOrderStatus.ALL,
        limit=5
    )
    try:
        orders = trading_client.get_orders(filter=get_orders_request)
        for order in orders:
            print(f"Order ID: {order.id}, Symbol: {order.symbol}, Qty: {order.qty}, Status: {order.status}")
    except Exception as e:
        print(f"Error fetching orders: {e}")

# Call the function
preview_and_trade()
