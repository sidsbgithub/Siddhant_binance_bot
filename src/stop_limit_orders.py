"""Stop-limit order execution manager."""

from typing import Dict, Any
from src.binance_client import BinanceClient, APIError, ConnectionError
from src.validator import InputValidator, ValidationError
from src.logger import BotLogger


class StopLimitOrderManager:
    """
    Handles stop-limit order execution logic.
    Validates inputs, executes orders via Binance API, and logs all activities.
    """
    
    def __init__(
        self,
        client: BinanceClient,
        validator: InputValidator,
        logger: BotLogger
    ):
        """
        Initialize stop-limit order manager.
        
        Args:
            client: BinanceClient instance for API calls.
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
        stop_price: float,
        limit_price: float
    ) -> Dict[str, Any]:
        """
        Execute stop-limit order with validation and logging.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            stop_price: Stop price to trigger the order.
            limit_price: Limit price for the order.
            
        Returns:
            dict: Order response from Binance API.
            
        Raises:
            ValidationError: If input validation fails.
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        # Convert to uppercase for consistency
        symbol = symbol.upper()
        side = side.upper()
        
        # Log order attempt
        self.logger.info(
            'StopLimitOrderManager',
            f'Attempting stop-limit order: {side} {quantity} {symbol} @ stop={stop_price}, limit={limit_price}'
        )
        
        # Validate inputs
        is_valid, error_msg = self.validator.validate_stop_limit_order(
            symbol, side, quantity, stop_price, limit_price
        )
        
        if not is_valid:
            self.logger.warning(
                'StopLimitOrderManager',
                f'Validation failed: {error_msg}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price
                }
            )
            raise ValidationError(error_msg)
        
        # Execute order via API
        try:
            result = self.client.create_stop_limit_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                stop_price=stop_price,
                limit_price=limit_price
            )
            
            # Log successful execution
            self.logger.log_order_execution('STOP_LIMIT', {
                'orderId': result.get('orderId'),
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'stopPrice': stop_price,
                'limitPrice': limit_price,
                'status': result.get('status'),
                'type': result.get('type')
            })
            
            return result
            
        except (APIError, ConnectionError) as e:
            # Log error and re-raise
            self.logger.error(
                'StopLimitOrderManager',
                f'Failed to execute stop-limit order: {str(e)}',
                {
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price,
                    'error': str(e)
                }
            )
            raise
