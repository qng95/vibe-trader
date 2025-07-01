def get_company_news(symbol: str, _from: str, to: str) -> list:
    """
    Fetches company news for a given stock symbol within a specified date range.
    :param symbol: Stock symbol of the company (e.g., 'AAPL' for Apple Inc.)
    :param _from: Start date in 'YYYY-MM-DD' format.
    :param to: End date in 'YYYY-MM-DD'
    :return: List of news articles related to the company.
    """
    # Placeholder for actual implementation
    import finnhub
    finnhub_client = finnhub.Client(api_key="d0nm271r01qn5ghkj7cgd0nm271r01qn5ghkj7d0")

    news = finnhub_client.company_news(symbol=symbol, _from=_from, to=to)