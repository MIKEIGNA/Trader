

import time
import pandas as pd
import numpy as np

# Import historical price data
data = pd.read_csv('datasets/BTCUSD_M15.csv')

# Calculate the 50 EMA
data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()

# ATR Calculation for volatility filtering
data['TR'] = np.maximum(data['High'] - data['Low'], np.maximum(abs(data['High'] - data['Close'].shift(1)), abs(data['Low'] - data['Close'].shift(1))))
data['ATR'] = data['TR'].rolling(window=14).mean()

# Volume Filter: Average volume over last 20 periods
data['Avg_Volume'] = data['Volume'].rolling(window=20).mean()

# Add Chandelier Stop (using ATR)
def chandelier_stop(data, atr_multiplier=3):
    data['Chandelier_Stop'] = data['Close'] - (atr_multiplier * data['ATR'])
    return data

data = chandelier_stop(data)

# Set up variables for tracking trades
balance = 1000  # Starting balance
position = None
stop_loss = None
take_profit = None
risk_percent = 0.02  # Risk 2% of the balance per trade to allow more trades
trade_log = []
trade_records = []  # To hold trade event data

# Backtest loop with refined rules
for i in range(3, len(data)):
    atr_filter = data['ATR'][i] > 0.2  # Lower Volatility Filter: Only trade if ATR is above 0.2
    volume_filter = data['Volume'][i] > 0.5 * data['Avg_Volume'][i]  # Loosen volume filter to half the average volume
    
    if atr_filter and volume_filter:
        # Check for long entry
        if data['Close'][i] > data['EMA_50'][i] and data['Close'][i-1] < data['Close'][i-2] and data['Close'][i-1] < data['Close'][i-3]:
            if data['Close'][i] > max(data['High'][i-4:i]):
                entry_price = data['Close'][i]
                stop_loss = data['Chandelier_Stop'][i]
                if np.isnan(stop_loss):  # If Chandelier Stop is not valid, use default stop-loss
                    stop_loss = entry_price - data['ATR'][i]  # Default stop-loss: 1x ATR below entry
                trade_risk = min(balance * risk_percent, entry_price - stop_loss)  # Risk 2% of the balance
                take_profit = entry_price + 2 * (entry_price - stop_loss)
                position = 'long'
                balance -= trade_risk  # Deduct the risk from balance
                trade_log.append({'type': 'buy', 'price': entry_price, 'stop_loss': stop_loss, 'take_profit': take_profit, 'balance': balance})
                trade_records.append([data['Time'][i], 'buy', entry_price, stop_loss, take_profit, balance])
        
        # Check for short entry
        elif data['Close'][i] < data['EMA_50'][i] and data['Close'][i-1] > data['Close'][i-2] and data['Close'][i-1] > data['Close'][i-3]:
            if data['Close'][i] < min(data['Low'][i-4:i]):
                entry_price = data['Close'][i]
                stop_loss = data['Chandelier_Stop'][i]
                if np.isnan(stop_loss):  # If Chandelier Stop is not valid, use default stop-loss
                    stop_loss = entry_price + data['ATR'][i]  # Default stop-loss: 1x ATR above entry
                trade_risk = min(balance * risk_percent, stop_loss - entry_price)
                take_profit = entry_price - 2 * (stop_loss - entry_price)
                position = 'short'
                balance -= trade_risk  # Deduct the risk from balance
                trade_log.append({'type': 'sell', 'price': entry_price, 'stop_loss': stop_loss, 'take_profit': take_profit, 'balance': balance})
                trade_records.append([data['Time'][i], 'sell', entry_price, stop_loss, take_profit, balance])
    
    # Exit long position
    if position == 'long' and (data['Close'][i] <= stop_loss or data['Close'][i] >= take_profit):
        balance += (data['Close'][i] - entry_price)
        trade_log.append({'type': 'exit', 'price': data['Close'][i], 'balance': balance})
        trade_records.append([data['Time'][i], 'exit', data['Close'][i], stop_loss, take_profit, balance])
        position = None
    
    # Exit short position
    if position == 'short' and (data['Close'][i] >= stop_loss or data['Close'][i] <= take_profit):
        balance += (entry_price - data['Close'][i])
        trade_log.append({'type': 'exit', 'price': data['Close'][i], 'balance': balance})
        trade_records.append([data['Time'][i], 'exit', data['Close'][i], stop_loss, take_profit, balance])
        position = None

# Analyze performance
print(f"Final Balance: ${balance}")
print(f"Total Trades: {len([log for log in trade_log if log['type'] == 'buy' or log['type'] == 'sell'])}")

# Save trade events to DataFrame
trade_df = pd.DataFrame(trade_records, columns=['Time', 'action', 'price', 'stop_loss', 'take_profit', 'balance'])

# Save DataFrame to CSV for further analysis
trade_df.to_csv('trade_log.csv', index=False)

print("Trade log saved as 'trade_log.csv'")
