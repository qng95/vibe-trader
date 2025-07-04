"""
Vibe Trader Agent Tools
This module provides tools for interacting with the Alpaca API using alpaca-py library.
https://alpaca.markets/sdks/python/

All functions in this module should return with some natural language description, because these functions is used by the AI agent (LLM).

All functions in this module will have parameter tool_context: ToolContext | None = None which is used to pass the tool context to the function by Google ADK.
"""
import asyncio
import json
import os
import datetime as dt
import logging
from typing import Dict, Any, List

from dotenv import load_dotenv
from google.adk.tools import FunctionTool, ToolContext

from alpaca.data import (
    NewsClient,  # Import Alpaca API clients for news. These are wrappers around the Alpaca REST API. https://docs.alpaca.markets/docs/getting-started
    NewsRequest,  # Import Alpaca data requests for news data. These are wrappers around request parameters for the Alpaca REST API.
    CryptoHistoricalDataClient,  # Import Alpaca data clients for crypto historical data. These are wrappers around the Alpaca REST API for crypto data.
    CryptoBarsRequest,  # Import Alpaca data requests for crypto bars data. These are wrappers around request parameters for the Alpaca REST API.
    StockHistoricalDataClient,  # Import Alpaca data clients for stock historical data. These are wrappers around the Alpaca REST API for stock data.
    StockBarsRequest,  # Import Alpaca data requests for stock bars data. These are wrappers around request parameters for the Alpaca REST API.
    TimeFrame,
    TimeFrameUnit,
    DataFeed,  # Import Alpaca data enums for time frames. These are used to specify the time frame for historical data requests.
)

# Import Alpaca trading clients for executing trades, managing orders, and handling market data. This is a wrapper around the Alpaca REST API for trading operations.
# Import Alpaca trading requests for placing different types of orders. These are wrappers around request parameters for the Alpaca REST API.
from alpaca.trading import (
    TradingClient,
    GetAssetsRequest,
    GetOrdersRequest,
    MarketOrderRequest,
    QueryOrderStatus,
)

# Import Alpaca trading enums for order side and time in force. These are used to specify order types and conditions.
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, AssetStatus, OrderType

# Set up a logger for the module to log messages, errors, and debug information to console (termininal) for debuging reason.
logger = logging.getLogger(__name__)

# load environment variables from .env file for Alpaca API keys
load_dotenv()

# Now we can access the Alpaca API keys from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
PAPE_TRADING = os.getenv("ALPACA_PAPER", "True").lower() in (
    "true", "1")  # Check if paper trading is enabled, Paper trading is used for testing purposes
SAVE_CHART_ARTIFACT = os.getenv("SAVE_CHART_ARTIFACT", "False").lower() in (
    "true",
    "1")  # Check if chart artifacts should be saved, this is used for testing purposes to save chart images to disk

if SAVE_CHART_ARTIFACT:
    # If chart artifacts should be saved, we import the Plotly library for creating charts.
    import plotly.express as px
    import plotly.graph_objects as go
    # Import necessary types for artifacts type handling.
    import google.genai.types as types

# Initialize Alpaca Trading Clients with API keys
trading_client = TradingClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    paper=PAPE_TRADING,  # Use paper trading for testing
    raw_data=True  # Use raw data to get data as python dictionary like json object, it is easier to work with for AI
)

# Initialize the Alpaca News Client with API keys.
news_client = NewsClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    raw_data=True
    # raw_data=True to get raw news data as python dictionary like json object, it is easier to work with.
)

# Initialize the Alpaca Crypto Historical Data Client with API keys.
crypto_historical_data_client = CryptoHistoricalDataClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    raw_data=True  # Use raw data to get data as python dictionary like json object, it is easier to work with for AI
)

# Initialize the Alpaca Stock Historical Data Client with API keys.
stock_historical_data_client = StockHistoricalDataClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    raw_data=True  # Use raw data to get data as python dictionary like json object, it is easier to work with for AI
)


