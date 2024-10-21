import MetaTrader5 as mt5
import pandas as pd
import time

# Trading parameters
SYMBOLS = ["BTCUSD", "ETHUSD"]
LOT_SIZE = 0.1
SLIPPAGE = 10
MAGIC_NUMBER = 123456
STOP_LOSS_MULTIPLIER = 1.5  # Adjusted for ATR
TAKE_PROFIT_MULTIPLIER = 2.0  # Adjusted for ATR
TIMEFRAME = mt5.TIMEFRAME_M15  # 15-minute timeframe

# Initialize MetaTrader 5 connection
if not mt5.initialize():
    print("Initialization failed")
    mt5.shutdown()

# Function to get price data
def get_data(symbol, timeframe, num_bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    return data

# Function to calculate EMA
def calculate_ema(data, period=50):
    return data['close'].ewm(span=period, adjust=False).mean()

# Function to calculate ATR
def calculate_atr(data, period=14):
    data['tr'] = data[['high', 'low', 'close']].apply(
        lambda row: max(row['high'] - row['low'], 
                        abs(row['high'] - row['close']), 
                        abs(row['low'] - row['close'])), axis=1)
    return data['tr'].rolling(window=period).mean()

# Function to check if there is an open position
def is_position_open(symbol):
    positions = mt5.positions_get(symbol=symbol)
    return len(positions) > 0  # Returns True if there are open positions for the symbol

# Function to check minimum stop level
def get_minimum_stop_level(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol info not found for {symbol}")
        return None
    return symbol_info.trade_stops_level * symbol_info.point

# Function to execute trades
def execute_trade(symbol, action, price, sl, tp):
    min_stop_level = get_minimum_stop_level(symbol)
    if min_stop_level is None:
        print(f"Cannot retrieve stop level info for {symbol}")
        return None

    # Check if stop loss or take profit is too close to the price
    if abs(price - sl) < min_stop_level:
        sl = price - min_stop_level if action == "buy" else price + min_stop_level
    if abs(price - tp) < min_stop_level:
        tp = price + min_stop_level if action == "buy" else price - min_stop_level

    request = {
        'action': mt5.TRADE_ACTION_DEAL,
        'symbol': symbol,
        'volume': LOT_SIZE,
        'type': mt5.ORDER_TYPE_BUY if action == "buy" else mt5.ORDER_TYPE_SELL,
        'price': price,
        'sl': sl,
        'tp': tp,
        'deviation': SLIPPAGE,
        'magic': MAGIC_NUMBER,
        'comment': 'Strategy Trade',
        'type_time': mt5.ORDER_TIME_GTC,
        'type_filling': mt5.ORDER_FILLING_IOC
    }
    result = mt5.order_send(request)
    return result

# Trading logic
while True:
    for SYMBOL in SYMBOLS:
        data = get_data(SYMBOL, TIMEFRAME, 100)  # Using 15-minute timeframe
        data['ema50'] = calculate_ema(data)
        data['atr'] = calculate_atr(data)

        # Apply trading strategy logic
        for i in range(1, len(data)):
            if not is_position_open(SYMBOL):
                if data['close'][i] > data['ema50'][i] and data['close'][i-1] <= data['ema50'][i-1]:
                    # Buy signal: Price broke above 50 EMA
                    sl = data['close'][i] - (STOP_LOSS_MULTIPLIER * data['atr'][i])
                    tp = data['close'][i] + (TAKE_PROFIT_MULTIPLIER * data['atr'][i])
                    result = execute_trade(SYMBOL, "buy", data['close'][i], sl, tp)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"Buy trade executed for {SYMBOL} at {data['close'][i]} with SL={sl} and TP={tp}")
                    else:
                        print(f"Failed to execute buy trade for {SYMBOL}. Error code: {result.retcode} and comment: {result.comment}")

                elif data['close'][i] < data['ema50'][i] and data['close'][i-1] >= data['ema50'][i-1]:
                    # Sell signal: Price broke below 50 EMA
                    sl = data['close'][i] + (STOP_LOSS_MULTIPLIER * data['atr'][i])
                    tp = data['close'][i] - (TAKE_PROFIT_MULTIPLIER * data['atr'][i])
                    result = execute_trade(SYMBOL, "sell", data['close'][i], sl, tp)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"Sell trade executed for {SYMBOL} at {data['close'][i]} with SL={sl} and TP={tp}")
                    else:
                        print(f"Failed to execute sell trade for {SYMBOL}. Error code: {result.retcode} and comment: {result.comment}")
            else:
                print(f"Position already open for {SYMBOL}. No new trade executed.")
                break  # Exit the loop once a trade has been executed to prevent further trade attempts in this iteration.

    time.sleep(60 * 15)  # Wait 15 minutes for the next iteration
