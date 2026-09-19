import yfinance as yf


# Get current stock details
def get_stock_data(symbol):

    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if data.empty:
        return None

    stock_data = {
        "open": float(data["Open"][0]),
        "high": float(data["High"][0]),
        "low": float(data["Low"][0]),
        "current": float(data["Close"][0])
    }

    return stock_data


# Get historical stock data for graph
def get_stock_history(symbol):

    stock = yf.Ticker(symbol)

    # last 7 days data
    data = stock.history(period="7d")

    dates = []
    prices = []

    for index, row in data.iterrows():

        date = index.strftime("%Y-%m-%d")
        price = float(row["Close"])

        dates.append(date)
        prices.append(price)

    return dates, prices