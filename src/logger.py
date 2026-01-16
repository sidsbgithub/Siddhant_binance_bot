"""Logging infrastructure for the trading bot."""

import logging
import json
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler
from datetime import datetime


class BotLogger:
    """
    Handles structured logging to file and console.
    Provides methods for logging API requests, responses, errors, and order executions.
    """
    
    def __init__(self, log_file: str = "bot.log", log_level: str = "INFO"):
        """
        Initialize the logger with file and console handlers.
        
        Args:
            log_file: Path to the log file.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR).
        """
        self.log_file = log_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger("TradingBot")
        self.setup_logger()
    
    def setup_logger(self) -> None:
        """
        Configure logger with file and console handlers.
        Sets up structured logging format and log rotation.
        """
        # Clear any existing handlers
        self.logger.handlers.clear()
        self.logger.setLevel(self.log_level)
        
        # Create formatter with structured format
        formatter = logging.Formatter(
            fmt='[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(component)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation (max 10MB, keep 5 backup files)
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _log(self, level: int, component: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Internal method to log with component and optional JSON data.
        
        Args:
            level: Logging level (logging.DEBUG, logging.INFO, etc.).
            component: Component name (e.g., 'BinanceClient', 'MarketOrderManager').
            message: Log message.
            data: Optional dictionary to be logged as JSON.
        """
        # Add component to extra dict for formatter
        extra = {'component': component}
        
        # Append JSON data to message if provided
        if data:
            # Sanitize sensitive data
            sanitized_data = self._sanitize_data(data)
            message = f"{message} {json.dumps(sanitized_data, default=str)}"
        
        self.logger.log(level, message, extra=extra)
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize sensitive information from log data.
        
        Args:
            data: Dictionary that may contain sensitive information.
            
        Returns:
            Sanitized dictionary with sensitive fields masked.
        """
        sanitized = data.copy()
        sensitive_keys = ['api_key', 'api_secret', 'apiKey', 'apiSecret', 'secret', 'password']
        
        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = '***'
        
        return sanitized
    
    def log_api_request(self, endpoint: str, params: Dict[str, Any]) -> None:
        """
        Log API request details.
        
        Args:
            endpoint: API endpoint being called.
            params: Request parameters.
        """
        self._log(
            logging.DEBUG,
            'BinanceClient',
            f'API Request to {endpoint}',
            {'endpoint': endpoint, 'params': params}
        )
    
    def log_api_response(self, endpoint: str, response: Dict[str, Any]) -> None:
        """
        Log API response details.
        
        Args:
            endpoint: API endpoint that was called.
            response: Response data from API.
        """
        self._log(
            logging.DEBUG,
            'BinanceClient',
            f'API Response from {endpoint}',
            {'endpoint': endpoint, 'response': response}
        )
    
    def log_order_execution(self, order_type: str, order_details: Dict[str, Any]) -> None:
        """
        Log order execution with all details.
        
        Args:
            order_type: Type of order (MARKET, LIMIT, STOP_LIMIT, OCO).
            order_details: Order details including symbol, side, quantity, etc.
        """
        self._log(
            logging.INFO,
            f'{order_type}OrderManager',
            f'{order_type} order executed successfully',
            order_details
        )
    
    def log_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Log error with context and stack trace.
        
        Args:
            error: Exception that occurred.
            context: Additional context about where/why the error occurred.
        """
        self._log(
            logging.ERROR,
            context.get('component', 'Unknown'),
            f'Error occurred: {str(error)}',
            {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context
            }
        )
    
    def info(self, component: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log info level message.
        
        Args:
            component: Component name.
            message: Log message.
            data: Optional data dictionary.
        """
        self._log(logging.INFO, component, message, data)
    
    def debug(self, component: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log debug level message.
        
        Args:
            component: Component name.
            message: Log message.
            data: Optional data dictionary.
        """
        self._log(logging.DEBUG, component, message, data)
    
    def warning(self, component: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log warning level message.
        
        Args:
            component: Component name.
            message: Log message.
            data: Optional data dictionary.
        """
        self._log(logging.WARNING, component, message, data)
    
    def error(self, component: str, message: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Log error level message.
        
        Args:
            component: Component name.
            message: Log message.
            data: Optional data dictionary.
        """
        self._log(logging.ERROR, component, message, data)
