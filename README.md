# OptionBacktester 

Welcome to the Options Strategy Backtesting System! This project implements a backtesting system for trading strategies using Python.


## Installation
1. Clone this repository:
```
git clone https://github.com/nihadshibilec/OptionBacktester.git
```

2. Install the required Python packages:
```
pip install pandas tqdm
```

## File Structure
- **OptionBacktester.py:** Contains the implementation of the TradeStrategy class.
- **sample_spot_data.csv:** Sample market data for testing the script.
- **sample_options_data.csv:** Sample options data for testing the script. (not uploaded due to size limit) here's the link to dataset: https://www.kaggle.com/datasets/nihadshibil/sample-options-data

Implementation Details
---
- `TradeStrategy Class:`
This class contains methods for adding features to market data, running the trade strategy, checking entry and exit criteria, and converting orders to trades.
- `add_features() Method:`
Adds pivot point features to the spot data.
- `run_strategy() Method:`
Executes the trade strategy based on specified criteria.
- `checkEntryCriteria() Method:` Checks if the current market conditions meet the criteria for entering a trade.
- `add_entry_orders() Method:` Places orders for entering a trade based on the current market conditions.
- `checkExitCriteria() Method:` Checks if the current market conditions meet the criteria for exiting a trade.
- `add_exit_orders() Method:` Places orders for exiting a trade based on the current market conditions.
- `convert_orders_to_trades() Method:` Converts orders placed during the strategy execution into trades.
- `plot_cumulative_returns() Method:` Plot return of trades and benchmark.
- `report() Method:` Prints the basic reports of trades.

### Additional Tips

- If you want to change the time frame of data for backtesting, add this code to add_features function:
```
timeframe = '5min' # use '1D' for daily timeframe, 60min for hourly timeframe
self.spot_data['currentdatetime'] = pd.to_datetime(self.spot_data['currentdate'] + ' ' + self.spot_data['currenttime'])
self.spot_data.set_index('currentdatetime', inplace=True)
self.spot_data = self.spot_data.resample(timeframe).agg({'currentdate': 'first','currenttime': 'first','open': 'first','high': 'max','low': 'min','close': 'last'}).reset_index()
self.spot_data.drop(columns='currentdatetime', inplace=True)
print("spot data converted to", timeframe, "timeframe")
```

### Contributing
Contributions are welcome! Feel free to submit pull requests or open issues.
### License
This project is licensed under the MIT License.
