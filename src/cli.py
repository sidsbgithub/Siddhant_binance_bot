"""Command-line interface for the trading bot."""

from typing import Optional
from src.config import Config, ConfigurationError
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.validator import InputValidator, ValidationError
from src.logger import BotLogger
from src.market_orders import MarketOrderManager
from src.limit_orders import LimitOrderManager
from src.stop_limit_orders import StopLimitOrderManager
from src.advanced.oco import OCOOrderManager
from src.advanced.twap import TWAPStrategy
from src.advanced.grid import GridStrategy


class TradingBotCLI:
    """
    Command-line interface for the trading bot.
    Provides interactive menu and command handling for order execution.
    """
    
    def __init__(self, config: Config):
        """
        Initialize CLI with configuration.
        
        Args:
            config: Configuration object with API credentials.
        """
        self.config = config
        self.logger: Optional[BotLogger] = None
        self.client: Optional[BinanceClient] = None
        self.validator: Optional[InputValidator] = None
        self.market_manager: Optional[MarketOrderManager] = None
        self.limit_manager: Optional[LimitOrderManager] = None
        self.stop_limit_manager: Optional[StopLimitOrderManager] = None
        self.oco_manager: Optional[OCOOrderManager] = None
        self.twap_strategy: Optional[TWAPStrategy] = None
        self.grid_strategy: Optional[GridStrategy] = None
        self.running = False
    
    def initialize(self) -> None:
        """
        Initialize all components (logger, client, validator, managers).
        
        Raises:
            ConfigurationError: If configuration is invalid.
            ConnectionError: If connection to Binance fails.
        """
        print("\n" + "="*60)
        print("  Binance Futures Trading Bot - Initializing...")
        print("="*60)
        
        # Initialize logger
        print("\n[1/5] Setting up logger...")
        self.logger = BotLogger(
            log_file=self.config.log_file,
            log_level=self.config.log_level
        )
        self.logger.info('TradingBotCLI', 'Trading bot starting up', {
            'testnet': self.config.testnet,
            'log_file': self.config.log_file
        })
        print(f"✓ Logger initialized (log file: {self.config.log_file})")
        
        # Initialize Binance client
        print("\n[2/5] Connecting to Binance...")
        self.client = BinanceClient(self.config, self.logger)
        print(f"✓ Connected to {'Testnet' if self.config.testnet else 'Production'}")
        
        # Test connection
        print("\n[3/5] Testing API connection...")
        if self.client.test_connection():
            print("✓ API connection successful")
        
        # Initialize validator
        print("\n[4/5] Initializing input validator...")
        self.validator = InputValidator(self.client)
        print("✓ Validator ready")
        
        # Initialize order managers
        print("\n[5/5] Setting up order managers...")
        self.market_manager = MarketOrderManager(
            self.client,
            self.validator,
            self.logger
        )
        self.limit_manager = LimitOrderManager(
            self.client,
            self.validator,
            self.logger
        )
        self.stop_limit_manager = StopLimitOrderManager(
            self.client,
            self.validator,
            self.logger
        )
        self.oco_manager = OCOOrderManager(
            self.client,
            self.validator,
            self.logger
        )
        self.twap_strategy = TWAPStrategy(
            self.client,
            self.logger
        )
        self.grid_strategy = GridStrategy(
            self.client,
            self.logger
        )
        print("✓ Order managers ready")
        
        print("\n" + "="*60)
        print("  Initialization Complete!")
        print("="*60)
        
        self.logger.info('TradingBotCLI', 'Bot initialization complete')
    
    def start(self) -> None:
        """
        Start the CLI interface.
        Displays menu and handles user commands in a loop.
        """
        self.running = True
        
        print("\n")
        print("Welcome to Binance Futures Trading Bot!")
        print("Type 'help' for available commands or 'quit' to exit.\n")
        
        while self.running:
            try:
                command = input("bot> ").strip().lower()
                
                if not command:
                    continue
                
                self.handle_command(command)
                
            except KeyboardInterrupt:
                print("\n\nReceived interrupt signal. Exiting...")
                self.running = False
            except EOFError:
                print("\n\nExiting...")
                self.running = False
            except Exception as e:
                print(f"\n✗ Unexpected error: {str(e)}")
                if self.logger:
                    self.logger.log_error(e, {
                        'component': 'TradingBotCLI',
                        'action': 'command_loop'
                    })
        
        print("\nThank you for using Binance Futures Trading Bot!")
        if self.logger:
            self.logger.info('TradingBotCLI', 'Bot shutting down')
    
    def display_menu(self) -> None:
        """Display available commands and usage instructions."""
        print("\n" + "="*60)
        print("  AVAILABLE COMMANDS")
        print("="*60)
        print("\nOrder Commands:")
        print("  market      - Execute a market order")
        print("  limit       - Place a limit order")
        print("  stop-limit  - Place a stop-limit order")
        print("  oco         - Place an OCO (One-Cancels-Other) order")
        print("  twap        - Execute a TWAP (Time-Weighted Average Price) strategy")
        print("  grid        - Start a Grid trading strategy")
        print("  stop-grid   - Stop the active Grid trading strategy")
        print("\nUtility Commands:")
        print("  help    - Display this help message")
        print("  menu    - Display this menu")
        print("  quit    - Exit the bot")
        print("  exit    - Exit the bot")
        print("\nExamples:")
        print("  bot> market")
        print("  bot> limit")
        print("  bot> stop-limit")
        print("  bot> oco")
        print("  bot> twap")
        print("  bot> grid")
        print("  bot> stop-grid")
        print("  bot> help")
        print("="*60 + "\n")
    
    def handle_command(self, command: str) -> None:
        """
        Parse and execute user command.
        
        Args:
            command: User command string.
        """
        if command in ['help', 'menu', '?']:
            self.display_menu()
        
        elif command in ['quit', 'exit', 'q']:
            print("\nExiting...")
            self.running = False
        
        elif command == 'market':
            self.prompt_market_order()
        
        elif command == 'limit':
            self.prompt_limit_order()
        
        elif command in ['stop-limit', 'stoplimit', 'stop_limit']:
            self.prompt_stop_limit_order()
        
        elif command == 'oco':
            self.prompt_oco_order()
        
        elif command == 'twap':
            self.prompt_twap_strategy()
        
        elif command == 'grid':
            self.prompt_grid_strategy()
        
        elif command in ['stop-grid', 'stopgrid', 'stop_grid']:
            self.stop_grid_strategy()
        
        else:
            print(f"\n✗ Unknown command: '{command}'")
            print("Type 'help' to see available commands.\n")
    
    def prompt_market_order(self) -> None:
        """
        Interactive prompt for market order input.
        Collects symbol, side, and quantity from user and executes the order.
        """
        print("\n" + "-"*60)
        print("  MARKET ORDER")
        print("-"*60)
        
        try:
            # Get symbol
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            if not symbol:
                print("✗ Symbol cannot be empty")
                return
            
            # Get side
            side = input("Side (BUY/SELL): ").strip().upper()
            if not side:
                print("✗ Side cannot be empty")
                return
            
            # Get quantity
            quantity_str = input("Quantity: ").strip()
            if not quantity_str:
                print("✗ Quantity cannot be empty")
                return
            
            try:
                quantity = float(quantity_str)
            except ValueError:
                print(f"✗ Invalid quantity: '{quantity_str}' is not a valid number")
                return
            
            # Confirm order
            print(f"\n📋 Order Summary:")
            print(f"   Type: MARKET")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Quantity: {quantity}")
            
            confirm = input("\nConfirm order? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ Order cancelled")
                return
            
            # Execute order
            print("\n⏳ Executing market order...")
            result = self.market_manager.execute(symbol, side, quantity)
            
            # Display result
            self.display_order_result(result, 'MARKET')
            
        except ValidationError as e:
            print(f"\n✗ Validation Error: {str(e)}")
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'prompt_market_order'
                })
    
    def prompt_limit_order(self) -> None:
        """
        Interactive prompt for limit order input.
        Collects symbol, side, quantity, and price from user and executes the order.
        """
        print("\n" + "-"*60)
        print("  LIMIT ORDER")
        print("-"*60)
        
        try:
            # Get symbol
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            if not symbol:
                print("✗ Symbol cannot be empty")
                return
            
            # Get side
            side = input("Side (BUY/SELL): ").strip().upper()
            if not side:
                print("✗ Side cannot be empty")
                return
            
            # Get quantity
            quantity_str = input("Quantity: ").strip()
            if not quantity_str:
                print("✗ Quantity cannot be empty")
                return
            
            try:
                quantity = float(quantity_str)
            except ValueError:
                print(f"✗ Invalid quantity: '{quantity_str}' is not a valid number")
                return
            
            # Get price
            price_str = input("Price: ").strip()
            if not price_str:
                print("✗ Price cannot be empty")
                return
            
            try:
                price = float(price_str)
            except ValueError:
                print(f"✗ Invalid price: '{price_str}' is not a valid number")
                return
            
            # Confirm order
            print(f"\n📋 Order Summary:")
            print(f"   Type: LIMIT")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Quantity: {quantity}")
            print(f"   Price: {price}")
            
            confirm = input("\nConfirm order? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ Order cancelled")
                return
            
            # Execute order
            print("\n⏳ Placing limit order...")
            result = self.limit_manager.execute(symbol, side, quantity, price)
            
            # Display result
            self.display_order_result(result, 'LIMIT')
            
        except ValidationError as e:
            print(f"\n✗ Validation Error: {str(e)}")
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'prompt_limit_order'
                })
    
    def prompt_stop_limit_order(self) -> None:
        """
        Interactive prompt for stop-limit order input.
        Collects symbol, side, quantity, stop price, and limit price from user and executes the order.
        """
        print("\n" + "-"*60)
        print("  STOP-LIMIT ORDER")
        print("-"*60)
        
        try:
            # Get symbol
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            if not symbol:
                print("✗ Symbol cannot be empty")
                return
            
            # Get side
            side = input("Side (BUY/SELL): ").strip().upper()
            if not side:
                print("✗ Side cannot be empty")
                return
            
            # Get quantity
            quantity_str = input("Quantity: ").strip()
            if not quantity_str:
                print("✗ Quantity cannot be empty")
                return
            
            try:
                quantity = float(quantity_str)
            except ValueError:
                print(f"✗ Invalid quantity: '{quantity_str}' is not a valid number")
                return
            
            # Get stop price
            stop_price_str = input("Stop Price (trigger price): ").strip()
            if not stop_price_str:
                print("✗ Stop price cannot be empty")
                return
            
            try:
                stop_price = float(stop_price_str)
            except ValueError:
                print(f"✗ Invalid stop price: '{stop_price_str}' is not a valid number")
                return
            
            # Get limit price
            limit_price_str = input("Limit Price (execution price): ").strip()
            if not limit_price_str:
                print("✗ Limit price cannot be empty")
                return
            
            try:
                limit_price = float(limit_price_str)
            except ValueError:
                print(f"✗ Invalid limit price: '{limit_price_str}' is not a valid number")
                return
            
            # Confirm order
            print(f"\n📋 Order Summary:")
            print(f"   Type: STOP-LIMIT")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Quantity: {quantity}")
            print(f"   Stop Price: {stop_price}")
            print(f"   Limit Price: {limit_price}")
            
            confirm = input("\nConfirm order? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ Order cancelled")
                return
            
            # Execute order
            print("\n⏳ Placing stop-limit order...")
            result = self.stop_limit_manager.execute(
                symbol, side, quantity, stop_price, limit_price
            )
            
            # Display result
            self.display_order_result(result, 'STOP-LIMIT')
            
        except ValidationError as e:
            print(f"\n✗ Validation Error: {str(e)}")
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'prompt_stop_limit_order'
                })
    
    def prompt_oco_order(self) -> None:
        """
        Interactive prompt for OCO order input.
        Collects symbol, side, quantity, price, stop price, and stop limit price from user and executes the order.
        """
        print("\n" + "-"*60)
        print("  OCO (ONE-CANCELS-OTHER) ORDER")
        print("-"*60)
        print("\nOCO orders place two orders simultaneously:")
        print("  1. A limit order at your target price")
        print("  2. A stop-limit order for risk management")
        print("When one order fills, the other is automatically cancelled.\n")
        
        try:
            # Get symbol
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            if not symbol:
                print("✗ Symbol cannot be empty")
                return
            
            # Get side
            side = input("Side (BUY/SELL): ").strip().upper()
            if not side:
                print("✗ Side cannot be empty")
                return
            
            # Get quantity
            quantity_str = input("Quantity: ").strip()
            if not quantity_str:
                print("✗ Quantity cannot be empty")
                return
            
            try:
                quantity = float(quantity_str)
            except ValueError:
                print(f"✗ Invalid quantity: '{quantity_str}' is not a valid number")
                return
            
            # Get limit price
            price_str = input("Limit Price (take profit): ").strip()
            if not price_str:
                print("✗ Limit price cannot be empty")
                return
            
            try:
                price = float(price_str)
            except ValueError:
                print(f"✗ Invalid price: '{price_str}' is not a valid number")
                return
            
            # Get stop price
            stop_price_str = input("Stop Price (trigger price): ").strip()
            if not stop_price_str:
                print("✗ Stop price cannot be empty")
                return
            
            try:
                stop_price = float(stop_price_str)
            except ValueError:
                print(f"✗ Invalid stop price: '{stop_price_str}' is not a valid number")
                return
            
            # Get stop limit price
            stop_limit_price_str = input("Stop Limit Price (execution price): ").strip()
            if not stop_limit_price_str:
                print("✗ Stop limit price cannot be empty")
                return
            
            try:
                stop_limit_price = float(stop_limit_price_str)
            except ValueError:
                print(f"✗ Invalid stop limit price: '{stop_limit_price_str}' is not a valid number")
                return
            
            # Confirm order
            print(f"\n📋 Order Summary:")
            print(f"   Type: OCO (One-Cancels-Other)")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Quantity: {quantity}")
            print(f"   Limit Price: {price}")
            print(f"   Stop Price: {stop_price}")
            print(f"   Stop Limit Price: {stop_limit_price}")
            
            confirm = input("\nConfirm order? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ Order cancelled")
                return
            
            # Execute order
            print("\n⏳ Placing OCO order...")
            result = self.oco_manager.execute(
                symbol, side, quantity, price, stop_price, stop_limit_price
            )
            
            # Display result
            self.display_order_result(result, 'OCO')
            
        except ValidationError as e:
            print(f"\n✗ Validation Error: {str(e)}")
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'prompt_oco_order'
                })
    
    def prompt_twap_strategy(self) -> None:
        """
        Interactive prompt for TWAP strategy input.
        Collects symbol, side, total quantity, duration, and intervals from user and executes the strategy.
        """
        print("\n" + "-"*60)
        print("  TWAP (TIME-WEIGHTED AVERAGE PRICE) STRATEGY")
        print("-"*60)
        print("\nTWAP splits a large order into smaller chunks executed")
        print("at regular time intervals to minimize market impact.\n")
        
        try:
            # Get symbol
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            if not symbol:
                print("✗ Symbol cannot be empty")
                return
            
            # Get side
            side = input("Side (BUY/SELL): ").strip().upper()
            if not side:
                print("✗ Side cannot be empty")
                return
            
            # Get total quantity
            total_quantity_str = input("Total Quantity: ").strip()
            if not total_quantity_str:
                print("✗ Total quantity cannot be empty")
                return
            
            try:
                total_quantity = float(total_quantity_str)
            except ValueError:
                print(f"✗ Invalid total quantity: '{total_quantity_str}' is not a valid number")
                return
            
            # Get duration
            duration_str = input("Duration (minutes): ").strip()
            if not duration_str:
                print("✗ Duration cannot be empty")
                return
            
            try:
                duration_minutes = int(duration_str)
            except ValueError:
                print(f"✗ Invalid duration: '{duration_str}' is not a valid number")
                return
            
            # Get intervals (optional)
            intervals_str = input(f"Number of intervals (default: {duration_minutes}): ").strip()
            if intervals_str:
                try:
                    intervals = int(intervals_str)
                except ValueError:
                    print(f"✗ Invalid intervals: '{intervals_str}' is not a valid number")
                    return
            else:
                intervals = duration_minutes
            
            # Calculate interval details
            interval_quantity = total_quantity / intervals
            interval_seconds = (duration_minutes * 60) / intervals
            
            # Confirm strategy
            print(f"\n📋 TWAP Strategy Summary:")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Total Quantity: {total_quantity}")
            print(f"   Duration: {duration_minutes} minutes")
            print(f"   Intervals: {intervals}")
            print(f"   Quantity per interval: {interval_quantity:.8f}")
            print(f"   Time between orders: {interval_seconds:.2f} seconds")
            
            confirm = input("\nConfirm TWAP execution? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ TWAP execution cancelled")
                return
            
            # Execute TWAP strategy
            print(f"\n⏳ Executing TWAP strategy ({intervals} intervals over {duration_minutes} minutes)...")
            print("   This may take a while. Please wait...\n")
            
            executed_orders = self.twap_strategy.execute(
                symbol=symbol,
                side=side,
                total_quantity=total_quantity,
                duration_minutes=duration_minutes,
                intervals=intervals
            )
            
            # Display results
            self.display_twap_result(executed_orders, symbol, side, total_quantity)
            
        except ValidationError as e:
            print(f"\n✗ Validation Error: {str(e)}")
        except ValueError as e:
            print(f"\n✗ Invalid Input: {str(e)}")
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'prompt_twap_strategy'
                })
    
    def display_twap_result(
        self,
        executed_orders: list,
        symbol: str,
        side: str,
        total_quantity: float
    ) -> None:
        """
        Display TWAP execution results in a formatted way.
        
        Args:
            executed_orders: List of executed order responses.
            symbol: Trading pair symbol.
            side: Order side (BUY/SELL).
            total_quantity: Total quantity requested.
        """
        print("\n" + "="*60)
        print(f"  ✓ TWAP STRATEGY COMPLETED")
        print("="*60)
        
        # Calculate summary statistics
        total_executed_qty = sum(
            float(order.get('executedQty', 0))
            for order in executed_orders
        )
        
        # Calculate average price
        total_value = 0
        for order in executed_orders:
            executed_qty = float(order.get('executedQty', 0))
            avg_price = float(order.get('avgPrice', 0))
            total_value += executed_qty * avg_price
        
        avg_execution_price = total_value / total_executed_qty if total_executed_qty > 0 else 0
        
        print(f"\n📊 Execution Summary:")
        print(f"   Symbol: {symbol}")
        print(f"   Side: {side}")
        print(f"   Total Quantity Requested: {total_quantity}")
        print(f"   Total Quantity Executed: {total_executed_qty}")
        print(f"   Average Execution Price: {avg_execution_price:.8f}")
        print(f"   Intervals Executed: {len(executed_orders)}")
        
        # Display individual orders
        if executed_orders:
            print(f"\n📋 Individual Orders:")
            for i, order in enumerate(executed_orders, 1):
                order_id = order.get('orderId', 'N/A')
                executed_qty = order.get('executedQty', 'N/A')
                avg_price = order.get('avgPrice', 'N/A')
                status = order.get('status', 'N/A')
                
                print(f"   {i}. Order ID: {order_id}")
                print(f"      Quantity: {executed_qty}")
                print(f"      Price: {avg_price}")
                print(f"      Status: {status}")
        
        print("\n" + "="*60 + "\n")
    
    def display_order_result(self, result: dict, order_type: str) -> None:
        """
        Display order execution result in a formatted way.
        
        Args:
            result: Order response dictionary from Binance API.
            order_type: Type of order (MARKET, LIMIT, STOP-LIMIT, OCO).
        """
        print("\n" + "="*60)
        print(f"  ✓ {order_type} ORDER EXECUTED SUCCESSFULLY")
        print("="*60)
        
        # Handle OCO orders differently
        if order_type == 'OCO':
            order_list_id = result.get('orderListId', 'N/A')
            symbol = result.get('symbol', 'N/A')
            list_order_status = result.get('listOrderStatus', 'N/A')
            orders = result.get('orders', [])
            
            print(f"\n📊 OCO Order Details:")
            print(f"   Order List ID: {order_list_id}")
            print(f"   Symbol: {symbol}")
            print(f"   Status: {list_order_status}")
            
            if orders:
                print(f"\n   Sub-Orders:")
                for i, order in enumerate(orders, 1):
                    print(f"   {i}. Order ID: {order.get('orderId', 'N/A')}")
                    print(f"      Type: {order.get('type', 'N/A')}")
                    print(f"      Side: {order.get('side', 'N/A')}")
            
            update_time = result.get('transactionTime')
            if update_time:
                from datetime import datetime
                dt = datetime.fromtimestamp(update_time / 1000)
                print(f"\n   Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        else:
            # Extract key information for regular orders
            order_id = result.get('orderId', 'N/A')
            symbol = result.get('symbol', 'N/A')
            side = result.get('side', 'N/A')
            status = result.get('status', 'N/A')
            orig_qty = result.get('origQty', 'N/A')
            executed_qty = result.get('executedQty', 'N/A')
            price = result.get('price', result.get('avgPrice', 'N/A'))
            
            print(f"\n📊 Order Details:")
            print(f"   Order ID: {order_id}")
            print(f"   Symbol: {symbol}")
            print(f"   Side: {side}")
            print(f"   Status: {status}")
            print(f"   Quantity: {orig_qty}")
            print(f"   Executed: {executed_qty}")
            
            if price and price != 'N/A' and price != '0':
                print(f"   Price: {price}")
            
            # Display additional info for limit orders
            if order_type == 'LIMIT':
                time_in_force = result.get('timeInForce', 'N/A')
                print(f"   Time in Force: {time_in_force}")
            
            # Display additional info for stop-limit orders
            if order_type == 'STOP-LIMIT':
                stop_price = result.get('stopPrice', 'N/A')
                time_in_force = result.get('timeInForce', 'N/A')
                print(f"   Stop Price: {stop_price}")
                print(f"   Time in Force: {time_in_force}")
            
            update_time = result.get('updateTime')
            if update_time:
                from datetime import datetime
                dt = datetime.fromtimestamp(update_time / 1000)
                print(f"   Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*60 + "\n")

    def prompt_grid_strategy(self) -> None:
        """
        Interactive prompt for Grid strategy input.
        Collects symbol, price range, grids, and investment from user and starts the strategy.
        """
        print("\n" + "-"*60)
        print("  GRID TRADING STRATEGY")
        print("-"*60)
        print("\nGrid trading places buy and sell orders at multiple price levels")
        print("within a range. When orders are filled, counter orders are placed")
        print("to profit from price oscillations.\n")
        
        try:
            # Get symbol
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            if not symbol:
                print("✗ Symbol cannot be empty")
                return
            
            # Get lower price
            lower_price_str = input("Lower Price (bottom of range): ").strip()
            if not lower_price_str:
                print("✗ Lower price cannot be empty")
                return
            
            try:
                lower_price = float(lower_price_str)
            except ValueError:
                print(f"✗ Invalid lower price: '{lower_price_str}' is not a valid number")
                return
            
            # Get upper price
            upper_price_str = input("Upper Price (top of range): ").strip()
            if not upper_price_str:
                print("✗ Upper price cannot be empty")
                return
            
            try:
                upper_price = float(upper_price_str)
            except ValueError:
                print(f"✗ Invalid upper price: '{upper_price_str}' is not a valid number")
                return
            
            # Get number of grids
            grids_str = input("Number of Grid Levels: ").strip()
            if not grids_str:
                print("✗ Number of grids cannot be empty")
                return
            
            try:
                grids = int(grids_str)
            except ValueError:
                print(f"✗ Invalid number of grids: '{grids_str}' is not a valid number")
                return
            
            # Get total investment
            investment_str = input("Total Investment (in quote currency): ").strip()
            if not investment_str:
                print("✗ Total investment cannot be empty")
                return
            
            try:
                total_investment = float(investment_str)
            except ValueError:
                print(f"✗ Invalid investment: '{investment_str}' is not a valid number")
                return
            
            # Calculate grid details
            price_range = upper_price - lower_price
            price_step = price_range / (grids - 1) if grids > 1 else 0
            avg_price = (lower_price + upper_price) / 2
            quantity_per_grid = (total_investment / grids) / avg_price
            
            # Confirm strategy
            print(f"\n📋 Grid Strategy Summary:")
            print(f"   Symbol: {symbol}")
            print(f"   Price Range: {lower_price} - {upper_price}")
            print(f"   Grid Levels: {grids}")
            print(f"   Price Step: {price_step:.8f}")
            print(f"   Total Investment: {total_investment}")
            print(f"   Quantity per Grid: {quantity_per_grid:.8f}")
            print(f"\n   Note: Grid will run continuously until you stop it.")
            print(f"   Use 'stop-grid' command to stop the strategy.")
            
            confirm = input("\nStart Grid strategy? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ Grid strategy cancelled")
                return
            
            # Check if grid is already running
            if self.grid_strategy.is_running:
                print("\n✗ Grid strategy is already running!")
                print("   Use 'stop-grid' to stop the current strategy first.")
                return
            
            # Start grid strategy
            print(f"\n⏳ Starting Grid strategy...")
            print("   Placing initial grid orders...\n")
            
            self.grid_strategy.start(
                symbol=symbol,
                lower_price=lower_price,
                upper_price=upper_price,
                grids=grids,
                total_investment=total_investment
            )
            
            # Display results
            print("\n" + "="*60)
            print(f"  ✓ GRID STRATEGY STARTED")
            print("="*60)
            print(f"\n📊 Grid Status:")
            print(f"   Symbol: {symbol}")
            print(f"   Active Orders: {len(self.grid_strategy.active_orders)}")
            print(f"   Grid Levels: {grids}")
            print(f"   Price Range: {lower_price} - {upper_price}")
            print(f"\n   The grid is now active and monitoring orders.")
            print(f"   Use 'stop-grid' command to stop the strategy.")
            print("\n" + "="*60 + "\n")
            
            # Note: In a production system, you would run monitor_and_rebalance
            # in a separate thread. For this implementation, we're keeping it simple.
            print("   Note: Automatic rebalancing requires running 'monitor-grid' command")
            print("   or implementing background monitoring in production.\n")
            
        except ValidationError as e:
            print(f"\n✗ Validation Error: {str(e)}")
        except ValueError as e:
            print(f"\n✗ Invalid Input: {str(e)}")
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'prompt_grid_strategy'
                })
    
    def stop_grid_strategy(self) -> None:
        """
        Stop the active Grid trading strategy.
        Cancels all open grid orders and stops monitoring.
        """
        print("\n" + "-"*60)
        print("  STOP GRID STRATEGY")
        print("-"*60)
        
        try:
            # Check if grid is running
            if not self.grid_strategy.is_running:
                print("\n✗ No active grid strategy to stop.")
                return
            
            # Confirm stop
            print(f"\n   Active Grid Orders: {len(self.grid_strategy.active_orders)}")
            print(f"   Symbol: {self.grid_strategy.symbol}")
            
            confirm = input("\nStop grid strategy and cancel all orders? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("✗ Operation cancelled")
                return
            
            # Stop grid strategy
            print("\n⏳ Stopping grid strategy...")
            print("   Cancelling all active orders...\n")
            
            self.grid_strategy.stop()
            
            print("\n" + "="*60)
            print(f"  ✓ GRID STRATEGY STOPPED")
            print("="*60 + "\n")
            
        except APIError as e:
            print(f"\n✗ API Error: {str(e)}")
        except ConnectionError as e:
            print(f"\n✗ Connection Error: {str(e)}")
        except Exception as e:
            print(f"\n✗ Unexpected Error: {str(e)}")
            if self.logger:
                self.logger.log_error(e, {
                    'component': 'TradingBotCLI',
                    'action': 'stop_grid_strategy'
                })
