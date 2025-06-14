from datetime import date, timedelta

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