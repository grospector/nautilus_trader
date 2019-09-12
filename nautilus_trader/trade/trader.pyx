# -------------------------------------------------------------------------------------------------
# <copyright file="trader.pyx" company="Nautech Systems Pty Ltd">
#  Copyright (C) 2015-2019 Nautech Systems Pty Ltd. All rights reserved.
#  The use of this source code is governed by the license as found in the LICENSE.md file.
#  https://nautechsystems.io
# </copyright>
# -------------------------------------------------------------------------------------------------

from cpython.datetime cimport datetime
from typing import List

from nautilus_trader.core.correctness cimport Condition
from nautilus_trader.model.commands cimport AccountInquiry
from nautilus_trader.common.logger cimport Logger, LoggerAdapter
from nautilus_trader.common.data cimport DataClient
from nautilus_trader.common.execution cimport ExecutionEngine
from nautilus_trader.trade.strategy cimport TradingStrategy
from nautilus_trader.trade.reports cimport ReportProvider


cdef class Trader:
    """
    Provides a trader for managing a portfolio of trading strategies.
    """

    def __init__(self,
                 TraderId trader_id,
                 AccountId account_id,
                 list strategies,
                 DataClient data_client,
                 ExecutionEngine exec_engine,
                 Clock clock,
                 GuidFactory guid_factory,
                 Logger logger):
        """
        Initializes a new instance of the Trader class.

        :param trader_id: The trader_id for the trader.
        :param trader_id: The account_id for the trader.
        :param strategies: The initial strategies for the trader.
        :param data_client: The data client for the trader.
        :param exec_engine: The execution engine for the trader.
        :param clock: The clock for the trader.
        :param guid_factory: The guid_factory for the trader.
        :param logger: The logger for the trader.
        :raises ConditionFailed: If the trader_id is not equal to the exec_engine.trader_id.
        """
        Condition.equal(trader_id, exec_engine.trader_id)

        self._clock = clock
        self._guid_factory = guid_factory
        self.id = trader_id
        self.account_id = account_id
        self._log = LoggerAdapter(f'Trader-{self.id.value}', logger)
        self._data_client = data_client
        self._exec_engine = exec_engine
        self._report_provider = ReportProvider()

        self.portfolio = self._exec_engine.portfolio
        self.is_running = False
        self.started_datetimes = []  # type: List[datetime]
        self.stopped_datetimes = []  # type: List[datetime]
        self.strategies = None

        self.initialize_strategies(strategies)

    cpdef initialize_strategies(self, list strategies: List[TradingStrategy]):
        """
        Change strategies with the given list of trading strategies.
        
        :param strategies: The list of strategies to load into the trader.
        :raises ConditionFailed: If the strategies list is empty.
        :raises ConditionFailed: If the strategies list contains a type other than TradingStrategy.
        """
        if self.strategies is None:
            self.strategies = []  # type: List[TradingStrategy]
        else:
            Condition.not_empty(strategies, 'strategies')
            Condition.list_type(strategies, TradingStrategy, 'strategies')

        if self.is_running:
            self._log.error('Cannot re-initialize the strategies of a running trader.')
            return

        for strategy in self.strategies:
            # Design assumption that no strategies are running
            assert not strategy.is_running

        # Check strategy_ids are unique
        strategy_ids = set()
        for strategy in strategies:
            if strategy.id not in strategy_ids:
                strategy_ids.add(strategy.id)
            else:
                raise RuntimeError(f'The strategy_id {strategy.id} was not unique '
                                   f'(duplicate strategy_ids).')

        # Dispose of current strategies
        for strategy in self.strategies:
            self._exec_engine.deregister_strategy(strategy)
            strategy.dispose()

        self.strategies.clear()

        # Initialize strategies
        for strategy in strategies:
            strategy.change_logger(self._log.get_logger())
            self.strategies.append(strategy)

        for strategy in self.strategies:
            strategy.register_trader(self.id)
            self._data_client.register_strategy(strategy)
            self._exec_engine.register_strategy(strategy)
            self._log.info(f"Initialized {strategy}.")

    cpdef start(self):
        """
        Start the trader.
        """
        if self.is_running:
            self._log.error(f"Cannot start trader (already running).")
            return

        if len(self.strategies) == 0:
            self._log.error(f"Cannot start trader (no strategies loaded).")
            return

        self._log.info("Starting...")
        self.started_datetimes.append(self._clock.time_now())

        # TODO: Implement below
        # cdef AccountInquiry account_inquiry = AccountInquiry(
        #     account_id=self.account_id,
        #     command_id=self._guid_factory.generate(),
        #     command_timestamp=self._clock.time_now())
        #
        # self._exec_engine.execute_command(account_inquiry)

        for strategy in self.strategies:
            strategy.start()

        self.is_running = True
        self._log.info("Running...")

    cpdef stop(self):
        """
        Stop the trader.
        """
        if not self.is_running:
            self._log.error(f"Cannot stop trader (already stopped).")
            return

        self.stopped_datetimes.append(self._clock.time_now())

        self._log.info("Stopping...")
        for strategy in self.strategies:
            strategy.stop()

        self.is_running = False
        self._log.info("Stopped.")
        self._exec_engine.check_residuals()

    cpdef reset(self):
        """
        Reset the trader by returning all stateful internal values of the portfolio, 
        and every strategy to their initial value.
        
        Note: The trader cannot be running otherwise an error is logged.
        """
        if self.is_running:
            self._log.error(f"Cannot reset trader (trader must be stopped to reset).")
            return

        self._log.debug("Resetting...")
        for strategy in self.strategies:
            strategy.reset()

        self.portfolio.reset()
        self._log.info("Reset.")

    cpdef dispose(self):
        """
        Dispose of the trader.
        """
        self._log.debug("Disposing...")
        for strategy in self.strategies:
            strategy.dispose()

        self._log.info("Disposed.")

    cpdef dict strategy_status(self):
        """
        Return a dictionary containing the traders strategy status.
        The key is the strategy_id.
        The value is a bool which is True if the strategy is running else False.
        
        :return Dict[StrategyId, bool].
        """
        cdef status = {}
        for strategy in self.strategies:
            if strategy.is_running:
                status[strategy.id] = True
            else:
                status[strategy.id] = False

        return status

    cpdef void create_returns_tear_sheet(self):
        """
        Create a returns tear sheet based on analyzer data from the last run.
        """
        self.portfolio.analyzer.create_returns_tear_sheet()

    cpdef void create_full_tear_sheet(self):
        """
        Create a full tear sheet based on analyzer data from the last run.
        """
        self.portfolio.analyzer.create_full_tear_sheet()

    cpdef object get_orders_report(self):
        """
        Return an orders report dataframe.

        :return pd.DataFrame.
        """
        return self._report_provider.get_orders_report(self._exec_engine.database.get_orders())

    cpdef object get_order_fills_report(self):
        """
        Return an order fills report dataframe.
        
        :return pd.DataFrame.
        """
        return self._report_provider.get_order_fills_report(self._exec_engine.database.get_orders())

    cpdef object get_positions_report(self):
        """
        Return a positions report dataframe.

        :return pd.DataFrame.
        """
        return self._report_provider.get_positions_report(self._exec_engine.database.get_positions())
