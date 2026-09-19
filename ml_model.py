import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_price(symbol):

    df = yf.download(symbol, period="3mo")

    if df.empty:
        return None

    df['Prediction'] = df[['Close']].shift(-1)

    X = df[['Close']]
    y = df['Prediction']

    X = X[:-1]
    y = y[:-1]

    model = LinearRegression()
    model.fit(X, y)

    prediction = model.predict(df[['Close']].tail(1))

    return float(prediction[0])