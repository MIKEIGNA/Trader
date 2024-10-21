# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt

# # Load the trade log data
# trade_df = pd.read_csv('updated_trade_log.csv')

# # Ensure that the 'Time' column is parsed as datetime for time-based analysis
# trade_df['Time'] = pd.to_datetime(trade_df['Time'])

# # Separate trade actions
# entries = trade_df[trade_df['action'].isin(['buy', 'sell'])].reset_index(drop=True)
# exits = trade_df[trade_df['action'] == 'exit'].reset_index(drop=True)

# # Ensure each entry has a corresponding exit
# if len(entries) != len(exits):
#     print("Warning: Mismatch between entry and exit trades!")
#     entries = entries.head(min(len(entries), len(exits)))
#     exits = exits.head(min(len(entries), len(exits)))

# # 1. Performance Metrics
# initial_balance = 1000  # Starting balance
# final_balance = trade_df['balance'].iloc[-1]
# total_return = final_balance - initial_balance

# # Determine if each entry was a buy or sell, and calculate profit accordingly
# profits = []
# for i in range(len(entries)):
#     entry_price = entries['price'].iloc[i]
#     exit_price = exits['price'].iloc[i]
    
#     if entries['action'].iloc[i] == 'buy':  # Long trade
#         profit = exit_price - entry_price
#     else:  # Short trade
#         profit = entry_price - exit_price
#     profits.append(profit)

# # Convert profits into a numpy array for analysis
# profits = np.array(profits)
# win_trades = profits[profits > 0]
# lose_trades = profits[profits <= 0]
# win_rate = len(win_trades) / len(profits) if len(profits) > 0 else 0
# average_profit = np.mean(win_trades) if len(win_trades) > 0 else 0
# average_loss = np.mean(lose_trades) if len(lose_trades) > 0 else 0

# # 2. Drawdown calculation
# balance = trade_df['balance']
# high_watermark = balance.cummax()
# drawdown = balance - high_watermark
# drawdown_pct = (balance / high_watermark - 1) * 100
# max_drawdown = drawdown.min()

# # 3. Profit factor
# total_profit = np.sum(win_trades)
# total_loss = np.sum(lose_trades)
# profit_factor = total_profit / -total_loss if total_loss != 0 else np.inf

# # 4. Expectancy
# expectancy = (win_rate * average_profit) - ((1 - win_rate) * abs(average_loss))

# # 5. Risk/Reward Ratio
# risk_reward_ratio = average_profit / abs(average_loss) if average_loss != 0 else np.inf

# # 6. Sharpe Ratio (assuming no risk-free rate, using return std deviation)
# returns = balance.pct_change().dropna()
# sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)  # Assuming 252 trading days/year

# # Output Performance Metrics
# print(f"Initial Balance: ${initial_balance}")
# print(f"Final Balance: ${final_balance}")
# print(f"Total Return: ${total_return}")
# print(f"Win Rate: {win_rate * 100:.2f}%")
# print(f"Average Profit: ${average_profit:.2f}")
# print(f"Average Loss: ${average_loss:.2f}")
# print(f"Max Drawdown: ${max_drawdown:.2f}")
# print(f"Profit Factor: {profit_factor:.2f}")
# print(f"Expectancy: ${expectancy:.2f}")
# print(f"Risk/Reward Ratio: {risk_reward_ratio:.2f}")
# print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# # 7. Plotting the results
# plt.figure(figsize=(14, 8))

# # Plot the balance over time
# plt.subplot(2, 2, 1)
# plt.plot(trade_df['Time'], trade_df['balance'], label="Balance Over Time")
# plt.title("Balance Over Time")
# plt.xlabel("Time")
# plt.ylabel("Balance")
# plt.grid(True)

# # Plot drawdowns
# plt.subplot(2, 2, 2)
# plt.plot(trade_df['Time'], drawdown_pct, label="Drawdown (%)", color='red')
# plt.fill_between(trade_df['Time'], drawdown_pct, 0, color='red', alpha=0.3)
# plt.title("Drawdown Over Time")
# plt.xlabel("Time")
# plt.ylabel("Drawdown (%)")
# plt.grid(True)

# # Plot histogram of trade returns
# plt.subplot(2, 2, 3)
# plt.hist(profits, bins=20, alpha=0.7, color='blue', edgecolor='black')
# plt.title("Distribution of Trade Returns")
# plt.xlabel("Return per Trade")
# plt.ylabel("Frequency")
# plt.grid(True)

# # Plot cumulative trade returns over time, using the 'exits' times for the x-axis
# plt.subplot(2, 2, 4)
# plt.plot(exits['Time'], np.cumsum(profits), label="Cumulative Trade Returns")
# plt.title("Cumulative Returns Over Time")
# plt.xlabel("Time")
# plt.ylabel("Cumulative Returns")
# plt.grid(True)

# plt.tight_layout()
# plt.show()


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the trade log data
trade_df = pd.read_csv('updated_trade_log.csv')

