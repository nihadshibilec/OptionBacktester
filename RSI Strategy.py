from option_backtester import TradeStrategy
import pandas as pd
from tqdm import tqdm
import pandas_ta as ta

class RSIOptionStrategy(TradeStrategy):
    def __init__(self, option_data, spot_data, strategy_name, lot_size, unique_dates):
        super().__init__(option_data, spot_data, strategy_name, lot_size, unique_dates)

    def add_features(self):
        self.spot_data['RSI'] = ta.rsi(self.spot_data['close'], length=14)
        print("Added RSI feature to spot data")

    def checkEntryCriteria(self, row):
        if row['RSI'] >= 70:
            return True
    
    def add_entry_orders(self,row,trade_id):
        entry_date = row['currentdate']
        entry_time = row['currenttime']
        current_close = row['close']
        ATM_strike = round(current_close / self.lot_size) * self.lot_size
        quantity = self.lot_size

        self.add_order(trade_id=trade_id, orderDate = entry_date, orderTime=entry_time, Strike=ATM_strike, option_type='PE', 
                        orderType='buy', quantity=quantity, expiry_date=self.expiry_date)
        
### Processing Market Data ### 
spot_file_path = "sample_spot_data.csv"
option_data_file_path = "sample_options_data.csv"
spot_data = pd.read_csv(spot_file_path)
spot_data['currentdate'] = pd.to_datetime(spot_data['currentdate'])
options_data = pd.read_csv(option_data_file_path)
options_data['currentdate'] = pd.to_datetime(options_data['currentdate'])
options_data['Expiry_Date'] = pd.to_datetime(options_data['Expiry_Date'])
################################################################

unique_days=spot_data['currentdate'].dt.date.unique()

rsi_strategy = RSIOptionStrategy(option_data=options_data, spot_data=spot_data, strategy_name="RSI", lot_size=100, unique_dates=unique_days)
trades = rsi_strategy.run_strategy()
rsi_strategy.plot_cumulative_returns(trades= trades, capital_per_trade = 100000)
rsi_strategy.report(trades , 100000)
