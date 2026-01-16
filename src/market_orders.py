"""Market order execution manager."""

from typing import Dict, Any
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.validator import InputValidator, ValidationError
from src.logger import BotLogger


class MarketOrderManager:
    """
    Handles market order execution logic.
    Validates inputs, executes orders via Binance API, and logs all activities.
    """
    
    def __init__(self, client: BinanceClient, validator: InputValidator, logger: BotLogger):
        """
        Initialize market order manager.
        
        Args:
            client: BinanceClient instance for API interactions.
            validator: InputValidator instance for input validation.
            logger: BotLogger instance for logging.
        """
        self.client = client
        self.validator = validator
        self.logger = logger
    
    def execute(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Execute market order with validation and logging.
        
        This method:
        1. Validates all input parameters
        2. Executes the market order via Binance API
        3. Logs the execution details
        4. Returns the order result or raises an exception
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            
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
            'MarketOrderManager',
            f'Attempting to execute market order: {side} {quantity} {symbol}',
            {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'order_type': 'MARKET'
            }
        )
        
        # Validate inputs
        is_valid, error_msg = self.validator.validate_market_order(symbol, side, quantity)
        if not is_valid:
            self.logger.warning(
                'MarketOrderManager',
                f'Market order validation failed: {error_msg}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'error': error_msg
                }
            )
            raise ValidationError(error_msg)
        
        try:
            # Execute market order via API
            response = self.client.create_market_order(symbol, side, quantity)
            
            # Log successful execution
            self.logger.log_order_execution(
                'MARKET',
                {
                    'orderId': response.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'executedQty': response.get('executedQty'),
                    'status': response.get('status'),
                    'updateTime': response.get('updateTime')
                }
            )
            
            self.logger.info(
                'MarketOrderManager',
                f'Market order executed successfully: Order ID {response.get("orderId")}',
                {
                    'orderId': response.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'status': response.get('status')
                }
            )
            
            return response
            
        except APIError as e:
            # Log API error with details
            self.logger.error(
                'MarketOrderManager',
                f'API error during market order execution: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'error': str(e)
                }
            )
            # Re-raise with user-friendly message
            raise APIError(f"Failed to execute market order: {str(e)}")
            
        except ConnectionError as e:
            # Log connection error
            self.logger.error(
                'MarketOrderManager',
                f'Connection error during market order execution: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
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
                    'component': 'MarketOrderManager',
                    'action': 'execute',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity
                }
            )
            # Re-raise as APIError
            raise APIError(f"Unexpected error executing market order: {str(e)}")
