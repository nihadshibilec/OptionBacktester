# OptionBacktester
This Python script implements an options backtesting framework for evaluating trading strategies based on historical market data. It allows users to simulate trading strategies on options contracts, assessing their performance under various market conditions.

Installation
------------
1. Clone this repository:
```
git clone https://github.com/your-username/trade-strategy.git
```

2. Install the required Python packages:
```
pip install pandas tqdm
```

**File Structure**
---
> trade_strategy.py: Contains the implementation of the TradeStrategy class.
---
> sample_spot_data.csv: Sample market data for testing the script.


sample_options_data.csv: Sample options data for testing the script.
Implementation Details
---
>TradeStrategy Class:
This class contains methods for adding features to market data, running the trade strategy, checking entry and exit criteria, and converting orders to trades.
add_features() Method:
Adds pivot point features to the spot data.
run_strategy() Method:
Executes the trade strategy based on specified criteria.
checkEntryCriteria() Method: Checks if the current market conditions meet the criteria for entering a trade.
add_entry_orders() Method: Places orders for entering a trade based on the current market conditions.
checkExitCriteria() Method: Checks if the current market conditions meet the criteria for exiting a trade.
add_exit_orders() Method: Places orders for exiting a trade based on the current market conditions.
convert_orders_to_trades() Method: Converts orders placed during the strategy execution into trades.
Contributing
Contributions are welcome! Feel free to submit pull requests or open issues.

License
This project is licensed under the MIT License.
