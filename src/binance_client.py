"""Binance API client wrapper for Futures trading."""

from typing import Dict, Any, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from src.config import Config
from src.logger import BotLogger


class APIError(Exception):
    """Raised when Binance API returns an error."""
    pass


class ConnectionError(Exception):
    """Raised when connection to Binance fails."""
    pass


class BinanceClient:
    """
    Wrapper for Binance Futures API interactions.
    Provides methods for order execution with error handling and logging.
    """
    
    def __init__(self, config: Config, logger: BotLogger):
        """
        Initialize Binance client with configuration and logger.
        
        Args:
            config: Configuration object with API credentials.
            logger: Logger instance for logging API interactions.
        """
        self.config = config
        self.logger = logger
        self.client: Optional[Client] = None
        
        try:
            # Initialize python-binance client
            self.client = Client(
                api_key=config.api_key,
                api_secret=config.api_secret,
                testnet=config.testnet
            )
            
            # Set base URL for testnet if needed
            if config.testnet:
                self.client.API_URL = 'https://testnet.binancefuture.com'
            
            self.logger.info(
                'BinanceClient',
                'Binance client initialized',
                {'testnet': config.testnet, 'base_url': config.base_url}
            )
        except Exception as e:
            self.logger.log_error(e, {'component': 'BinanceClient', 'action': 'initialization'})
            raise ConnectionError(f"Failed to initialize Binance client: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test API connectivity and credentials.
        
        Returns:
            bool: True if connection is successful.
            
        Raises:
            ConnectionError: If connection test fails.
            APIError: If API credentials are invalid.
        """
        try:
            self.logger.debug('BinanceClient', 'Testing API connection')
            
            # Test connection by getting server time
            response = self.client.futures_time()
            
            self.logger.log_api_response('futures_time', response)
            self.logger.info(
                'BinanceClient',
                'Connection test successful',
                {'server_time': response.get('serverTime')}
            )
            
            return True
            
        except BinanceAPIException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'test_connection',
                    'error_code': e.code,
                    'error_message': e.message
                }
            )
            raise APIError(f"API Error: {e.message} (Code: {e.code})")
            
        except BinanceRequestException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'test_connection',
                    'error_message': str(e)
                }
            )
            raise ConnectionError(f"Connection failed: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'test_connection'
                }
            )
            raise ConnectionError(f"Unexpected error during connection test: {str(e)}")

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Retrieve symbol information for validation.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            
        Returns:
            dict: Symbol information including filters, precision, etc.
            
        Raises:
            APIError: If symbol is not found or API error occurs.
            ConnectionError: If connection fails.
        """
        try:
            self.logger.log_api_request('futures_exchange_info', {'symbol': symbol})
            
            # Get exchange info for the symbol
            exchange_info = self.client.futures_exchange_info()
            
            # Find the specific symbol
            symbol_info = None
            for s in exchange_info.get('symbols', []):
                if s.get('symbol') == symbol:
                    symbol_info = s
                    break
            
            if not symbol_info:
                error_msg = f"Symbol {symbol} not found"
                self.logger.warning(
                    'BinanceClient',
                    error_msg,
                    {'symbol': symbol}
                )
                raise APIError(error_msg)
            
            # Check if symbol is tradeable
            if symbol_info.get('status') != 'TRADING':
                error_msg = f"Symbol {symbol} is not tradeable (status: {symbol_info.get('status')})"
                self.logger.warning(
                    'BinanceClient',
                    error_msg,
                    {'symbol': symbol, 'status': symbol_info.get('status')}
                )
                raise APIError(error_msg)
            
            self.logger.log_api_response('futures_exchange_info', {
                'symbol': symbol,
                'status': symbol_info.get('status'),
                'baseAsset': symbol_info.get('baseAsset'),
                'quoteAsset': symbol_info.get('quoteAsset')
            })
            
            self.logger.debug(
                'BinanceClient',
                f'Retrieved symbol info for {symbol}',
                {
                    'symbol': symbol,
                    'status': symbol_info.get('status'),
                    'pricePrecision': symbol_info.get('pricePrecision'),
                    'quantityPrecision': symbol_info.get('quantityPrecision')
                }
            )
            
            return symbol_info
            
        except APIError:
            # Re-raise APIError as-is
            raise
            
        except BinanceAPIException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'get_symbol_info',
                    'symbol': symbol,
                    'error_code': e.code,
                    'error_message': e.message
                }
            )
            raise APIError(f"API Error: {e.message} (Code: {e.code})")
            
        except BinanceRequestException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'get_symbol_info',
                    'symbol': symbol,
                    'error_message': str(e)
                }
            )
            raise ConnectionError(f"Connection failed: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'get_symbol_info',
                    'symbol': symbol
                }
            )
            raise APIError(f"Unexpected error retrieving symbol info: {str(e)}")
    
    def create_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Execute market order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            
        Returns:
            dict: Order response from Binance API.
            
        Raises:
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'type': 'MARKET'
            }
            
            self.logger.log_api_request('futures_create_order', params)
            
            # Execute market order
            response = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            self.logger.log_api_response('futures_create_order', response)
            
            self.logger.info(
                'BinanceClient',
                f'Market order executed: {side} {quantity} {symbol}',
                {
                    'orderId': response.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'status': response.get('status')
                }
            )
            
            return response
            
        except BinanceAPIException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_market_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'error_code': e.code,
                    'error_message': e.message
                }
            )
            raise APIError(f"API Error: {e.message} (Code: {e.code})")
            
        except BinanceRequestException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_market_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'error_message': str(e)
                }
            )
            raise ConnectionError(f"Connection failed: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_market_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity
                }
            )
            raise APIError(f"Unexpected error creating market order: {str(e)}")
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        Execute limit order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            price: Limit price.
            
        Returns:
            dict: Order response from Binance API.
            
        Raises:
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'type': 'LIMIT',
                'timeInForce': 'GTC'
            }
            
            self.logger.log_api_request('futures_create_order', params)
            
            # Execute limit order
            response = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=price
            )
            
            self.logger.log_api_response('futures_create_order', response)
            
            self.logger.info(
                'BinanceClient',
                f'Limit order placed: {side} {quantity} {symbol} @ {price}',
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
            
        except BinanceAPIException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_limit_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'error_code': e.code,
                    'error_message': e.message
                }
            )
            raise APIError(f"API Error: {e.message} (Code: {e.code})")
            
        except BinanceRequestException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_limit_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'error_message': str(e)
                }
            )
            raise ConnectionError(f"Connection failed: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_limit_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price
                }
            )
            raise APIError(f"Unexpected error creating limit order: {str(e)}")
    
    def create_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float
    ) -> Dict[str, Any]:
        """
        Execute stop-limit order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            stop_price: Stop price to trigger the order.
            limit_price: Limit price for the order.
            
        Returns:
            dict: Order response from Binance API.
            
        Raises:
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'stopPrice': stop_price,
                'price': limit_price,
                'type': 'STOP',
                'timeInForce': 'GTC'
            }
            
            self.logger.log_api_request('futures_create_order', params)
            
            # Execute stop-limit order
            response = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                timeInForce='GTC',
                quantity=quantity,
                price=limit_price,
                stopPrice=stop_price
            )
            
            self.logger.log_api_response('futures_create_order', response)
            
            self.logger.info(
                'BinanceClient',
                f'Stop-limit order placed: {side} {quantity} {symbol} @ stop={stop_price}, limit={limit_price}',
                {
                    'orderId': response.get('orderId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price,
                    'status': response.get('status')
                }
            )
            
            return response
            
        except BinanceAPIException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_stop_limit_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price,
                    'error_code': e.code,
                    'error_message': e.message
                }
            )
            raise APIError(f"API Error: {e.message} (Code: {e.code})")
            
        except BinanceRequestException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_stop_limit_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price,
                    'error_message': str(e)
                }
            )
            raise ConnectionError(f"Connection failed: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_stop_limit_order',
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price
                }
            )
            raise APIError(f"Unexpected error creating stop-limit order: {str(e)}")
    
    def create_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        stop_limit_price: float
    ) -> Dict[str, Any]:
        """
        Execute OCO (One-Cancels-Other) order.
        
        Note: OCO orders are primarily supported on Binance Spot markets.
        For Futures, this implementation uses the spot OCO endpoint.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            price: Limit order price.
            stop_price: Stop price to trigger stop-limit order.
            stop_limit_price: Limit price for stop-limit order.
            
        Returns:
            dict: Order response from Binance API.
            
        Raises:
            APIError: If API returns an error.
            ConnectionError: If connection fails.
        """
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'stopPrice': stop_price,
                'stopLimitPrice': stop_limit_price,
                'stopLimitTimeInForce': 'GTC'
            }
            
            self.logger.log_api_request('create_oco_order', params)
            
            # Execute OCO order using spot API (OCO not available on Futures)
            # For testnet, we'll use the spot OCO endpoint
            response = self.client.create_oco_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                stopLimitPrice=stop_limit_price,
                stopLimitTimeInForce='GTC'
            )
            
            self.logger.log_api_response('create_oco_order', response)
            
            self.logger.info(
                'BinanceClient',
                f'OCO order placed: {side} {quantity} {symbol}',
                {
                    'orderListId': response.get('orderListId'),
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'stopPrice': stop_price,
                    'stopLimitPrice': stop_limit_price,
                    'listOrderStatus': response.get('listOrderStatus')
                }
            )
            
            return response
            
        except BinanceAPIException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_oco_order',
                    'symbol': symbol,
                    'error_code': e.code,
                    'error_message': e.message
                }
            )
            raise APIError(f"API Error: {e.message} (Code: {e.code})")
            
        except BinanceRequestException as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_oco_order',
                    'symbol': symbol,
                    'error_message': str(e)
                }
            )
            raise ConnectionError(f"Connection failed: {str(e)}")
            
        except Exception as e:
            self.logger.log_error(
                e,
                {
                    'component': 'BinanceClient',
                    'action': 'create_oco_order',
                    'symbol': symbol
                }
            )
            raise APIError(f"Unexpected error creating OCO order: {str(e)}")
