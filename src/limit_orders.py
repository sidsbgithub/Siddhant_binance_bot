"""Limit order execution manager."""

from typing import Dict, Any
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.validator import InputValidator, ValidationError
from src.logger import BotLogger


class LimitOrderManager:
    """
    Handles limit order execution logic.
    Validates inputs, executes orders via Binance API, and logs all activities.
    """
    
    def __init__(self, client: BinanceClient, validator: InputValidator, logger: BotLogger):
        """
        Initialize limit order manager.
        
        Args:
            client: BinanceClient instance for API interactions.
            validator: InputValidator instance for input validation.
            logger: BotLogger instance for logging.
        """
        self.client = client
        self.validator = validator
        self.logger = logger
    
    def execute(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        Execute limit order with validation and logging.
        
        This method:
        1. Validates all input parameters
        2. Executes the limit order via Binance API
        3. Logs the execution details
        4. Returns the order result or raises an exception
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            price: Limit price.
            
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
            'LimitOrderManager',
            f'Attempting to execute limit order: {side} {quantity} {symbol} @ {price}',
            {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'order_type': 'LIMIT'
            }
        )
        
        # Validate inputs
        is_valid, error_msg = self.validator.validate_limit_order(symbol, side, quantity, price)
        if not is_valid:
            self.logger.warning(
                'LimitOrderManager',
                f'Limit order validation failed: {error_msg}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'error': error_msg
                }
            )
            raise ValidationError(error_msg)
        
        try:
            # Execute limit order via API
            response = self.client.create_limit_order(symbol, side, quantity, price)
            
            # Log successful execution
            self.logger.log_order_execution(
                'LIMIT',
                {
                    'orderId': response.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'executedQty': response.get('executedQty'),
                    'status': response.get('status'),
                    'updateTime': response.get('updateTime')
                }
            )
            
            self.logger.info(
                'LimitOrderManager',
                f'Limit order placed successfully: Order ID {response.get("orderId")}',
                {
                    'orderId': response.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'status': response.get('status')
                }
            )
            
            return response
            
        except APIError as e:
            # Log API error with details
            self.logger.error(
                'LimitOrderManager',
                f'API error during limit order execution: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'error': str(e)
                }
            )
            # Re-raise with user-friendly message
            raise APIError(f"Failed to execute limit order: {str(e)}")
            
        except ConnectionError as e:
            # Log connection error
            self.logger.error(
                'LimitOrderManager',
                f'Connection error during limit order execution: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
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
                    'component': 'LimitOrderManager',
                    'action': 'execute',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price
                }
            )
            # Re-raise as APIError
            raise APIError(f"Unexpected error executing limit order: {str(e)}")
