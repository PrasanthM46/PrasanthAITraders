import pandas as pd
import numpy as np
import yfinance as yf


def load_data(ticker: str, period: str = "2d", interval: str = "1m") -> pd.DataFrame:
    """Load recent market data from Yahoo Finance."""
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        return pd.DataFrame()

    df = df.rename(columns={"Adj Close": "AdjClose"})
    if "Close" not in df.columns and "AdjClose" in df.columns:
        df["Close"] = df["AdjClose"]

    df = df.loc[:, ~df.columns.duplicated()]
    df = df[~df.index.duplicated(keep="last")]
    df = df.dropna(how="any")
    return df


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add EMA, RSI and Heikin Ashi indicators to the data frame."""
    df = df.copy()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Heikin Ashi candles
    ha_close = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4
    ha_open = [((df["Open"].iloc[0] + df["Close"].iloc[0]) / 2)]
    for i in range(1, len(df)):
        ha_open.append((ha_open[-1] + ha_close.iloc[i - 1]) / 2)
    df["HA_Open"] = ha_open
    df["HA_Close"] = ha_close
    df["HA_High"] = pd.concat([df["High"], df["HA_Open"], df["HA_Close"]], axis=1).max(axis=1)
    df["HA_Low"] = pd.concat([df["Low"], df["HA_Open"], df["HA_Close"]], axis=1).min(axis=1)
    df["HA_Bull"] = df["HA_Close"] > df["HA_Open"]
    df["HA_Bear"] = df["HA_Close"] < df["HA_Open"]

    # Signal with HA confirmation
    df["Signal"] = "NONE"
    call_mask = (df["Close"] > df["EMA50"]) & (df["RSI"] < 35) & df["HA_Bull"]
    put_mask = (df["Close"] < df["EMA50"]) & (df["RSI"] > 65) & df["HA_Bear"]
    df.loc[call_mask, "Signal"] = "CALL"
    df.loc[put_mask, "Signal"] = "PUT"
    return df


def _signal_row(row: pd.Series) -> str:
    if np.isnan(row["EMA50"]) or np.isnan(row["RSI"]):
        return "NONE"
    if row["Close"] > row["EMA50"] and row["RSI"] < 35:
        return "CALL"
    if row["Close"] < row["EMA50"] and row["RSI"] > 65:
        return "PUT"
    return "NONE"


def latest_signal(df: pd.DataFrame) -> str:
    if df.empty:
        return "NONE"
    last = df.iloc[-1]
    return last.get("Signal", "NONE")
