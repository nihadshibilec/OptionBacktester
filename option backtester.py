import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

class TradeStrategy:
    def __init__(self, option_data, spot_data, strategy_name, lot_size, unique_dates):
        self.strategy_name = strategy_name
        self.spot_data = spot_data
        self.option_data = option_data
        self.order_log = pd.DataFrame()
        self.expiry_date = None
        self.unique_dates = unique_dates
        self.lot_size = lot_size

    def add_features(self):
        # Converty to daily timeframe
        daily_data = self.spot_data.groupby(self.spot_data['currentdate'].dt.date).agg(currenttime=('currenttime', 'first'),
                    open=('open', 'first'),high=('high', 'max'),low=('low', 'min'),close=('close', 'last'),).reset_index()
        
        # Calculate Pivot and P_R1
        daily_data['yesterdays_low'] = daily_data['low'].shift(1)
        daily_data['yesterdays_high'] = daily_data['high'].shift(1)
        daily_data['Pivot'] = (daily_data['yesterdays_high'] + daily_data['yesterdays_low']) / 2
        daily_data['P_R1'] = (daily_data['Pivot'] * 2) - daily_data['yesterdays_low']
        daily_data['currentdate'] = pd.to_datetime(daily_data['currentdate'])

        merged_df = pd.merge(self.spot_data, daily_data[['currentdate', 'Pivot', 'P_R1']], on='currentdate', how='left')
        merged_df['prev_close'] = merged_df['close'].shift(1)
        merged_df.dropna(subset=['Pivot'], inplace=True)

        self.spot_data = merged_df
        print("Pivot features added to spot data")
    
    def run_strategy(self):
        self.add_features()

        trade_status = False
        total_trade_count = 0
        for date in tqdm(self.unique_dates, total=len(self.unique_dates), desc="Backtesting", ncols=150):
            date = pd.to_datetime(date)
            filtered_option_data = self.option_data[self.option_data['currentdate']==date]
            # print(filtered_option_data)
            filtered_option_data = filtered_option_data.sort_values(by='Expiry_Date')
            self.expiry_date = filtered_option_data['Expiry_Date'].iloc[0]
            filtered_spot_data = self.spot_data[self.spot_data['currentdate']== date]
            filtered_spot_data = filtered_spot_data.reset_index()
            for index, row in filtered_spot_data.iterrows():
                if index == 0: continue # skip the first candle

                if trade_status == True : # If  
                    exit_condition = self.checkExitCriteria(row,trade_id)
                    if exit_condition ==True or index == filtered_spot_data.index.max(): #Exit Trades if exit condition is met or market is closed
                        self.add_exit_orders(row,trade_id)
                        trade_status = False
                
                if trade_status == False or not index == filtered_spot_data.index.max(): #Check for Entry Condition if no trade is active or market is not closed
                    entry_condition = self.checkEntryCriteria(row)
                    if entry_condition == True:
                        total_trade_count += 1
                        trade_id = str(self.strategy_name[:5])+str(total_trade_count)
                        self.add_entry_orders(row,trade_id)
                        trade_status = True
                    
        trades_df = self.convert_orders_to_trades(self.order_log)
        return trades_df
    
    def checkEntryCriteria(self, row):
        P_R1 = row['P_R1']
        current_close = row['close']
        prev_close = row['prev_close']
        if (current_close <= P_R1) and (prev_close > P_R1):
            return True
        if (current_close >= P_R1) and (prev_close < P_R1):
            return True
        if row['currenttime'] =="09:15:00":
            return False
    
    def add_entry_orders(self,row,trade_id):
        entry_date = row['currentdate']
        entry_time = row['currenttime']
        P_R1 = row['P_R1']
        current_close = row['close']
        prev_close = row['prev_close']
        
        if (current_close <= P_R1) and (prev_close > P_R1):
            # Buy PE
            ATM_strike = round(current_close / self.lot_size) * self.lot_size
            OTM_PE_strike = ATM_strike - (self.lot_size * 2)
            quantity_OTM = self.lot_size
            self.add_order(trade_id=trade_id, orderDate = entry_date, orderTime=entry_time, Strike=OTM_PE_strike, option_type='PE', 
                           orderType='buy', quantity=quantity_OTM, expiry_date=self.expiry_date)
        
        if (current_close >= P_R1) and (prev_close < P_R1):
            # Buy CE
            ATM_strike = round(current_close / self.lot_size) * self.lot_size
            OTM_CE_strike = ATM_strike + (self.lot_size * 2)
            quantity_OTM = self.lot_size
            self.add_order(trade_id=trade_id, orderDate = entry_date, orderTime=entry_time, Strike=OTM_CE_strike, option_type='CE', 
                           orderType='buy', quantity=quantity_OTM, expiry_date=self.expiry_date)
        
    def add_order(self, trade_id, orderDate, orderTime, Strike, option_type, orderType, quantity, expiry_date):
        spot_price = self.spot_data[(self.spot_data['currentdate']==orderDate) & (self.spot_data['currenttime']==orderTime) ]['close' ].values[0]
        orderPrice = self.option_data.loc[(self.option_data['strike'] == Strike) & (self.option_data['type'] == option_type) & (self.option_data['currentdate']
                    == orderDate)& (self.option_data['currenttime'] == orderTime) &(self.option_data['Expiry_Date'] == self.expiry_date), 'close'].values[0]
        new_order = {'tradeID': trade_id, 'orderDate': orderDate, 'orderTime': orderTime, 'orderType': orderType, 'optionType': option_type, 'Quantity': quantity,
                    'Strike': Strike, 'orderPrice': orderPrice, 'spotPrice': spot_price, 'Expiry Date': expiry_date}

        self.order_log = pd.concat([self.order_log, pd.DataFrame([new_order])], ignore_index=True)
        
    def add_exit_orders(self, row, trade_id):
        filtered_orders = self.order_log[self.order_log['tradeID'] == trade_id]
        exit_date = row['currentdate']
        exit_time = row['currenttime']
        for _, row in filtered_orders.iterrows():
            exit_order_type = 'sell' if row['orderType'] == 'buy' else 'buy' 
            self.add_order(trade_id=trade_id, orderDate = exit_date, orderTime=exit_time, Strike=row['Strike'], option_type=row['optionType'],
                           orderType=exit_order_type, quantity=-row['Quantity'], expiry_date=row['Expiry Date'])         


    def checkExitCriteria(self, row, trade_id):
        entry_price = self.order_log[self.order_log['tradeID'] == trade_id]['spotPrice'].iloc[0]
        stoploss = entry_price * 0.997
        target = entry_price * 1.003
        current_price = row['close']
        if current_price >= target or current_price <= stoploss:
            return True
        
    def convert_orders_to_trades(self,orders_df):
        grouped = orders_df.groupby(['tradeID', 'Strike', 'optionType', 'Expiry Date'])

        trades = []
        for name, group in grouped:
            entry_orders = group[group['Quantity'] >= 0]
            exit_orders = group[group['Quantity'] < 0]
            if not entry_orders.empty and not exit_orders.empty:
                entry_type = entry_orders['orderType'].values[0]
                quantity = entry_orders['Quantity'].values[0]
                entry_price = entry_orders['orderPrice'].values[0]
                exit_price = exit_orders['orderPrice'].values[0]
                if entry_type == 'buy':
                    PnL = (exit_price - entry_price)*quantity
                else:
                    PnL = (entry_price - exit_price)*quantity
                trade = {
                    'tradeID': name[0],
                    'Strike': name[1],
                    'optionType': name[2],
                    'ExpiryDate': name[3],
                    'EntryType': entry_type,
                    'Quantity': quantity,
                    'EntryDate': entry_orders['orderDate'].values[0],
                    'EntryTime': entry_orders['orderTime'].values[0],
                    'ExitDate': exit_orders['orderDate'].values[0],
                    'ExitTime': exit_orders['orderTime'].values[0],
                    'EntryOrderPrice': entry_price,
                    'ExitOrderPrice': exit_price,
                    'EntrySpotPrice': entry_orders['spotPrice'].values[0],
                    'ExitSpotPrice': exit_orders['spotPrice'].values[0],
                    'PnL' : PnL
                }
                trades.append(trade)

        trades_df = pd.DataFrame(trades)
        trades_df = trades_df.sort_values(by=['EntryDate', 'EntryType'])
        return trades_df
    
    def plot_cumulative_returns(self, trades, capital_per_trade):
        trades['Return'] = trades['PnL']/capital_per_trade
        strategy_returns = trades.groupby('EntryDate')['Return'].sum().reset_index() # Calculate daily return
        daily_data = self.spot_data.groupby('currentdate').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).reset_index()
        daily_data['Return'] = daily_data['close'].pct_change()  # Calculating returns as percentage
        daily_data['Return'] = daily_data['Return'].fillna(0)
        strategy_returns['Benchmark'] = daily_data['Return']
        # Calculate cumulative returns
        strategy_returns['Cumulative_Return'] = strategy_returns['Return'].cumsum()
        strategy_returns['Cumulative_Benchmark'] = strategy_returns['Benchmark'].cumsum()
        # Plotting
        plt.figure(figsize=(10, 6))

        plt.plot(strategy_returns['EntryDate'], strategy_returns['Cumulative_Return'], marker='o', label='Cumulative Return', color='blue')
        plt.plot(strategy_returns['EntryDate'], strategy_returns['Cumulative_Benchmark'], marker='o', label='Cumulative Benchmark', color='red')

        plt.title('Cumulative Return vs. Cumulative Benchmark')
        plt.xlabel('EntryDate')
        plt.ylabel('Cumulative Value')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()
    
    def report(self, trades, capital_per_trade):
        trades['Return'] = trades['PnL']/capital_per_trade
        total_return = trades['Return'].sum()
        wins = (trades['Return'] >= 0).sum()
        loss = (trades['Return'] < 0).sum()
        Winrate = wins/(wins+loss)
        avg_wins = trades.loc[trades['Return'] > 0, 'Return'].mean()
        avg_loss = trades.loc[trades['Return'] < 0, 'Return'].mean()
        
        #Drawdown
        trades['cumulative_return'] = trades['Return'].cumsum()
        drawdown = trades['cumulative_return'] - trades['cumulative_return'].cummax()
        max_drawdown = drawdown.min()

        pnl_to_dd = total_return/-max_drawdown
        print("Total return             : ", str(round(total_return,3)*100) + "%")
        print("Max drawdown             : ", str(round(max_drawdown,3)*100) + "%")
        print("Return/Max drawdown      : ", round(pnl_to_dd,3))
        print("Daily Wins               : ", wins)
        print("Daily losses             : ", loss)
        print("Winrate                  : ", str(round(Winrate,3)*100) + "%")
        print("Average Wins             : ", str(round(avg_wins,3)*100) + "%")
        print("Average losses           : ", str(round(avg_loss,3)*100) + "%")

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

strategy = TradeStrategy(option_data = options_data, spot_data=spot_data, strategy_name="test", lot_size =100, unique_dates = unique_days)
trades = strategy.run_strategy()
strategy.plot_cumulative_returns(trades=trades, capital_per_trade= 300000)
strategy.report(trades, 300000)
