#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2025 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import time
from decimal import Decimal

import pandas as pd

from examples.utils.data_provider import prepare_demo_data_eurusd_futures_1min
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.engine import BacktestEngineConfig
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import RiskEngineConfig
from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType
from nautilus_trader.model.enums import OmsType
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money


if __name__ == "__main__":
    print("🚀 Starting EUR/USD Backtest with EMA Cross Strategy")
    print("=" * 60)
    
    # ----------------------------------------------------------------------------------
    # 1. Configure backtest engine
    # ----------------------------------------------------------------------------------
    
    config = BacktestEngineConfig(
        trader_id=TraderId("EURUSD-BACKTEST-001"),
        logging=LoggingConfig(
            log_level="INFO",
            log_file_format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
            log_colors=True,
        ),
        risk_engine=RiskEngineConfig(
            bypass=True,  # Bypass pre-trade risk checks for backtests
        ),
    )

    # Build backtest engine
    engine = BacktestEngine(config=config)

    # ----------------------------------------------------------------------------------
    # 2. Prepare EUR/USD market data
    # ----------------------------------------------------------------------------------
    
    print("📊 Loading EUR/USD futures data...")
    prepared_data = prepare_demo_data_eurusd_futures_1min()
    
    venue_name = prepared_data["venue_name"]
    eurusd_instrument = prepared_data["instrument"]
    eurusd_1min_bartype = prepared_data["bar_type"]
    eurusd_1min_bars = prepared_data["bars_list"]
    
    print(f"✅ Loaded {len(eurusd_1min_bars)} bars for {eurusd_instrument.id}")
    print(f"📈 Data period: {eurusd_1min_bars[0].ts_init} to {eurusd_1min_bars[-1].ts_init}")

    # ----------------------------------------------------------------------------------
    # 3. Configure trading environment
    # ----------------------------------------------------------------------------------
    
    # Create a fill model for realistic execution simulation
    fill_model = FillModel(
        prob_fill_on_limit=0.8,    # 80% probability of limit order fills
        prob_fill_on_stop=0.95,    # 95% probability of stop order fills
        prob_slippage=0.1,         # 10% probability of slippage
        random_seed=42,            # For reproducible results
    )

    # Add trading venue
    venue = Venue(venue_name)
    engine.add_venue(
        venue=venue,
        oms_type=OmsType.NETTING,           # Use netting for forex
        account_type=AccountType.MARGIN,     # Margin account for leverage
        base_currency=USD,                   # Account currency
        starting_balances=[Money(100_000, USD)],  # Starting capital: $100,000
        default_leverage=Decimal(10),        # 10:1 leverage
        fill_model=fill_model,
        bar_execution=True,                  # Enable bar-based execution
    )

    # Add instrument
    engine.add_instrument(eurusd_instrument)

    # Add historical data
    engine.add_data(eurusd_1min_bars)

    # ----------------------------------------------------------------------------------
    # 4. Configure EMA Cross Strategy
    # ----------------------------------------------------------------------------------
    
    # Create 5-minute bars from 1-minute data for strategy execution
    strategy_bar_type = BarType.from_str(f"{eurusd_instrument.id}-5-MINUTE-LAST-EXTERNAL")
    
    # Configure EMA Cross strategy
    strategy_config = EMACrossConfig(
        instrument_id=eurusd_instrument.id,
        bar_type=strategy_bar_type,
        fast_ema_period=12,         # Fast EMA period
        slow_ema_period=26,         # Slow EMA period
        trade_size=Decimal(10000),  # 10,000 EUR contract size
        order_id_tag="EURUSD-EMA",  # Tag for order identification
    )
    
    # Instantiate strategy
    strategy = EMACross(config=strategy_config)
    engine.add_strategy(strategy=strategy)

    print(f"⚡ Strategy configured: EMA Cross ({strategy_config.fast_ema_period}/{strategy_config.slow_ema_period})")
    print(f"💰 Starting capital: ${100_000:,}")
    print(f"🔧 Leverage: {10}:1")
    print(f"📊 Strategy bar type: {strategy_bar_type}")

    # ----------------------------------------------------------------------------------
    # 5. Run backtest
    # ----------------------------------------------------------------------------------
    
    print("\n🎯 Starting backtest execution...")
    print("Press Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ Backtest cancelled by user")
        engine.dispose()
        exit(0)

    # Record start time
    start_time = time.time()
    
    # Run the backtest
    engine.run()
    
    # Record end time
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\n✅ Backtest completed in {execution_time:.2f} seconds")

    # ----------------------------------------------------------------------------------
    # 6. Generate reports
    # ----------------------------------------------------------------------------------
    
    print("\n📈 BACKTEST RESULTS")
    print("=" * 60)
    
    # Account report
    with pd.option_context(
        "display.max_rows", 100,
        "display.max_columns", None,
        "display.width", 300,
    ):
        print("\n💼 ACCOUNT SUMMARY:")
        print(engine.trader.generate_account_report(venue))
        
        print("\n📋 ORDER FILLS:")
        fills_report = engine.trader.generate_order_fills_report()
        if not fills_report.empty:
            print(fills_report)
        else:
            print("No fills executed during backtest period")
        
        print("\n📊 POSITIONS:")
        positions_report = engine.trader.generate_positions_report()
        if not positions_report.empty:
            print(positions_report)
        else:
            print("No positions opened during backtest period")

    # ----------------------------------------------------------------------------------
    # 7. Performance Analysis
    # ----------------------------------------------------------------------------------
    
    print("\n🎯 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    # Get account statistics
    account = engine.trader.get_account(venue)
    if account:
        total_pnl = account.calculate_pnl_total()
        balance = account.balance_total()
        
        print(f"📊 Total P&L: {total_pnl}")
        print(f"💰 Final Balance: {balance}")
        print(f"📈 Return: {((float(balance.raw) / 100_000) - 1) * 100:.2f}%")
        
        # Calculate some basic statistics
        fills_df = engine.trader.generate_order_fills_report()
        if not fills_df.empty:
            total_trades = len(fills_df)
            print(f"🔄 Total Trades: {total_trades}")
            print(f"⏱️  Average Trades per Hour: {total_trades / (len(eurusd_1min_bars) / 60):.2f}")
    
    print(f"\n⚡ Execution Time: {execution_time:.2f} seconds")
    print(f"📊 Bars Processed: {len(eurusd_1min_bars):,}")
    print(f"🔧 Processing Speed: {len(eurusd_1min_bars) / execution_time:.0f} bars/second")

    # ----------------------------------------------------------------------------------
    # 8. Cleanup
    # ----------------------------------------------------------------------------------
    
    print("\n🔄 Cleaning up resources...")
    
    # Reset engine for potential future runs
    engine.reset()
    
    # Dispose of engine
    engine.dispose()
    
    print("✅ EUR/USD Backtest completed successfully!")
    print("=" * 60)