# PrasanthAITraders

A simple Streamlit dashboard for fixed-time trading signals using a 50 EMA + 14 RSI strategy.

## What this does
- Loads recent market data from Yahoo Finance
- Computes 50-period EMA and 14-period RSI
- Displays a CALL or PUT signal based on simple rules
- Shows the latest price, signal, and indicator values

## Install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the dashboard
```powershell
streamlit run app.py
```

## Example usage
- Enter a ticker like `EURUSD=X` or `AAPL`
- Set interval to `1m`, `2m`, `5m`, or `15m`
- Use the dashboard signal as a reference for fixed-time trades

## Notes
- This is a demo strategy, not financial advice.
- Practice on a demo account first.
- Fixed-time trading is risky; use small stakes and strict risk control.
