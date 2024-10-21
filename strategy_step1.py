import pandas as pd
import numpy as np

# Import historical price data
data = pd.read_csv('datasets/BTCUSD_M15.csv')  # You can change this to your data file

# Calculate the 50 EMA
data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()

# Add a column for Chandelier Stop (we will use ATR for this calculation)
def chandelier_stop(data, atr_multiplier=3):
    data['TR'] = np.maximum(data['High'] - data['Low'], np.maximum(abs(data['High'] - data['Close'].shift(1)), abs(data['Low'] - data['Close'].shift(1))))
    data['ATR'] = data['TR'].rolling(window=22).mean()  # 22 period ATR
    data['Chandelier_Stop'] = data['Close'] - (atr_multiplier * data['ATR'])
    return data

data = chandelier_stop(data)

# Set up variables for tracking trades
balance = 1000  # Starting balance
position = None
stop_loss = None
take_profit = None
trade_log = []

# Trading logic
for i in range(2, len(data)):
    # Long entry condition
    if data['Close'][i] > data['EMA_50'][i] and data['Close'][i-1] <= data['EMA_50'][i-1]:
        pullback = (data['Close'][i-1] < data['Close'][i-2] and data['Close'][i-1] < data['Close'][i-3])
        if pullback and data['Close'][i] > max(data['High'][:i-1]):
            # Enter long
            entry_price = data['Close'][i]
            stop_loss = data['Chandelier_Stop'][i]
            take_profit = entry_price + 2 * (entry_price - stop_loss)
            position = 'long'
            trade_log.append({'type': 'buy', 'price': entry_price, 'stop_loss': stop_loss, 'take_profit': take_profit, 'balance': balance})

    # Short entry condition
    elif data['Close'][i] < data['EMA_50'][i] and data['Close'][i-1] >= data['EMA_50'][i-1]:
        pullback = (data['Close'][i-1] > data['Close'][i-2] and data['Close'][i-1] > data['Close'][i-3])
        if pullback and data['Close'][i] < min(data['Low'][:i-1]):
            # Enter short
            entry_price = data['Close'][i]
            stop_loss = data['Chandelier_Stop'][i]
            take_profit = entry_price - 2 * (stop_loss - entry_price)
            position = 'short'
            trade_log.append({'type': 'sell', 'price': entry_price, 'stop_loss': stop_loss, 'take_profit': take_profit, 'balance': balance})

    # Exit logic (for simplicity)
    if position == 'long' and (data['Close'][i] <= stop_loss or data['Close'][i] >= take_profit):
        # Exit long
        balance += (data['Close'][i] - entry_price)  # P/L calculation
        trade_log.append({'type': 'exit', 'price': data['Close'][i], 'balance': balance})
        position = None

    elif position == 'short' and (data['Close'][i] >= stop_loss or data['Close'][i] <= take_profit):
        # Exit short
        balance += (entry_price - data['Close'][i])  # P/L calculation
        trade_log.append({'type': 'exit', 'price': data['Close'][i], 'balance': balance})
        position = None

# Analyze performance
print(f"Final Balance: ${balance}")
print(f"Total Trades: {len([log for log in trade_log if log['type'] == 'buy' or log['type'] == 'sell'])}")