# Ensure that the 'Time' column is parsed as datetime for time-based analysis
trade_df['Time'] = pd.to_datetime(trade_df['Time'], dayfirst=True)

# Separate trade actions
entries = trade_df[trade_df['action'].isin(['buy', 'sell'])].reset_index(drop=True)
exits = trade_df[trade_df['action'] == 'exit'].reset_index(drop=True)

# Ensure each entry has a corresponding exit, pair trades using index to match them properly
if len(entries) != len(exits):
    print("Warning: Mismatch between entry and exit trades!")
    
# Calculate performance metrics for matched trades only
matched_trades = min(len(entries), len(exits))
entries = entries.iloc[:matched_trades]
exits = exits.iloc[:matched_trades]

# 1. Performance Metrics
initial_balance = 1000
final_balance = trade_df['balance'].iloc[-1]
total_return = final_balance - initial_balance

# For long trades (buy), check if exit price is higher for win trades
win_trades = exits[exits['price'] > entries['price']] 
lose_trades = exits[exits['price'] <= entries['price']]

# Win rate calculation
win_rate = len(win_trades) / len(exits) if len(exits) > 0 else 0

# Average profit and loss
average_profit = (win_trades['price'] - entries.loc[win_trades.index, 'price']).mean() if len(win_trades) > 0 else 0
average_loss = (lose_trades['price'] - entries.loc[lose_trades.index, 'price']).mean() if len(lose_trades) > 0 else 0

# 2. Drawdown calculation
balance = trade_df['balance']
high_watermark = balance.cummax()
drawdown = balance - high_watermark
drawdown_pct = (balance / high_watermark - 1) * 100
max_drawdown = drawdown.min()

# # 3. Profit factor
# total_profit = (win_trades['price'] - entries.loc[win_trades.index, 'price']).sum()
# total_loss = (entries.loc[lose_trades.index, 'price'] - lose_trades['price']).sum()
# profit_factor = total_profit / -total_loss if total_loss != 0 else np.inf

# 3. Profit factor
# Correct Profit Factor Calculation
total_profit = win_trades['price'].sum() - entries.loc[win_trades.index, 'price'].sum()
total_loss = entries.loc[lose_trades.index, 'price'].sum() - lose_trades['price'].sum()

if total_loss != 0:
    profit_factor = total_profit / abs(total_loss)
else:
    profit_factor = np.inf  # Prevent division by zero if there are no losses

# 4. Expectancy
expectancy = (win_rate * average_profit) - ((1 - win_rate) * average_loss)

# 5. Risk/Reward Ratio
risk_reward_ratio = average_profit / abs(average_loss) if average_loss != 0 else np.inf

# 6. Sharpe Ratio (assuming no risk-free rate, using return std deviation)
returns = balance.pct_change().dropna()
sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252)  # Assuming 252 trading days/year

# Output Performance Metrics
print(f"Initial Balance: ${initial_balance}")
print(f"Final Balance: ${final_balance:.2f}")
print(f"Total Return: ${total_return:.2f}")
print(f"Win Rate: {win_rate * 100:.2f}%")
print(f"Average Profit: ${average_profit:.2f}")
print(f"Average Loss: ${average_loss:.2f}")
print(f"Max Drawdown: ${max_drawdown:.2f}")
print(f"Profit Factor: {profit_factor:.2f}")
print(f"Expectancy: ${expectancy:.2f}")
print(f"Risk/Reward Ratio: {risk_reward_ratio:.2f}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# 7. Plotting the results
plt.figure(figsize=(14, 8))

# Plot the balance over time
plt.subplot(2, 2, 1)
plt.plot(trade_df['Time'], trade_df['balance'], label="Balance Over Time")
plt.title("Balance Over Time")
plt.xlabel("Time")
plt.ylabel("Balance")
plt.grid(True)

# Plot drawdowns
plt.subplot(2, 2, 2)
plt.plot(trade_df['Time'], drawdown_pct, label="Drawdown (%)", color='red')
plt.fill_between(trade_df['Time'], drawdown_pct, 0, color='red', alpha=0.3)
plt.title("Drawdown Over Time")
plt.xlabel("Time")
plt.ylabel("Drawdown (%)")
plt.grid(True)

# Plot histogram of trade returns
plt.subplot(2, 2, 3)
trade_returns = exits['price'].values - entries['price'].values
plt.hist(trade_returns, bins=20, alpha=0.7, color='blue', edgecolor='black')
plt.title("Distribution of Trade Returns")
plt.xlabel("Return per Trade")
plt.ylabel("Frequency")
plt.grid(True)

# Plot cumulative trade returns over time, using the 'exits' times for the x-axis
plt.subplot(2, 2, 4)
plt.plot(exits['Time'], trade_returns.cumsum(), label="Cumulative Trade Returns")
plt.title("Cumulative Returns Over Time")
plt.xlabel("Time")
plt.ylabel("Cumulative Returns")
plt.grid(True)

plt.tight_layout()
plt.show()