# Function to place a market order for a specific stock or crypto symbol.
# Type annotations are used to specify the expected types of parameters and return values.
async def fetch_today_news_for_symbol(symbol: str, tool_context: ToolContext | None = None) -> dict:
    """Fetch the latest news for a specific stock or crypto symbol from Alpaca.
    Args:
        symbol (str): The stock or crypto ticker symbol, e.g., 'AAPL' for Apple or 'BTC/USD' for Bitcoin.
    Returns:
        dict: A dictionary containing the status and news summary or error message.
        If successful, it returns a list of news articles with their headlines, summaries, and sources.
        If an error occurs, it returns an error message.
    """
    try:
        # Get today's date in UTC with time set to 00:00:00
        today_utc_00_00: dt.datetime = dt.datetime.now(dt.UTC).replace(
            hour=0, minute=0, second=0, microsecond=0)

        # Get today's date in UTC with time set to 23:59:59
        today_utc_23_59: dt.datetime = dt.datetime.now(dt.UTC).replace(
            hour=23, minute=59, second=59, microsecond=999999)

        news_request = NewsRequest(
            start=today_utc_00_00,  # Start date for news articles, set to today's date at 00:00:00 UTC
            end=today_utc_23_59,  # End date for news articles, set to today's date at 23:59:59 UTC
            sort="desc",  # Sort news articles in descending order by date, so the latest articles come first
            symbols=symbol,  # Specify the symbol for which to fetch news
            limit=10,  # Limit the number of news articles to fetch, only the latest 10 articles
        )
        news: Dict[str, Any] = news_client.get_news(
            request_params=news_request)  # now call the Alpaca News API to fetch news articles
        """
        Example of the news response:
        {
          "news": [
            {
              "author": "Aniket Verma",
              "content": "",
              "created_at": "2025-07-01T08:19:19Z",
              "headline": "Anthony Pompliano Says Bitcoin To Reach 'A Gazillion' Driven By Massive Money Printing In A Heated Economy",
              "id": 46188791,
              "images": [
                {
                  "size": "large",
                  "url": "https://cdn.benzinga.com/files/imagecache/2048x1536xUP/images/story/2025/07/01/Golden-Ray-Of-Light-Illuminate-A-Bitcoin.jpeg"
                },
                {
                  "size": "small",
                  "url": "https://cdn.benzinga.com/files/imagecache/1024x768xUP/images/story/2025/07/01/Golden-Ray-Of-Light-Illuminate-A-Bitcoin.jpeg"
                },
                {
                  "size": "thumb",
                  "url": "https://cdn.benzinga.com/files/imagecache/250x187xUP/images/story/2025/07/01/Golden-Ray-Of-Light-Illuminate-A-Bitcoin.jpeg"
                }
              ],
              "source": "benzinga",
              "summary": "Entrepreneur and cryptocurrency market commentator Anthony Pompliano projected Bitcoin (CRYPTO: BTC) to soar to a gazillion Monday, driven by massive money printing in a heated economy.",
              "symbols": [
                "BTCUSD"
              ],
              "updated_at": "2025-07-01T08:19:20Z",
              "url": "https://www.benzinga.com/crypto/cryptocurrency/25/07/46188791/anthony-pompliano-says-bitcoin-to-reach-a-gazillion-driven-by-massive-money-printing-in-a-heated-economy"
            }
          ],
          "next_page_token": "MTc1MTM1Nzk2MDAwMDAwMDAwMHw0NjE4ODc5MQ=="
        }
        """

        # Extract relevant information from the news articles
        news: List[Dict[str, Any]] = news["news"]  # Extract the list of news articles from the response
        if not news:
            # If no news articles are found, return an error message.
            return {"status": "error",
                    "message": f"There is now news found for symbol {symbol}. May be it is an invalid symbol {symbol}. Please check again."}

        # Create a summary of the news articles with relevant fields
        news_summary: List[Dict[str, Any]] = []
        for article in news:
            news_summary.append({
                "headline": article.get("headline", ""),
                "summary": article.get("summary", ""),
                "source": article.get("source", ""),
                "created_at": article.get("created_at", ""),
            })

        if not news_summary:
            return {"status": "error",
                    "news": f"There is now news found for symbol {symbol}. May be it is an invalid symbol {symbol}. Please check again."}

        return {"status": "success", "news": news_summary}

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_supported_crypto_symbols(tool_context: ToolContext | None = None) -> dict:
    """Get a list of all supported crypto symbols from Alpaca.
    This function fetches all active crypto assets from Alpaca and returns their symbols.

    Returns:
        List[str]: A list of active crypto symbols supported by Alpaca.
        Example: ['BTC/USD', 'ETH/USD', 'BTC/ETH', ...]
    """

    try:
        get_assets_request: GetAssetsRequest = GetAssetsRequest(
            asset_class=AssetClass.CRYPTO,
            status=AssetStatus.ACTIVE
        )
        assets = trading_client.get_all_assets(filter=get_assets_request)
        return {"status": "success",
                "available_crypto_symbols": [asset["symbol"] for asset in assets if "symbol" in asset]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# Function to place a market order for a specific stock or crypto symbol.
# This function is not intended to be used directly, but rather as a helper function for the public API functions.
async def _place_market_order(symbol: str, quantity: float, side: str,
                              time_in_force: TimeInForce, tool_context: ToolContext | None = None) -> dict:
    # first validate the side input parameters
    if side.lower() not in ["buy", "sell"]:
        return {"status": "error", "message": "Invalid order side. Use 'buy' or 'sell'."}

    try:
        # Create a market order request with the specified parameters
        market_order_request = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            type=OrderType.MARKET,
            time_in_force=time_in_force  # Order is valid for the day
        )

        # Place the market order using the trading client
        order = trading_client.submit_order(
            order_data=market_order_request)

        """
        Example of the order response:
        {
            "id": "462076e1-3dfe-407f-809f-9f8266a38d8f",
            "client_order_id": "75d1a291-57f8-41ab-907a-ad0241ea8ca7",
            "created_at": "2025-07-01T13:15:19.895354426Z",
            "updated_at": "2025-07-01T13:15:19.897002416Z",
            "submitted_at": "2025-07-01T13:15:19.895354426Z",
            "filled_at": null,
            "expired_at": null,
            "canceled_at": null,
            "failed_at": null,
            "replaced_at": null,
            "replaced_by": null,
            "replaces": null,
            "asset_id": "276e2673-764b-4ab6-a611-caf665ca6340",
            "symbol": "BTC/USD",
            "asset_class": "crypto",
            "notional": null,
            "qty": "0.0001",
            "filled_qty": "0",
            "filled_avg_price": null,
            "order_class": "",
            "order_type": "market",
            "type": "market",
            "side": "buy",
            "position_intent": "buy_to_open",
            "time_in_force": "gtc",
            "limit_price": null,
            "stop_price": null,
            "status": "pending_new",
            "extended_hours": false,
            "legs": null,
            "trail_percent": null,
            "trail_price": null,
            "hwm": null,
            "subtag": null,
            "source": null,
            "expires_at": "2025-09-28T20:00:00Z"
        }
        """

        return {
            "status": "success",
            "order": {
                "id": order["id"],
                "symbol": order["symbol"],
                "qty": order["qty"],
                "order_type": order["order_type"],
                "side": order["side"],
                "type": order["type"],
                "time_in_force": order["time_in_force"],
                "status": order["status"],
                "position_intent": order["position_intent"],
                "asset_class": order["asset_class"],
                "expired_at": order["expires_at"],
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


async def place_crypto_market_order(symbol: str, quantity: float, side: str,
                                    tool_context: ToolContext | None = None) -> dict:
    """Place a market order for a specific stock or crypto symbol.
    Args:
        symbol (str): The stock or crypto ticker symbol, e.g., 'AAPL' for Apple, 'BTC/USD' for Bitcoin, "ETH/USD" for Ethereum or "SOL/USD" for Solana. For currency pairs, use the format 'BASEQUOTE', e.g., 'BTC/USD' for Bitcoin to US Dollar. or between crypto pairs like 'ETH/BTC' for Ethereum to Bitcoin.
        quantity (float): The quantity of shares or units to buy or sell, e.g., 10.0 for 10 shares or 0.5 for half a Bitcoin.
        side (str): The side of the order, either 'buy' or 'sell'.
    Returns:
        dict: A dictionary containing the status and order details or error message.
    """
    # time_in_force is set to GTC (Good Till Cancelled) for crypto market orders, meaning the order will remain active until it is filled or cancelled.
    # This is suitable for crypto trading where orders can remain open for longer periods due to the 24/7 nature of crypto markets.
    return await _place_market_order(symbol=symbol, quantity=quantity, side=side,
                                     time_in_force=TimeInForce.GTC, tool_context=tool_context)


async def place_stock_market_order(symbol: str, quantity: float, side: str,
                                   tool_context: ToolContext | None = None) -> dict:
    """Place a market order for a specific stock symbol.
    Args:
        symbol (str): The stock ticker symbol, e.g., 'AAPL' for Apple.
        quantity (float): The number of shares to buy or sell.
        side (str): The side of the order, either 'buy' or 'sell'.
    Returns:
        dict: A dictionary containing the status and order details or error message.
    """
    # time_in_force is set to DAY for stock market orders, meaning the order is valid only for the current trading day.
    # This is suitable for stock trading where orders are typically executed within the trading day. If not filled, the order will be cancelled at the end of the trading day.
    return await _place_market_order(symbol=symbol, quantity=quantity, side=side,
                                     time_in_force=TimeInForce.DAY, tool_context=tool_context)


async def get_all_orders(tool_context: ToolContext | None = None) -> dict:
    """
    Get all orders placed by the user.
    Returns:
        dict: A dictionary containing the status and list of all orders or error message.
    """
    try:
        get_order_request = GetOrdersRequest(
            status=QueryOrderStatus.ALL  # Gett all orders
        )
        # Fetch all orders using the trading client
        orders = trading_client.get_orders(filter=get_order_request)
        return {"status": "success", "orders": [
            {
                "id": order["id"],
                "symbol": order["symbol"],
                "qty": order["qty"],
                "order_type": order["order_type"],
                "side": order["side"],
                "type": order["type"],
                "time_in_force": order["time_in_force"],
                "status": order["status"],
                "position_intent": order["position_intent"],
                "asset_class": order["asset_class"],
                "expired_at": order["expires_at"],
            } for order in orders
        ]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_open_orders(tool_context: ToolContext | None = None) -> dict:
    """Get all currently open orders.
    Returns:
        dict: A dictionary containing the status and list of open orders or error message.
    """
    try:
        get_order_request = GetOrdersRequest(
            status=QueryOrderStatus.OPEN  # Filter for open orders only
        )
        # Fetch all open orders using the trading client
        open_orders = trading_client.get_orders(filter=get_order_request)
        return {"status": "success", "open_orders": [
            {
                "id": order["id"],
                "symbol": order["symbol"],
                "qty": order["qty"],
                "order_type": order["order_type"],
                "side": order["side"],
                "type": order["type"],
                "time_in_force": order["time_in_force"],
                "status": order["status"],
                "position_intent": order["position_intent"],
                "asset_class": order["asset_class"],
                "expired_at": order["expires_at"],
            } for order in open_orders
        ]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_closed_orders(tool_context: ToolContext | None = None) -> dict:
    """Get all cancelled orders.
    Returns:
        dict: A dictionary containing the status and list of cancelled orders or error message.
    """
    try:
        get_order_request = GetOrdersRequest(
            status=QueryOrderStatus.CLOSED  # Filter for cancelled orders only
        )
        # Fetch all cancelled orders using the trading client
        cancelled_orders = trading_client.get_orders(filter=get_order_request)
        return {"status": "success", "cancelled_orders": [
            {
                "id": order["id"],
                "symbol": order["symbol"],
                "qty": order["qty"],
                "order_type": order["order_type"],
                "side": order["side"],
                "type": order["type"],
                "time_in_force": order["time_in_force"],
                "status": order["status"],
                "position_intent": order["position_intent"],
                "asset_class": order["asset_class"],
                "expired_at": order["expires_at"],
            } for order in cancelled_orders
        ]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def cancel_order_by_id(order_id: str, tool_context: ToolContext | None = None) -> dict:
    """Cancel an order by its ID.
    Args:
        order_id (str): The ID of the order to cancel.
    Returns:
        dict: A dictionary containing the status and details of the cancelled order or error message.
    """
    try:
        # Cancel the order using the trading client
        trading_client.cancel_order_by_id(order_id=order_id)
        return {"status": "success", "cancelled_order": f"{order_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_all_open_positions(tool_context: ToolContext | None = None) -> dict:
    """Get all currently open positions.
    Returns:
        dict: A dictionary containing the status and list of open positions or error message.
    """
    try:
        # Fetch all open positions using the trading client
        positions = trading_client.get_all_positions()

        """
        Example of the positions response:
        [
            {
              "asset_id": "b0b6dd9d-8b9b-48a9-ba46-b9d54906e415",
              "symbol": "AAPL",
              "exchange": "NASDAQ",
              "asset_class": "us_equity",
              "asset_marginable": true,
              "qty": "0.5",
              "avg_entry_price": "203.5",
              "side": "long",
              "market_value": "103.45",
              "cost_basis": "101.75",
              "unrealized_pl": "1.7",
              "unrealized_plpc": "0.0167076167076167",
              "unrealized_intraday_pl": "0.865",
              "unrealized_intraday_plpc": "0.0084320319734854",
              "current_price": "206.9",
              "lastday_price": "205.17",
              "change_today": "0.0084320319734854",
              "qty_available": "0.5"
            },
            {
              "asset_id": "64bbff51-59d6-4b3c-9351-13ad85e3c752",
              "symbol": "BTCUSD",
              "exchange": "CRYPTO",
              "asset_class": "crypto",
              "asset_marginable": false,
              "qty": "0.000399",
              "avg_entry_price": "106532.62475",
              "side": "long",
              "market_value": "42.491122",
              "cost_basis": "42.506517",
              "unrealized_pl": "-0.015395",
              "unrealized_plpc": "-0.0003621797570476",
              "unrealized_intraday_pl": "-0.015395",
              "unrealized_intraday_plpc": "-0.0003621797570476",
              "current_price": "106494.04",
              "lastday_price": "107351.4",
              "change_today": "-0.0079864817785329",
              "qty_available": "0.000399"
            },
            {
              "asset_id": "8ccae427-5dd0-45b3-b5fe-7ba5e422c766",
              "symbol": "TSLA",
              "exchange": "NASDAQ",
              "asset_class": "us_equity",
              "asset_marginable": true,
              "qty": "1",
              "avg_entry_price": "363.97",
              "side": "long",
              "market_value": "298.82",
              "cost_basis": "363.97",
              "unrealized_pl": "-65.15",
              "unrealized_plpc": "-0.1789982690881117",
              "unrealized_intraday_pl": "-18.84",
              "unrealized_intraday_plpc": "-0.0593086948309513",
              "current_price": "298.82",
              "lastday_price": "317.66",
              "change_today": "-0.0593086948309513",
              "qty_available": "1"
            }
        ]
        """

        if SAVE_CHART_ARTIFACT and tool_context is not None:
            # Generate pie chart percentage of open positions using Plotly Express
            position_values = {
                position["symbol"]: float(position["market_value"])
                for position in positions
            }

            fig = px.pie(
                names=list(position_values.keys()),
                values=list(position_values.values()),
                title="Open Positions Market Value Distribution",
                labels={"value": "Market Value", "names": "Symbol"},
            )

            # Save the chart as an image bytes
            chart_bytes = fig.to_image(format="png")

            # Save the chart image to the tool context for later use
            await tool_context.save_artifact(
                filename=f"open_positions_distribution_{dt.datetime.now(dt.UTC).strftime('%Y%m%d_%H%M%S')}.png",
                artifact=types.Part.from_bytes(
                    data=chart_bytes,
                    mime_type="image/png",
                )
            )

            # Generate bar chart for position P&L percent using Plotly Express
            position_pnl = {
                position["symbol"]: float(position["unrealized_plpc"]) * 100  # Convert to percentage
                for position in positions
            }

            fig_pnl = px.bar(
                x=list(position_pnl.keys()),
                y=list(position_pnl.values()),
                title="Open Positions P&L Percentage",
                labels={"x": "Symbol", "y": "P&L Percentage (%)"},
            )

            # Save the P&L chart as an image bytes
            pnl_chart_bytes = fig_pnl.to_image(format="png")

            # Save the P&L chart image to the tool context for later use
            await tool_context.save_artifact(
                filename=f"open_positions_pnl_{dt.datetime.now(dt.UTC).strftime('%Y%m%d_%H%M%S')}.png",
                artifact=types.Part.from_bytes(
                    data=pnl_chart_bytes,
                    mime_type="image/png",
                )
            )

        return {"status": "success", "open_positions": [
            {
                "symbol": position["symbol"],
                "exchange": position["exchange"],
                "asset_class": position["asset_class"],
                "quantity": position["qty"],
                "average_entry_price": position["avg_entry_price"],
                "side": position["side"],
                "market_value": position["market_value"],
                "cost_basis": position["cost_basis"],
                "total_pnl_since_buy_in_cash": position["unrealized_pl"],
                "total_pnl_since_buy_in_percentage": position["unrealized_plpc"],
                "total_intraday_pnl_in_cash": position["unrealized_intraday_pl"],
                "total_intraday_pnl_in_percentage": position["unrealized_intraday_plpc"],
                "current_price": position["current_price"],
                "lastday_price": position["lastday_price"],
            } for position in positions
        ]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def panic_exit(tool_context: ToolContext | None = None) -> dict:
    """Close all currently open positions and cancel all open orders.
    This function is used to quickly exit all positions and cancel all orders in case of a market emergency or panic situation.
    Returns:
        dict: A dictionary containing the status and list of closed positions and cancelled orders or error message.
    """
    try:
        closed_positions = trading_client.close_all_positions(
            cancel_orders=True)  # close all positions and cancel all open orders
        return {"status": "success", "closed_positions": closed_positions}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def close_all_positions(tool_context: ToolContext | None = None) -> dict:
    """Close all currently open positions.
    Returns:
        dict: A dictionary containing the status and list of closed positions or error message.
    """
    try:
        closed_positions = trading_client.close_all_positions(
            cancel_orders=False)  # close all positions without cancelling orders
        return {"status": "success", "closed_positions": closed_positions}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_account_information(tool_context: ToolContext | None = None) -> dict:
    """Get account information including cash balance, buying power, and account status.
    Returns:
        dict: A dictionary containing the status and account information or error message.
    """
    try:
        account = trading_client.get_account()  # Fetch account information
        """
        Example of the account response:
        {
            "id": "3394134a-4136-4eae-bb2e-e652dc503d37",
            "admin_configurations": {},
            "user_configurations": null,
            "account_number": "PA3NV9Q7CWET",
            "status": "ACTIVE",
            "crypto_status": "ACTIVE",
            "options_approved_level": 3,
            "options_trading_level": 3,
            "currency": "USD",
            "buying_power": "199178.71",
            "regt_buying_power": "199178.71",
            "daytrading_buying_power": "0",
            "effective_buying_power": "199178.71",
            "non_marginable_buying_power": "99327.41",
            "options_buying_power": "99327.41",
            "bod_dtbp": "0",
            "cash": "99491.65",
            "accrued_fees": "0",
            "portfolio_value": "99936.41",
            "pattern_day_trader": false,
            "trading_blocked": false,
            "transfers_blocked": false,
            "account_blocked": false,
            "created_at": "2025-05-17T09:25:59.625558Z",
            "trade_suspended_by_user": false,
            "multiplier": "2",
            "shorting_enabled": true,
            "equity": "99936.41",
            "last_equity": "99954.515",
            "long_market_value": "444.76",
            "short_market_value": "0",
            "position_market_value": "444.76",
            "initial_margin": "304.57",
            "maintenance_margin": "150.56",
            "last_maintenance_margin": "157.84",
            "sma": "99958.44",
            "daytrade_count": 0,
            "balance_asof": "2025-06-30",
            "crypto_tier": 1,
            "intraday_adjustments": "0",
            "pending_reg_taf_fees": "0"
        }
        """

        if SAVE_CHART_ARTIFACT and tool_context is not None:
            # Generate a pie chart of the account's asset allocation using Plotly Express
            asset_allocation = {
                "Cash": float(account["cash"]),
                "Equity": float(account["equity"]),
                "Long Market Value": float(account["long_market_value"]),
                "Short Market Value": float(account["short_market_value"]),
            }
            fig = px.pie(
                names=list(asset_allocation.keys()),
                values=list(asset_allocation.values()),
                title="Account Asset Allocation",
                labels={"value": "Amount", "names": "Asset Type"},
            )
            # Save the chart as an image bytes
            chart_bytes = fig.to_image(format="png")
            # Save the chart image to the tool context for later use
            await tool_context.save_artifact(
                filename=f"account_asset_allocation_{dt.datetime.now(dt.UTC).strftime('%Y%m%d_%H%M%S')}.png",
                artifact=types.Part.from_bytes(
                    data=chart_bytes,
                    mime_type="image/png",
                )
            )

        # We will only return the relevant account information that we need for trading.
        return {"status": "success", "account": {
            "account_number": account["account_number"],  # account number, e.g., PA3NV9Q7CWET
            "status": account["status"],  # account status, e.g., ACTIVE, INACTIVE, etc.
            "currency": account["currency"],  # currency of the account, e.g., USD for US Dollar
            "buying_power": account["buying_power"],
            # total buying power available for trading, this is the total cash and margin available for trading
            "cash": account["cash"],
            # current cash balance in the account, this is the total cash available for trading
            "equity": account["equity"],
            # current equity value of the account, this is the total value of the account including cash and positions
            "long_market_value": account["long_market_value"],  # market value of all long positions
            "short_market_value": account["short_market_value"],  # market value of all short positions
            "portfolio_value": account["portfolio_value"],  # total value of the portfolio including cash and positions
            "buying_power_available": account["effective_buying_power"],
            # effective buying power available for trading, this is the total cash and margin available for trading
            "non_marginable_buying_power": account["non_marginable_buying_power"],
            # buying power available for non-marginable assets, non-marginable assets are those that cannot be used as collateral for margin trading
            "options_buying_power": account["options_buying_power"],  # buying power available for options trading
            "last_equity": account["last_equity"],  # last equity value of the account from the previous trading day
        }}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# This function is to fetch historical candlestick data for a specific stock or crypto symbol.
async def get_today_candlestick_crypto_data(
        symbol: str,
        tool_context: ToolContext | None = None
) -> dict:
    """Fetch today candlestick data for a specific crypto symbol.
    Args:
        symbol (str): The crypto ticker symbol, e.g., 'BTC/USD' for Bitcoin to USD. BTC/SOL for Bitcoin to Solana or 'ETH/BTC' for Ethereum to Bitcoin.
    Returns:
        dict: A dictionary containing the status and candlestick data or error message.
    """

    try:
        today_00_00 = dt.datetime.now(dt.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        today_23_59 = dt.datetime.now(dt.UTC).replace(hour=23, minute=59, second=59, microsecond=999999)

        request_params = CryptoBarsRequest(
            symbol_or_symbols=symbol,  # The crypto symbol to fetch data for, e.g., 'BTC/USD'
            start=today_00_00,  # Start date for the historical data
            end=today_23_59,  # End date for the historical data
            timeframe=TimeFrame.Hour,
            limit=10000  # maximum number of bars to fetch, can be adjusted as needed
        )
        bars = crypto_historical_data_client.get_crypto_bars(request_params)
        # --- Add symbol existence check ---
        if symbol not in bars or not bars[symbol]:
            return {"status": "error", "message": f"No candlestick data found for symbol {symbol}."}
        bars = bars[symbol]
        """
        Example of the bars response:
        [
          {
            "c": 105816.849,
            "h": 105873.9685,
            "l": 105816.849,
            "n": 0,
            "o": 105873.9685,
            "t": "2025-07-01T15:23:00Z",
            "v": 0,
            "vw": 105845.40875
          },
          {
            "c": 105865.75,
            "h": 105865.75,
            "l": 105865.75,
            "n": 0,
            "o": 105865.75,
            "t": "2025-07-01T15:24:00Z",
            "v": 0,
            "vw": 105865.75
          }
        ]
        """

        understandable_bars = [
            {
                "timestamp": bar["t"],  # Convert timestamp to ISO 8601 format
                "open": bar["o"],  # Open price
                "high": bar["h"],  # High price
                "low": bar["l"],  # Low price
                "close": bar["c"],  # Close price
                "bar_volume": bar["v"],  # Volume of trades
                "volumn_weighted_average_price": bar["vw"],  # Volume-weighted average price
                "trade_count": bar["n"],  # Number of trades
            } for bar in bars
        ]

        if SAVE_CHART_ARTIFACT and tool_context is not None:
            # Generate a candlestick chart using Plotly
            fig = go.Figure(data=[go.Candlestick(
                x=[dt.datetime.fromisoformat(bar["timestamp"].replace("Z", "+00:00")) for bar in understandable_bars],
                open=[bar["open"] for bar in understandable_bars],
                high=[bar["high"] for bar in understandable_bars],
                low=[bar["low"] for bar in understandable_bars],
                close=[bar["close"] for bar in understandable_bars],
            )])
            # Update the layout of the chart
            fig.update_layout(
                title=f"{symbol} Candlestick Chart",
                xaxis_title="Time",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
            )
            # Save the chart as an image bytes
            chart_bytes = fig.to_image(format="png")
            # Save the chart image to the tool context for later use
            await tool_context.save_artifact(
                filename=f"today_candlestick_{symbol.replace('/', '')}_{dt.datetime.now(dt.UTC).strftime('%Y%m%d_%H%M%S')}.png",
                artifact=types.Part.from_bytes(
                    data=chart_bytes,
                    mime_type="image/png",
                )
            )

        return {"status": "success", "candlestick_data": understandable_bars}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# This function is to fetch historical candlestick data for a specific stock symbol.
async def get_today_candlestick_stock_data(
        symbol: str,
        tool_context: ToolContext | None = None
) -> dict:
    """Fetch candlestick data for a specific stock symbol.
    Args:
        symbol (str): The stock ticker symbol, e.g., 'AAPL' for Apple.
    Returns:
        dict: A dictionary containing the status and candlestick data or error message.
    """

    try:
        today_00_00 = dt.datetime.now(dt.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        today_23_59 = dt.datetime.now(dt.UTC).replace(hour=23, minute=59, second=59, microsecond=999999)

        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,  # The stock symbol to fetch data for, e.g., 'AAPL'
            start=today_00_00,  # Start date for the historical data
            end=today_23_59,  # End date for the historical data
            timeframe=TimeFrame.Hour,
            limit=10000,  # maximum number of bars to fetch, can be adjusted as needed
            feed=DataFeed.IEX
            # IEX is the only free data feed for Alpaca free accounts, other feeds like SIP, DELAYED_SIP and OTC are paid and require a subscription.
        )
        bars = stock_historical_data_client.get_stock_bars(request_params)
        # --- Add symbol existence check ---
        if symbol not in bars or not bars[symbol]:
            return {"status": "error", "message": f"No candlestick data found for symbol {symbol}."}
        bars = bars[symbol]
        """
        Example of the bars response:
        [
          {
            "c": 200.75,
            "h": 202.17,
            "l": 200.57,
            "n": 1628,
            "o": 202.02,
            "t": "2025-06-30T13:00:00Z",
            "v": 124276,
            "vw": 201.097233
          },
          {
            "c": 199.92,
            "h": 201.35,
            "l": 199.595,
            "n": 3188,
            "o": 200.755,
            "t": "2025-06-30T14:00:00Z",
            "v": 273218,
            "vw": 200.545035
          }
        ]
        """
        understandable_bars = [
            {
                "timestamp": bar["t"],  # Convert timestamp to ISO 8601 format
                "open": bar["o"],  # Open price
                "high": bar["h"],  # High price
                "low": bar["l"],  # Low price
                "close": bar["c"],  # Close price
                "bar_volume": bar["v"],  # Volume of trades
                "volumn_weighted_average_price": bar["vw"],  # Volume-weighted average price
                "trade_count": bar["n"],  # Number of trades
            } for bar in bars
        ]

        if SAVE_CHART_ARTIFACT and tool_context is not None:
            # Generate a candlestick chart using Plotly
            fig = go.Figure(data=[go.Candlestick(
                x=[dt.datetime.fromisoformat(bar["timestamp"].replace("Z", "+00:00")) for bar in understandable_bars],
                open=[bar["open"] for bar in understandable_bars],
                high=[bar["high"] for bar in understandable_bars],
                low=[bar["low"] for bar in understandable_bars],
                close=[bar["close"] for bar in understandable_bars],
            )])
            # Update the layout of the chart
            fig.update_layout(
                title=f"{symbol} Candlestick Chart",
                xaxis_title="Time",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
            )
            # Save the chart as an image bytes
            chart_bytes = fig.to_image(format="png")
            # Save the chart image to the tool context for later use
            await tool_context.save_artifact(
                filename=f"candlestick_{symbol}_{dt.datetime.now(dt.UTC).strftime('%Y%m%d_%H%M%S')}.png",
                artifact=types.Part.from_bytes(
                    data=chart_bytes,
                    mime_type="image/png",
                )
            )

        return {"status": "success", "candlestick_data": understandable_bars}
    except Exception as e:
        return {"status": "error", "message": str(e)}


import pandas as pd

# --- Add: Get current price for stock or crypto ---
async def get_current_price(symbol: str, tool_context: ToolContext | None = None) -> dict:
    """
    Get the current/latest price for a stock or crypto symbol.
    Args:
        symbol (str): The ticker symbol, e.g., 'AAPL' or 'BTC/USD'.
    Returns:
        dict: A dictionary with the latest price or error message.
    """
    try:
        if "/" in symbol:  # Crypto
            bars = crypto_historical_data_client.get_crypto_bars(
                CryptoBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=TimeFrame.Minute,
                    limit=1
                )
            )
            # --- Add symbol existence check ---
            if symbol not in bars or not bars[symbol]:
                return {"status": "error", "message": f"No price data found for {symbol}."}
            last_bar = bars[symbol][-1]
        else:  # Stock
            bars = stock_historical_data_client.get_stock_bars(
                StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=TimeFrame.Minute,
                    limit=1,
                    feed=DataFeed.IEX
                )
            )
            # --- Add symbol existence check ---
            if symbol not in bars or not bars[symbol]:
                return {"status": "error", "message": f"No price data found for {symbol}."}
            last_bar = bars[symbol][-1]

        return {
            "status": "success",
            "symbol": symbol,
            "price": last_bar["c"],  # 'c' is the close price of the last bar
            "timestamp": last_bar["t"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- Add: Get historical prices for stock or crypto (multi-symbol support) ---
async def get_historical_prices(
    symbols: str,  # Accept comma-separated string
    start: str,
    end: str,
    interval: str = "day",
    tool_context: ToolContext | None = None
) -> dict:
    """
    Get historical prices for one or more stock or crypto symbols.
    Args:
        symbols (str): Comma-separated ticker symbols, e.g., 'AAPL' or 'AAPL,MSFT' or 'BTC/USD'.
        start (str): Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
        end (str): End date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
        interval (str): 'minute', 'hour', or 'day'. Default is 'day'.
    Returns:
        dict: A dictionary with historical price data or error message.
    """
    try:
        tf_map = {
            "minute": TimeFrame.Minute,
            "hour": TimeFrame.Hour,
            "day": TimeFrame.Day
        }
        tf = tf_map.get(interval.lower(), TimeFrame.Day)
        start_dt = dt.datetime.fromisoformat(start)
        end_dt = dt.datetime.fromisoformat(end)

        # Accept comma-separated string for multiple symbols
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]

        results = {}
        for symbol in symbol_list:
            if "/" in symbol:  # Crypto
                bars = crypto_historical_data_client.get_crypto_bars(
                    CryptoBarsRequest(
                        symbol_or_symbols=symbol,
                        start=start_dt,
                        end=end_dt,
                        timeframe=tf,
                        limit=10000
                    )
                )
                if symbol not in bars or not bars[symbol]:
                    results[symbol] = {"status": "error", "message": f"No historical data found for {symbol}."}
                    continue
                df = pd.DataFrame(bars[symbol])
            else:  # Stock
                bars = stock_historical_data_client.get_stock_bars(
                    StockBarsRequest(
                        symbol_or_symbols=symbol,
                        start=start_dt,
                        end=end_dt,
                        timeframe=tf,
                        limit=10000,
                        feed=DataFeed.IEX
                    )
                )
                if symbol not in bars or not bars[symbol]:
                    results[symbol] = {"status": "error", "message": f"No historical data found for {symbol}."}
                    continue
                df = pd.DataFrame(bars[symbol])

            # Convert timestamp to ISO 8601 format
            df["t"] = pd.to_datetime(df["t"]).dt.tz_convert("UTC").dt.strftime(
                "%Y-%m-%dT%H:%M:%SZ")

            # Select and rename columns
            df = df[["t", "o", "h", "l", "c", "v", "n"]]
            df.columns = ["timestamp", "open", "high", "low", "close", "volume", "trade_count"]

            # Convert to JSON serializable format
            historical_data = df.to_dict(orient="records")

            results[symbol] = {
                "status": "success",
                "symbol": symbol,
                "historical_data": historical_data
            }

        return results
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_yesterdays_price_action(symbol: str, tool_context: ToolContext | None = None) -> dict:
    """
    Get the price action (open, high, low, close, volume) for yesterday for a given symbol.
    Args:
        symbol (str): The stock or crypto ticker symbol, e.g., 'AAPL' or 'BTC/USD'.
    Returns:
        dict: A dictionary with the price action for yesterday or error message.
    """
    try:
        today = dt.datetime.now(dt.UTC).date()
        yesterday = today - dt.timedelta(days=1)
        start = dt.datetime.combine(yesterday, dt.time(0, 0)).isoformat()
        end = dt.datetime.combine(yesterday, dt.time(23, 59, 59)).isoformat()
        result = await get_historical_prices(
            symbols=symbol,
            start=start,
            end=end,
            interval="day"
        )
        if symbol in result and result[symbol]["status"] == "success":
            return {
                "status": "success",
                "symbol": symbol,
                "yesterdays_price_action": result[symbol]["historical_data"]
            }
        else:
            return {"status": "error", "message": f"No price action found for {symbol} on {yesterday}."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def plot_price_action(
    symbol: str,
    start: str,
    end: str,
    interval: str = "day",
    tool_context: ToolContext | None = None
) -> dict:
    """
    Plot price action for a symbol over a given date range and save as an artifact (if enabled).
    Args:
        symbol (str): The ticker symbol, e.g., 'AAPL' or 'BTC/USD'.
        start (str): Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
        end (str): End date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ).
        interval (str): 'minute', 'hour', or 'day'. Default is 'day'.
    Returns:
        dict: Status and message or artifact info.
    """
    try:
        result = await get_historical_prices(
            symbols=symbol,
            start=start,
            end=end,
            interval=interval,
            tool_context=tool_context
        )
        if symbol not in result or result[symbol]["status"] != "success":
            return {"status": "error", "message": f"No historical data found for {symbol}."}
        data = result[symbol]["historical_data"]
        if not data:
            return {"status": "error", "message": f"No data to plot for {symbol}."}

        if SAVE_CHART_ARTIFACT and tool_context is not None:
            import plotly.graph_objects as go
            import pandas as pd
            df = pd.DataFrame(data)
            fig = go.Figure(data=[go.Candlestick(
                x=pd.to_datetime(df["timestamp"]),
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
            )])
            fig.update_layout(
                title=f"{symbol} Price Action ({start} to {end})",
                xaxis_title="Time",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
            )
            chart_bytes = fig.to_image(format="png")
            filename = f"price_action_{symbol}_{start[:10]}_{end[:10]}.png"
            await tool_context.save_artifact(
                filename=filename,
                artifact=types.Part.from_bytes(
                    data=chart_bytes,
                    mime_type="image/png",
                )
            )
            return {"status": "success", "message": f"Chart saved as {filename}."}
        else:
            return {"status": "success", "message": "Chart plotting is disabled or no tool context provided."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


tools = [
    FunctionTool(func=get_account_information),
    FunctionTool(func=get_all_open_positions),
    FunctionTool(func=get_open_orders),
    FunctionTool(func=get_closed_orders),
    FunctionTool(func=get_all_orders),
    FunctionTool(func=place_stock_market_order),
    FunctionTool(func=place_crypto_market_order),
    FunctionTool(func=get_supported_crypto_symbols),
    FunctionTool(func=fetch_today_news_for_symbol),
    FunctionTool(func=cancel_order_by_id),
    FunctionTool(func=panic_exit),
    FunctionTool(func=close_all_positions),
    FunctionTool(func=get_today_candlestick_crypto_data),
    FunctionTool(func=get_today_candlestick_stock_data),
    FunctionTool(func=get_current_price),
    FunctionTool(func=get_historical_prices),
    FunctionTool(func=get_yesterdays_price_action),
    FunctionTool(func=plot_price_action),
]

"""
All code below this is only use while testing the functions in the main block.
"""


async def __test():
    # We will test the functions here in the main block because we don't want to complicate the project with unit tests for now.

    # Test new fetching function
    symbol = "AAPL"  # Example stock symbol for Apple Inc.
    news_result = await fetch_today_news_for_symbol(symbol)
    print(json.dumps(news_result, indent=2))  # Print the fetched news articles or error message

    # Test crypto symbols fetching function
    crypto_symbols_result = await get_supported_crypto_symbols()
    print(json.dumps(crypto_symbols_result, indent=2))  # Print the list of supported crypto symbols or error message

    # Test market order placement function for crypto
    crypto_order_result = await place_crypto_market_order(symbol="BTC/USD", quantity=0.0001, side="buy")
    print(json.dumps(crypto_order_result, indent=2))  # Print the order details or error message
    await cancel_order_by_id(order_id=crypto_order_result["order"][
        "id"])  # Cancel the stock order by ID, because we are just testing the function

    # Test market order placement function for stock
    stock_order_result = await place_stock_market_order(symbol="AAPL", quantity=0.5, side="buy")
    print(json.dumps(stock_order_result, indent=2))  # Print the stock order details or error message
    await cancel_order_by_id(order_id=stock_order_result["order"][
        "id"])  # Cancel the stock order by ID, because we are just testing the function

    # Test fetching all orders
    all_orders_result = await get_all_orders()
    print(json.dumps(all_orders_result, indent=2))  # Print all orders or error message

    # Test fetching open orders
    open_orders_result = await get_open_orders()
    print(json.dumps(open_orders_result, indent=2))  # Print open orders or error message

    # Test fetching closed orders
    closed_orders_result = await get_closed_orders()
    print(json.dumps(closed_orders_result, indent=2))  # Print closed orders or error message

    # Test fetching all open positions
    open_positions_result = await get_all_open_positions()
    print(json.dumps(open_positions_result, indent=2))  # Print open positions or error message

    # Test getting account information
    account_info_result = await get_account_information()
    print(json.dumps(account_info_result, indent=2))  # Print account information or error message

    # Test historical data fetching for crypto
    last_2_hours = dt.datetime.now(dt.UTC) - dt.timedelta(minutes=15)
    now = dt.datetime.now(dt.UTC)
    historical_crypto_data_result = await get_today_candlestick_crypto_data(
        symbol="BTC/USD",
    )
    print(json.dumps(historical_crypto_data_result, indent=2))  # Print historical crypto data or error message

    # Test historical data fetching for stock
    last_2_days = dt.datetime.now(dt.UTC) - dt.timedelta(days=2)
    now = dt.datetime.now(dt.UTC)
    historical_stock_data_result = await get_today_candlestick_stock_data(
        symbol="AAPL",
    )
    print(json.dumps(historical_stock_data_result, indent=2))  # Print historical stock data or error message

    # Test current price fetching
    current_price_result = await get_current_price(symbol="AAPL")
    print(json.dumps(current_price_result, indent=2))  # Print current price or error message

    # Test historical prices fetching
    historical_prices_result = await get_historical_prices(
        symbols="AAPL,BTC/USD",  # <-- FIXED: pass as string
        start="2025-06-01",
        end="2025-06-30",
        interval="day"
    )
    print(json.dumps(historical_prices_result, indent=2))  # Print historical prices or error message

    # Test yesterday's price action fetching
    yesterdays_price_action_result = await get_yesterdays_price_action(symbol="AAPL")
    print(json.dumps(yesterdays_price_action_result, indent=2))  # Print yesterday's price action or error message

    # Test price action plotting
    plot_result = await plot_price_action(
        symbol="AAPL",
        start="2025-06-01",
        end="2025-06-30",
        interval="day"
    )
    print(json.dumps(plot_result, indent=2))  # Print plot result or error message


if __name__ == "__main__":
    asyncio.run(__test())  # RUn test function asynchronously
