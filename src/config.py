"""Configuration management for the trading bot."""

import os
from typing import Optional
from dotenv import load_dotenv


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """
    Handles configuration loading from environment variables.
    Manages API credentials and bot settings.
    """
    
    def __init__(self):
        """Initialize configuration with default values."""
        self.api_key: Optional[str] = None
        self.api_secret: Optional[str] = None
        self.base_url: str = "https://testnet.binancefuture.com"
        self.testnet: bool = True
        self.log_level: str = "INFO"
        self.log_file: str = "bot.log"
    
    def load_from_env(self) -> None:
        """
        Load configuration from environment variables.
        Attempts to load from .env file first if present.
        
        Raises:
            ConfigurationError: If required configuration is missing.
        """
        # Load from .env file if it exists
        load_dotenv()
        
        # Load API credentials
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        
        # Load optional configuration
        testnet_env = os.getenv("BINANCE_TESTNET", "true")
        self.testnet = testnet_env.lower() in ("true", "1", "yes")
        
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "bot.log")
        
        # Set base URL based on testnet setting
        if self.testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
    
    def validate(self) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid.
            
        Raises:
            ConfigurationError: If required configuration is missing or invalid.
        """
        if not self.api_key:
            raise ConfigurationError(
                "BINANCE_API_KEY is required. Please set it in your environment or .env file."
            )
        
        if not self.api_secret:
            raise ConfigurationError(
                "BINANCE_API_SECRET is required. Please set it in your environment or .env file."
            )
        
        if not self.api_key.strip():
            raise ConfigurationError("BINANCE_API_KEY cannot be empty.")
        
        if not self.api_secret.strip():
            raise ConfigurationError("BINANCE_API_SECRET cannot be empty.")
        
        return True
    
    def __repr__(self) -> str:
        """String representation of config (without exposing secrets)."""
        return (
            f"Config(testnet={self.testnet}, "
            f"base_url={self.base_url}, "
            f"log_level={self.log_level}, "
            f"api_key={'***' if self.api_key else 'None'})"
        )
