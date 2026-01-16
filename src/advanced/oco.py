"""OCO (One-Cancels-Other) order execution manager."""

from typing import Dict, Any
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.validator import InputValidator, ValidationError
from src.logger import BotLogger


class OCOOrderManager:
    """
    Handles OCO (One-Cancels-Other) order execution logic.
    Validates inputs, executes orders via Binance API, and logs all activities.
    
    OCO orders consist of two orders:
    1. A limit order at the specified price
    2. A stop-limit order at the stop price with stop limit price
    
    When one order is filled, the other is automatically cancelled.
    """
    
    def __init__(self, client: BinanceClient, validator: InputValidator, logger: BotLogger):
        """
        Initialize OCO order manager.
        
        Args:
            client: BinanceClient instance for API interactions.
            validator: InputValidator instance for input validation.
            logger: BotLogger instance for logging.
        """
        self.client = client
        self.validator = validator
        self.logger = logger
    
    def execute(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        stop_limit_price: float
    ) -> Dict[str, Any]:
        """
        Execute OCO order with validation and logging.
        
        This method:
        1. Validates all input parameters
        2. Executes the OCO order via Binance API
        3. Logs the execution details
        4. Returns the order result or raises an exception
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            price: Limit order price.
            stop_price: Stop price to trigger stop-limit order.
            stop_limit_price: Limit price for stop-limit order.
            
        Returns:
            dict: Order response from Binance API containing order details.
            
        Raises:
            ValidationError: If input validation fails.
            APIError: If Binance API returns an error.
            ConnectionError: If connection to Binance fails.
        """
        # Normalize inputs
        symbol = symbol.upper() if symbol else ""
        side = side.upper() if side else ""
        
        self.logger.info(
            'OCOOrderManager',
            f'Attempting to execute OCO order: {side} {quantity} {symbol}',
            {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'stop_price': stop_price,
                'stop_limit_price': stop_limit_price,
                'order_type': 'OCO'
            }
        )
        
        # Validate inputs
        is_valid, error_msg = self.validator.validate_oco_order(
            symbol, side, quantity, price, stop_price, stop_limit_price
        )
        if not is_valid:
            self.logger.warning(
                'OCOOrderManager',
                f'OCO order validation failed: {error_msg}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'stop_limit_price': stop_limit_price,
                    'error': error_msg
                }
            )
            raise ValidationError(error_msg)
        
        try:
            # Execute OCO order via API
            response = self.client.create_oco_order(
                symbol, side, quantity, price, stop_price, stop_limit_price
            )
            
            # Log successful execution
            self.logger.log_order_execution(
                'OCO',
                {
                    'orderListId': response.get('orderListId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'stop_limit_price': stop_limit_price,
                    'listOrderStatus': response.get('listOrderStatus'),
                    'orders': response.get('orders', [])
                }
            )
            
            self.logger.info(
                'OCOOrderManager',
                f'OCO order placed successfully: Order List ID {response.get("orderListId")}',
                {
                    'orderListId': response.get('orderListId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'stop_limit_price': stop_limit_price,
                    'listOrderStatus': response.get('listOrderStatus')
                }
            )
            
            return response
            
        except APIError as e:
            # Log API error with details
            self.logger.error(
                'OCOOrderManager',
                f'API error during OCO order execution: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'stop_limit_price': stop_limit_price,
                    'error': str(e)
                }
            )
            # Re-raise with user-friendly message
            raise APIError(f"Failed to execute OCO order: {str(e)}")
            
        except ConnectionError as e:
            # Log connection error
            self.logger.error(
                'OCOOrderManager',
                f'Connection error during OCO order execution: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'stop_limit_price': stop_limit_price,
                    'error': str(e)
                }
            )
            # Re-raise with user-friendly message
            raise ConnectionError(f"Failed to connect to Binance: {str(e)}")
            
        except Exception as e:
            # Log unexpected error
            self.logger.log_error(
                e,
                {
                    'component': 'OCOOrderManager',
                    'action': 'execute',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stop_price': stop_price,
                    'stop_limit_price': stop_limit_price
                }
            )
            # Re-raise as APIError
            raise APIError(f"Unexpected error executing OCO order: {str(e)}")
