"""Main entry point for the Binance Futures Trading Bot."""

import sys
from src.config import Config, ConfigurationError
from src.cli import TradingBotCLI
from src.binance_client import ConnectionError as BinanceConnectionError


def main():
    """
    Main entry point for the trading bot.
    
    This function:
    1. Loads and validates configuration from environment variables
    2. Initializes all bot components (logger, client, validator, managers)
    3. Tests API connection to ensure credentials are valid
    4. Starts the CLI interface for user interaction
    5. Handles graceful error handling for startup failures
    """
    print("=" * 60)
    print("  Binance Futures Trading Bot - Testnet")
    print("=" * 60)
    
    try:
        # Load and validate configuration
        print("\n[Configuration]")
        config = Config()
        config.load_from_env()
        config.validate()
        
        print(f"✓ Configuration loaded successfully")
        print(f"  - Mode: {'TESTNET' if config.testnet else 'PRODUCTION'}")
        print(f"  - Base URL: {config.base_url}")
        print(f"  - Log Level: {config.log_level}")
        print(f"  - Log File: {config.log_file}")
        
        # Initialize CLI and all components
        cli = TradingBotCLI(config)
        cli.initialize()
        
        # Start CLI interface
        cli.start()
        
    except ConfigurationError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease ensure you have:")
        print("  1. Created a .env file (copy from .env.example)")
        print("  2. Added your Binance Testnet API credentials")
        print("  3. Get testnet keys from: https://testnet.binancefuture.com")
        print("\nExample .env file:")
        print("  BINANCE_API_KEY=your_api_key_here")
        print("  BINANCE_API_SECRET=your_api_secret_here")
        print("  BINANCE_TESTNET=true")
        sys.exit(1)
        
    except BinanceConnectionError as e:
        print(f"\n✗ Connection Error: {e}")
        print("\nPossible causes:")
        print("  1. Invalid API credentials")
        print("  2. Network connectivity issues")
        print("  3. Binance API is down or unreachable")
        print("\nPlease verify your credentials and network connection.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n✓ Bot stopped by user (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        print("\nAn unexpected error occurred during startup.")
        print("Please check the log file for more details.")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
