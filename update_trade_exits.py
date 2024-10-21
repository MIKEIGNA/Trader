import pandas as pd

# Load your trade log CSV
df = pd.read_csv('trade_log.csv')

# Forward-fill stop_loss and take_profit from previous trades
df['stop_loss'] = df['stop_loss'].ffill()
df['take_profit'] = df['take_profit'].ffill()

# Calculate balance for exit trades
for i in range(1, len(df)):
    if df.loc[i, 'action'] == 'exit':
        previous_balance = df.loc[i-1, 'balance']
        entry_price = df.loc[i-1, 'price']
        exit_price = df.loc[i, 'price']

        # Calculate profit/loss based on whether it was a buy or sell
        if df.loc[i-1, 'action'] == 'buy':
            profit_loss = (exit_price - entry_price) * 0.1  # Assuming lot size of 0.1
        elif df.loc[i-1, 'action'] == 'sell':
            profit_loss = (entry_price - exit_price) * 0.1
        
        # Update the balance for the exit
        df.loc[i, 'balance'] = previous_balance + profit_loss

# Save the updated CSV
df.to_csv('updated_trade_log.csv', index=False)
