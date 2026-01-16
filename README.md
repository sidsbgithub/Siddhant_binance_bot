# Binance Futures Trading Bot

A professional-grade Python CLI trading bot for Binance USDT-M Futures. Execute various order types with comprehensive validation, logging, and advanced trading strategies.

## Overview

This project provides a complete trading bot solution for Binance Futures with support for:
- **Market Orders** - Execute at current market price
- **Limit Orders** - Place orders at specified prices
- **Stop-Limit Orders** - Automated stop-loss and take-profit management
- **OCO Orders** - One-Cancels-Other for simultaneous profit/loss management
- **Advanced Strategies** - TWAP, Grid Trading, and more

## Features

✅ **Order Management**
- Market order execution
- Limit order placement
- Stop-limit orders with price validation
- OCO (One-Cancels-Other) orders
- Real-time order confirmation

✅ **Risk Management**
- Comprehensive input validation
- Symbol availability checking
- Quantity and price precision validation
- Stop-loss and take-profit automation

✅ **Advanced Strategies**
- TWAP (Time-Weighted Average Price) for large orders
- Grid Trading for volatility exploitation
- OCO strategy for automated profit/loss management

✅ **Reliability & Monitoring**
- Structured logging system
- API response tracking
- Connection error handling
- Detailed execution reports

✅ **User Interface**
- Interactive CLI with command menu
- Real-time order confirmation
- Clear error messaging
- Order history and status tracking

## Project Structure

```
Siddhant_binance_bot/
├── src/                           # Core application
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── binance_client.py         # Binance API wrapper with error handling
│   ├── validator.py              # Input validation logic
│   ├── logger.py                 # Structured logging system
│   ├── cli.py                    # CLI interface and commands
│   ├── market_orders.py          # Market order execution
│   ├── limit_orders.py           # Limit order execution
│   ├── stop_limit_orders.py      # Stop-limit order execution
│   └── advanced/                 # Advanced trading strategies
│       ├── oco.py                # OCO order implementation
│       ├── twap.py               # TWAP strategy
│       └── grid.py               # Grid trading strategy
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment configuration
├── .env                          # Environment variables (create from example)
├── README.md                      # This file
└── PROJECT_REPORT.md             # Detailed technical report
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Binance Futures Testnet account

### Step 1: Get Testnet Credentials

1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Sign up or log in with your credentials
3. Navigate to API Management
4. Create a new API key with the following permissions:
   - Trading enabled
   - Futures API enabled
5. Copy your API Key and Secret

### Step 2: Clone/Download Project

```bash
# Navigate to project directory
cd Siddhant_binance_bot
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env and add your Binance credentials:
# BINANCE_API_KEY=your_api_key_here
# BINANCE_API_SECRET=your_api_secret_here
# BINANCE_TESTNET=true
```

### Step 5: Run the Bot

```bash
python main.py
```

You should see:
```
============================================================
  Binance Futures Trading Bot - Testnet
============================================================

[Configuration]
✓ Configuration loaded successfully
  - Mode: TESTNET
  - Base URL: https://testnet.binancefuture.com
  - Log Level: INFO
  - Log File: bot.log

[1/5] Setting up logger...
✓ Logger initialized
[2/5] Connecting to Binance...
✓ Connected to Testnet
[3/5] Testing API connection...
✓ API connection successful
[4/5] Initializing input validator...
✓ Validator ready
[5/5] Setting up order managers...
✓ Order managers ready

Welcome to Binance Futures Trading Bot!
Type 'help' for available commands or 'quit' to exit.

bot>
```

## Usage Guide

### CLI Commands

Once the bot starts, use these commands:

#### Help
```
bot> help
```
Shows all available commands.

#### Market Order
```
bot> market
```
Execute a market order at current price.

**Interactive prompts:**
- Symbol: `BTCUSDT`
- Side: `BUY` or `SELL`
- Quantity: `0.01`

#### Limit Order
```
bot> limit
```
Place a limit order at a specific price.

**Interactive prompts:**
- Symbol: `BTCUSDT`
- Side: `BUY` or `SELL`
- Quantity: `0.01`
- Price: `50000.00`

#### Stop-Limit Order
```
bot> stop-limit
```
Place a stop-limit order with automatic triggering.

**Interactive prompts:**
- Symbol: `BTCUSDT`
- Side: `BUY` or `SELL`
- Quantity: `0.01`
- Stop Price: `49500.00`
- Limit Price: `49400.00`

#### OCO Order
```
bot> oco
```
Execute One-Cancels-Other order (take-profit + stop-loss).

**Interactive prompts:**
- Symbol: `BTCUSDT`
- Side: `BUY` or `SELL`
- Quantity: `0.01`
- Limit Price: `52000.00`
- Stop Price: `48000.00`
- Stop Limit Price: `47900.00`

#### TWAP Strategy
```
bot> twap
```
Execute Time-Weighted Average Price strategy for large orders.

#### Grid Trading
```
bot> grid
```
Execute grid trading strategy for volatile markets.

#### Exit
```
bot> quit
```
Exit the bot gracefully.

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Required
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Optional (defaults shown)
BINANCE_TESTNET=true                    # Use testnet
LOG_LEVEL=INFO                          # DEBUG, INFO, WARNING, ERROR
LOG_FILE=bot.log                        # Log file location
```

### Environment Variable Details

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `BINANCE_API_KEY` | string | Required | Your Binance API key |
| `BINANCE_API_SECRET` | string | Required | Your Binance API secret |
| `BINANCE_TESTNET` | boolean | true | Use testnet (true) or production (false) |
| `LOG_LEVEL` | string | INFO | Logging verbosity level |
| `LOG_FILE` | string | bot.log | Log file output path |

## Order Types Explained

### Market Order
Executes immediately at the best available market price.
- **Use case:** Quick entry/exit regardless of exact price
- **Advantage:** Guaranteed execution
- **Disadvantage:** Price may slip during volatile markets

### Limit Order
Executes only at your specified price or better.
- **Use case:** Precise price targets
- **Advantage:** Full control over execution price
- **Disadvantage:** May not fill if market doesn't reach your price

### Stop-Limit Order
Triggers a limit order when price reaches a stop level.
- **Use case:** Automated stop-loss and take-profit
- **Advantage:** Combines speed with price control
- **Disadvantage:** Complex to set correctly

### OCO Order
Two linked orders: when one executes, the other cancels.
- **Use case:** Simultaneous profit target and stop-loss
- **Advantage:** Comprehensive risk management
- **Disadvantage:** Requires careful price setup

## Validation Rules

The bot validates all inputs before execution:

### Symbol Validation
- Symbol must exist on Binance Futures
- Symbol must be in TRADING status
- Case-insensitive (BTCUSDT = btcusdt)

### Quantity Validation
- Must be positive number
- Must meet minimum quantity (minQty)
- Must not exceed maximum quantity (maxQty)
- Must comply with step size (quantity precision)

### Price Validation
- Must be positive number
- Must meet minimum price (minPrice)
- Must not exceed maximum price (maxPrice)
- Must comply with tick size (price precision)

### Side Validation
- Must be 'BUY' or 'SELL'
- Case-insensitive

## Logging

All bot activities are logged to `bot.log`:

```
[2026-01-16 10:30:45.123] [INFO] [BinanceClient] Binance client initialized {"testnet": true}
[2026-01-16 10:30:45.456] [INFO] [BinanceClient] Connection test successful {"server_time": 1768496867919}
[2026-01-16 10:30:50.789] [INFO] [MarketOrderManager] Market order executed successfully {"orderId": 11711383307}
```

**Log Levels:**
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for suspicious activity
- `ERROR` - Error messages for failures

## Error Handling

The bot provides clear error messages for common issues:

### APIError
- Invalid API credentials
- Symbol not found
- Invalid order parameters
- Insufficient balance

### ConnectionError
- Network connectivity issues
- Binance API unreachable
- Connection timeout

### ValidationError
- Invalid symbol format
- Quantity out of range
- Price precision mismatch

## Testing

Run the included test suite:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Run specific test file
pytest tests/test_market_orders.py
```

## Technical Architecture

### Component Architecture

The bot uses a modular, layered architecture:

1. **Configuration Layer** (`config.py`) - Load and validate environment settings
2. **Client Layer** (`binance_client.py`) - Wrapper for Binance API with error handling
3. **Validation Layer** (`validator.py`) - Multi-layer input validation
4. **Manager Layer** - Order execution managers for each order type
5. **Strategy Layer** (`advanced/`) - Advanced trading strategy implementations
6. **Logger Layer** (`logger.py`) - Structured logging system
7. **CLI Layer** (`cli.py`) - User interface and interaction

### API Integration

Uses the official [python-binance](https://github.com/sammchardy/python-binance) library:
- Futures API endpoints
- Testnet support
- Automatic request signing
- Rate limiting handling

### Data Validation

Multi-layer validation:
1. Type checking (string, float, etc.)
2. Range validation (min/max values)
3. Symbol validation (API lookup)
4. Precision validation (step sizes, tick sizes)
5. Relationship validation (e.g., stop > limit for SELL)

## Troubleshooting

### "Failed to initialize Binance client"
- Verify API credentials in `.env`
- Check internet connection
- Verify testnet status at https://testnet.binancefuture.com

### "Symbol not found"
- Verify symbol spelling (e.g., BTCUSDT not BTC/USDT)
- Check symbol is available on Futures
- Use uppercase format

### "Quantity does not match step size"
- Adjust quantity to match precision requirements
- For example: BTCUSDT may require 0.001 BTC increments
- Check symbol info for exact step size

### "Order not executing"
- Verify sufficient balance
- Check price is within valid range
- Verify limit price vs stop price relationship

### "Connection timeout"
- Check internet connection
- Verify Binance API is accessible
- Retry the operation

## Security Best Practices

⚠️ **Important Security Considerations**

1. **Never commit .env file** to version control
2. **Use Testnet API keys first** before production
3. **Limit API key permissions** - only enable needed features
4. **Rotate API keys** periodically
5. **Never share your API credentials**
6. **Use IP whitelist** in API settings for extra security
7. **Start with small amounts** to test thoroughly

## Production Considerations

Before deploying to production:

1. ✅ Thoroughly test with testnet
2. ✅ Review all order parameters
3. ✅ Implement additional safety checks
4. ✅ Monitor initial trades carefully
5. ✅ Set strict stop-loss limits
6. ✅ Start with small position sizes
7. ✅ Have an emergency exit plan

## Dependencies

```
python-binance>=1.0.17       # Binance API client
python-dotenv>=1.0.0         # Environment variable management
requests>=2.31.0             # HTTP client
pytest>=7.4.0                # Testing framework
pytest-mock>=3.12.0          # Mocking for tests
pytest-cov>=4.1.0            # Code coverage
```

## Additional Documentation

- [PROJECT_REPORT.md](PROJECT_REPORT.md) - Detailed technical report with architecture, testing, and implementation details

## License

This project is provided as-is for educational and trading purposes.

## Support & Contributions

For issues, questions, or contributions:
1. Check existing documentation
2. Review error logs in `bot.log`
3. Test with testnet first
4. Verify all inputs are correct

## Disclaimer

⚠️ **Risk Disclaimer**

This bot is provided for educational purposes. Trading cryptocurrencies carries substantial risk of loss. Past performance is not indicative of future results. Always:
- Use testnet before production
- Start with minimal amounts
- Test thoroughly
- Never risk more than you can afford to lose
- Have a comprehensive risk management strategy

The developers are not responsible for any losses incurred through use of this bot.

---

**Last Updated:** January 16, 2026
**Version:** 1.0.0
**Status:** Production Ready
python main.py
```

The bot will:
1. Load configuration from `.env` file
2. Initialize logging system
3. Connect to Binance Futures Testnet
4. Test API connection
5. Display an interactive command prompt

### Interactive CLI

The bot provides an interactive command-line interface. Type commands at the `bot>` prompt:

```
bot> help
```

### Available Commands

#### Order Commands

##### 1. Market Order
Execute an order at the current market price.

```
bot> market
```

**Prompts:**
- Symbol (e.g., BTCUSDT)
- Side (BUY/SELL)
- Quantity

**Example:**
```
bot> market
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): BUY
Quantity: 0.001
```

##### 2. Limit Order
Place an order at a specific price.

```
bot> limit
```

**Prompts:**
- Symbol (e.g., BTCUSDT)
- Side (BUY/SELL)
- Quantity
- Price

**Example:**
```
bot> limit
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): SELL
Quantity: 0.001
Price: 45000
```

##### 3. Stop-Limit Order
Place a stop-limit order for automated risk management.

```
bot> stop-limit
```

**Prompts:**
- Symbol (e.g., BTCUSDT)
- Side (BUY/SELL)
- Quantity
- Stop Price (trigger price)
- Limit Price (execution price)

**Example:**
```
bot> stop-limit
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): SELL
Quantity: 0.001
Stop Price: 43000
Limit Price: 42900
```

**How it works:** When the market price reaches the stop price (43000), a limit order is placed at the limit price (42900).

##### 4. OCO Order (One-Cancels-Other)
Place two orders simultaneously - when one fills, the other is cancelled.

```
bot> oco
```

**Prompts:**
- Symbol (e.g., BTCUSDT)
- Side (BUY/SELL)
- Quantity
- Limit Price (take profit)
- Stop Price (trigger price)
- Stop Limit Price (execution price)

**Example:**
```
bot> oco
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): SELL
Quantity: 0.001
Limit Price (take profit): 46000
Stop Price (trigger price): 43000
Stop Limit Price (execution price): 42900
```

**How it works:** Places a limit order at 46000 (profit target) and a stop-limit at 43000/42900 (stop loss). When one order fills, the other is automatically cancelled.

##### 5. TWAP Strategy (Time-Weighted Average Price)
Execute a large order by splitting it into smaller chunks over time.

```
bot> twap
```

**Prompts:**
- Symbol (e.g., BTCUSDT)
- Side (BUY/SELL)
- Total Quantity
- Duration (minutes)
- Number of intervals (optional)

**Example:**
```
bot> twap
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): BUY
Total Quantity: 0.01
Duration (minutes): 10
Number of intervals (default: 10): 5
```

**How it works:** Splits the total quantity (0.01) into 5 equal parts and executes them at regular intervals over 10 minutes (one order every 2 minutes).

##### 6. Grid Trading Strategy
Profit from price oscillations by placing buy and sell orders at multiple price levels.

```
bot> grid
```

**Prompts:**
- Symbol (e.g., BTCUSDT)
- Lower Price (bottom of range)
- Upper Price (top of range)
- Number of Grid Levels
- Total Investment (in quote currency)

**Example:**
```
bot> grid
Symbol (e.g., BTCUSDT): BTCUSDT
Lower Price (bottom of range): 42000
Upper Price (top of range): 46000
Number of Grid Levels: 10
Total Investment (in quote currency): 100
```

**How it works:** Places buy and sell limit orders at 10 price levels between 42000 and 46000. When an order fills, a counter order is placed to capture profit from price movements.

**Stop Grid Strategy:**
```
bot> stop-grid
```

Cancels all active grid orders and stops the strategy.

#### Utility Commands

- `help` or `menu` - Display available commands
- `quit` or `exit` - Exit the bot

### Order Confirmation

All orders require confirmation before execution. Review the order summary and type `yes` to confirm or `no` to cancel.

### Logging

All bot activities are logged to `bot.log` with the following information:
- Timestamp
- Log level (INFO, WARNING, ERROR, DEBUG)
- Component name
- Action details
- API requests and responses
- Order execution details
- Errors and exceptions

**Log Format:**
```
[2026-01-15 10:30:45.123] [INFO] [MarketOrderManager] Order executed successfully {"order_id": 12345, "symbol": "BTCUSDT", "side": "BUY", "quantity": 0.001}
```

## Usage Examples

### Example 1: Simple Market Order

```
bot> market
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): BUY
Quantity: 0.001

📋 Order Summary:
   Type: MARKET
   Symbol: BTCUSDT
   Side: BUY
   Quantity: 0.001

Confirm order? (yes/no): yes

⏳ Executing market order...

============================================================
  ✓ MARKET ORDER EXECUTED SUCCESSFULLY
============================================================

📊 Order Details:
   Order ID: 123456789
   Symbol: BTCUSDT
   Side: BUY
   Status: FILLED
   Quantity: 0.001
   Executed: 0.001
   Price: 44500.0
   Time: 2026-01-15 10:30:45

============================================================
```

### Example 2: Limit Order with Price Target

```
bot> limit
Symbol (e.g., BTCUSDT): ETHUSDT
Side (BUY/SELL): SELL
Quantity: 0.1
Price: 3200.50

📋 Order Summary:
   Type: LIMIT
   Symbol: ETHUSDT
   Side: SELL
   Quantity: 0.1
   Price: 3200.5

Confirm order? (yes/no): yes

⏳ Placing limit order...

============================================================
  ✓ LIMIT ORDER EXECUTED SUCCESSFULLY
============================================================

📊 Order Details:
   Order ID: 987654321
   Symbol: ETHUSDT
   Side: SELL
   Status: NEW
   Quantity: 0.1
   Executed: 0.0
   Price: 3200.5
   Time in Force: GTC
   Time: 2026-01-15 10:35:22

============================================================
```

### Example 3: Stop-Limit Order for Risk Management

```
bot> stop-limit
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): SELL
Quantity: 0.002
Stop Price (trigger price): 43000
Limit Price (execution price): 42900

📋 Order Summary:
   Type: STOP-LIMIT
   Symbol: BTCUSDT
   Side: SELL
   Quantity: 0.002
   Stop Price: 43000.0
   Limit Price: 42900.0

Confirm order? (yes/no): yes

⏳ Placing stop-limit order...

============================================================
  ✓ STOP-LIMIT ORDER EXECUTED SUCCESSFULLY
============================================================

📊 Order Details:
   Order ID: 456789123
   Symbol: BTCUSDT
   Side: SELL
   Status: NEW
   Quantity: 0.002
   Executed: 0.0
   Price: 42900.0
   Stop Price: 43000.0
   Time in Force: GTC
   Time: 2026-01-15 10:40:15

============================================================
```

### Example 4: OCO Order (Take Profit + Stop Loss)

```
bot> oco
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): SELL
Quantity: 0.001
Limit Price (take profit): 46000
Stop Price (trigger price): 43000
Stop Limit Price (execution price): 42900

📋 Order Summary:
   Type: OCO (One-Cancels-Other)
   Symbol: BTCUSDT
   Side: SELL
   Quantity: 0.001
   Limit Price: 46000.0
   Stop Price: 43000.0
   Stop Limit Price: 42900.0

Confirm order? (yes/no): yes

⏳ Placing OCO order...

============================================================
  ✓ OCO ORDER EXECUTED SUCCESSFULLY
============================================================

📊 OCO Order Details:
   Order List ID: 12345
   Symbol: BTCUSDT
   Status: EXECUTING

   Sub-Orders:
   1. Order ID: 111111
      Type: LIMIT_MAKER
      Side: SELL
   2. Order ID: 222222
      Type: STOP_LOSS_LIMIT
      Side: SELL

   Time: 2026-01-15 10:45:30

============================================================
```

### Example 5: TWAP Strategy for Large Orders

```
bot> twap
Symbol (e.g., BTCUSDT): BTCUSDT
Side (BUY/SELL): BUY
Total Quantity: 0.01
Duration (minutes): 5
Number of intervals (default: 5): 5

📋 TWAP Strategy Summary:
   Symbol: BTCUSDT
   Side: BUY
   Total Quantity: 0.01
   Duration: 5 minutes
   Intervals: 5
   Quantity per interval: 0.00200000
   Time between orders: 60.00 seconds

Confirm TWAP execution? (yes/no): yes

⏳ Executing TWAP strategy (5 intervals over 5 minutes)...
   This may take a while. Please wait...

[Interval 1/5] Executing order for 0.002 BTCUSDT...
✓ Order executed: ID 333333, Price: 44500.0

[Interval 2/5] Executing order for 0.002 BTCUSDT...
✓ Order executed: ID 444444, Price: 44520.0

[Interval 3/5] Executing order for 0.002 BTCUSDT...
✓ Order executed: ID 555555, Price: 44510.0

[Interval 4/5] Executing order for 0.002 BTCUSDT...
✓ Order executed: ID 666666, Price: 44530.0

[Interval 5/5] Executing order for 0.002 BTCUSDT...
✓ Order executed: ID 777777, Price: 44525.0

============================================================
  ✓ TWAP STRATEGY COMPLETED
============================================================

📊 Execution Summary:
   Symbol: BTCUSDT
   Side: BUY
   Total Quantity Requested: 0.01
   Total Quantity Executed: 0.01
   Average Execution Price: 44517.00000000
   Intervals Executed: 5

📋 Individual Orders:
   1. Order ID: 333333
      Quantity: 0.002
      Price: 44500.0
      Status: FILLED
   2. Order ID: 444444
      Quantity: 0.002
      Price: 44520.0
      Status: FILLED
   3. Order ID: 555555
      Quantity: 0.002
      Price: 44510.0
      Status: FILLED
   4. Order ID: 666666
      Quantity: 0.002
      Price: 44530.0
      Status: FILLED
   5. Order ID: 777777
      Quantity: 0.002
      Price: 44525.0
      Status: FILLED

============================================================
```

### Example 6: Grid Trading Strategy

```
bot> grid
Symbol (e.g., BTCUSDT): BTCUSDT
Lower Price (bottom of range): 43000
Upper Price (top of range): 45000
Number of Grid Levels: 5
Total Investment (in quote currency): 100

📋 Grid Strategy Summary:
   Symbol: BTCUSDT
   Price Range: 43000.0 - 45000.0
   Grid Levels: 5
   Price Step: 500.00000000
   Total Investment: 100.0
   Quantity per Grid: 0.00045455

   Note: Grid will run continuously until you stop it.
   Use 'stop-grid' command to stop the strategy.

Start Grid strategy? (yes/no): yes

⏳ Starting Grid strategy...
   Placing initial grid orders...

Placing BUY order at 43000.0...
Placing BUY order at 43500.0...
Placing BUY order at 44000.0...
Placing SELL order at 44500.0...
Placing SELL order at 45000.0...

============================================================
  ✓ GRID STRATEGY STARTED
============================================================

📊 Grid Status:
   Symbol: BTCUSDT
   Active Orders: 5
   Grid Levels: 5
   Price Range: 43000.0 - 45000.0

   The grid is now active and monitoring orders.
   Use 'stop-grid' command to stop the strategy.

============================================================

   Note: Automatic rebalancing requires running 'monitor-grid' command
   or implementing background monitoring in production.

bot> stop-grid

------------------------------------------------------------
  STOP GRID STRATEGY
------------------------------------------------------------

   Active Grid Orders: 5
   Symbol: BTCUSDT

Stop grid strategy and cancel all orders? (yes/no): yes

⏳ Stopping grid strategy...
   Cancelling all active orders...

============================================================
  ✓ GRID STRATEGY STOPPED
============================================================
```

## Dependencies

- `python-binance>=1.0.17` - Binance API client library
- `python-dotenv>=1.0.0` - Environment variable management
- `requests>=2.31.0` - HTTP library
- `pytest>=7.4.0` - Testing framework

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_market_orders.py

# Run with verbose output
pytest -v

# Run specific test function
pytest tests/test_validator.py::test_validate_symbol
```

### Test Structure

```
tests/
├── test_config.py           # Configuration tests
├── test_validator.py        # Input validation tests
├── test_market_orders.py    # Market order tests
├── test_limit_orders.py     # Limit order tests
├── test_stop_limit_orders.py # Stop-limit order tests
├── test_oco_orders.py       # OCO order tests
├── test_oco_validation.py   # OCO validation tests
├── test_logger.py           # Logging tests
└── test_grid_strategy.py    # Grid strategy tests
```

### Code Quality

The project follows Python best practices:
- Type hints for better code clarity
- Comprehensive error handling
- Detailed logging for debugging
- Input validation before API calls
- Modular design for maintainability

### Adding New Features

To add a new order type or strategy:

1. Create a new manager class in `src/` or `src/advanced/`
2. Implement validation in `src/validator.py`
3. Add API method to `src/binance_client.py`
4. Add CLI command in `src/cli.py`
5. Write unit tests in `tests/`
6. Update documentation

## Best Practices

### Trading Best Practices

1. **Start Small**: Always test with small quantities first
2. **Use Testnet**: Never use production API keys for testing
3. **Monitor Logs**: Regularly check `bot.log` for issues
4. **Confirm Orders**: Always review order summaries before confirming
5. **Understand Order Types**: Know the difference between market, limit, and stop orders
6. **Set Stop Losses**: Use stop-limit or OCO orders for risk management
7. **Check Balance**: Ensure sufficient testnet funds before trading
8. **Verify Symbols**: Use valid trading pairs (BTCUSDT, ETHUSDT, etc.)

### Security Best Practices

1. **Never Commit Secrets**: Keep `.env` file out of version control
2. **Use Testnet Keys**: Only use testnet API keys for development
3. **Rotate Keys**: Regularly regenerate API keys
4. **Limit Permissions**: Use API keys with minimal required permissions
5. **Secure Storage**: Store API keys securely
6. **Monitor Activity**: Review bot.log for unauthorized activity

### Development Best Practices

1. **Virtual Environment**: Use Python virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Version Control**: Use git and follow .gitignore rules
   ```bash
   git add .
   git commit -m "Your message"
   ```

3. **Testing**: Run tests before deploying changes
   ```bash
   pytest --cov=src tests/
   ```

4. **Logging**: Use appropriate log levels
   - DEBUG: Detailed information for debugging
   - INFO: General information about bot operations
   - WARNING: Warning messages for potential issues
   - ERROR: Error messages for failures

5. **Error Handling**: Always handle exceptions gracefully
   - Catch specific exceptions
   - Log errors with context
   - Display user-friendly messages
   - Don't expose sensitive information in errors

## Project Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Interface                        │
│                    (src/cli.py)                         │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐    ┌────────▼────────┐
│  Input Validator │    │  Order Managers │
│ (src/validator.py)│    │  (src/*.py)     │
└────────┬────────┘    └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Binance API Client   │
         │ (src/binance_client.py)│
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │    Binance Testnet     │
         │  (External API)        │
         └───────────────────────┘

         ┌───────────────────────┐
         │       Logger           │
         │   (src/logger.py)      │
         │   Logs all activities  │
         └───────────────────────┘
```

### Data Flow

1. **User Input** → CLI receives command
2. **Validation** → InputValidator checks parameters
3. **Order Creation** → OrderManager prepares order
4. **API Call** → BinanceClient sends request
5. **Response** → API returns order result
6. **Logging** → Logger records transaction
7. **Display** → CLI shows result to user

### Key Design Decisions

1. **Modular Architecture**: Each component has a single responsibility
2. **Validation First**: All inputs validated before API calls
3. **Comprehensive Logging**: Every action is logged for audit trail
4. **Error Handling**: Graceful error handling at every layer
5. **User Confirmation**: All orders require explicit confirmation
6. **Testnet Only**: Designed specifically for testnet use

## Security Notes

- Never commit your `.env` file or expose API credentials
- Always use testnet for development and testing
- The bot logs API requests but never logs API secrets
- Keep your API keys secure and rotate them regularly

## Troubleshooting

### Configuration Issues

#### Problem: `BINANCE_API_KEY is required`

**Cause:** Missing or empty API key in `.env` file.

**Solution:**
1. Ensure you have created a `.env` file (copy from `.env.example`)
2. Add your API credentials to the `.env` file:
   ```
   BINANCE_API_KEY=your_actual_api_key_here
   BINANCE_API_SECRET=your_actual_api_secret_here
   ```
3. Verify the credentials are correct (no extra spaces or quotes)
4. Get testnet keys from: https://testnet.binancefuture.com

#### Problem: `Configuration Error: Invalid API credentials`

**Cause:** API key or secret is incorrect or expired.

**Solution:**
1. Log in to Binance Futures Testnet
2. Generate new API keys
3. Update your `.env` file with the new credentials
4. Ensure you're using testnet keys, not production keys

### Connection Issues

#### Problem: `Connection Error: Cannot connect to Binance API`

**Cause:** Network connectivity issues or API unavailability.

**Solution:**
1. Check your internet connection
2. Verify testnet is accessible: https://testnet.binancefuture.com
3. Check if Binance API is experiencing downtime
4. Try again after a few minutes
5. Ensure no firewall is blocking the connection

#### Problem: `Connection timeout`

**Cause:** Slow network or API rate limiting.

**Solution:**
1. Check your network speed
2. Wait a few seconds and try again
3. Reduce the frequency of API calls
4. Check if you've exceeded API rate limits

### Validation Errors

#### Problem: `Validation Error: Symbol XXXUSDT does not exist or is not tradeable`

**Cause:** Invalid trading pair or symbol not available on testnet.

**Solution:**
1. Use valid Binance Futures symbols (e.g., BTCUSDT, ETHUSDT)
2. Ensure the symbol is available on testnet
3. Check symbol spelling and format (must be uppercase)
4. Common valid symbols: BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT

#### Problem: `Validation Error: Quantity is below minimum`

**Cause:** Order quantity is too small for the trading pair.

**Solution:**
1. Increase the quantity
2. Check minimum quantity requirements for the symbol
3. For BTC pairs, minimum is typically 0.001 BTC
4. For ETH pairs, minimum is typically 0.01 ETH

#### Problem: `Validation Error: Invalid price precision`

**Cause:** Price has too many decimal places.

**Solution:**
1. Round the price to the correct precision
2. For BTCUSDT, use 1 decimal place (e.g., 45000.0)
3. For ETHUSDT, use 2 decimal places (e.g., 3000.50)
4. Check the symbol's price precision requirements

### Order Execution Issues

#### Problem: `API Error: Insufficient balance`

**Cause:** Not enough funds in testnet account.

**Solution:**
1. Log in to Binance Futures Testnet
2. Use the testnet faucet to get test funds
3. Ensure you have sufficient balance for the order
4. Remember: testnet funds are free and for testing only

#### Problem: `API Error: Order would immediately trigger`

**Cause:** Limit order price is set to execute immediately (like a market order).

**Solution:**
1. For BUY limit orders, set price below current market price
2. For SELL limit orders, set price above current market price
3. Check current market price before placing limit orders
4. Use market orders if you want immediate execution

#### Problem: `API Error: Invalid order type`

**Cause:** Order parameters don't match the order type requirements.

**Solution:**
1. Ensure all required parameters are provided
2. For stop-limit orders, stop price must trigger before limit price
3. For OCO orders, ensure price relationships are correct
4. Review the order type requirements in the documentation

### TWAP Strategy Issues

#### Problem: `TWAP execution interrupted`

**Cause:** Network issue or API error during execution.

**Solution:**
1. Check the log file for details
2. Verify which orders were executed
3. Manually place remaining orders if needed
4. Ensure stable internet connection for long-running strategies

#### Problem: `TWAP orders executing too slowly`

**Cause:** Long duration with many intervals.

**Solution:**
1. Reduce the number of intervals
2. Shorten the duration
3. Be patient - TWAP is designed to execute slowly to minimize market impact

### Grid Strategy Issues

#### Problem: `Grid strategy not rebalancing`

**Cause:** Automatic monitoring not implemented in basic version.

**Solution:**
1. This is expected behavior in the current implementation
2. Grid orders are placed but automatic rebalancing requires background monitoring
3. For production use, implement background monitoring thread
4. Manually monitor and rebalance if needed

#### Problem: `Cannot start grid - already running`

**Cause:** A grid strategy is already active.

**Solution:**
1. Use `stop-grid` command to stop the current strategy
2. Wait for all orders to be cancelled
3. Start a new grid strategy

### Logging Issues

#### Problem: `bot.log file not created`

**Cause:** Permission issues or invalid log file path.

**Solution:**
1. Ensure you have write permissions in the project directory
2. Check the LOG_FILE setting in `.env`
3. Try running with administrator/sudo privileges if needed
4. Verify the directory exists

#### Problem: `Log file too large`

**Cause:** Extensive bot usage without log rotation.

**Solution:**
1. Delete or archive the old `bot.log` file
2. The bot will create a new log file automatically
3. Consider implementing log rotation for production use
4. Review log level settings (use INFO instead of DEBUG)

### General Issues

#### Problem: `ModuleNotFoundError: No module named 'binance'`

**Cause:** Dependencies not installed.

**Solution:**
```bash
pip install -r requirements.txt
```

#### Problem: `Python version error`

**Cause:** Python version is too old.

**Solution:**
1. Ensure Python 3.8 or higher is installed
2. Check version: `python --version`
3. Upgrade Python if needed
4. Use virtual environment to avoid conflicts

#### Problem: `Bot freezes or becomes unresponsive`

**Cause:** Long-running operation or network timeout.

**Solution:**
1. Wait for the current operation to complete
2. Press Ctrl+C to interrupt and exit
3. Check the log file for details
4. Restart the bot

### Getting Help

If you encounter issues not covered here:

1. Check the `bot.log` file for detailed error messages
2. Review the requirements and design documents in `.kiro/specs/`
3. Verify your testnet account status and API keys
4. Ensure all dependencies are correctly installed
5. Test with small quantities first

### Common Testnet Limitations

- Testnet may have different symbols available than production
- Testnet liquidity is limited - large orders may not fill
- Testnet may experience downtime or maintenance
- API rate limits may differ from production
- Testnet funds are reset periodically

## Frequently Asked Questions (FAQ)

### General Questions

**Q: Is this bot safe to use with real money?**
A: No! This bot is designed exclusively for Binance Futures Testnet. Never use production API keys. Always test thoroughly on testnet before considering any production use.

**Q: How do I get testnet funds?**
A: Log in to https://testnet.binancefuture.com and use the testnet faucet to get free test USDT.

**Q: Can I use this bot for spot trading?**
A: No, this bot is specifically designed for Binance Futures. It would require modifications for spot trading.

**Q: What trading pairs are supported?**
A: Any trading pair available on Binance Futures Testnet (e.g., BTCUSDT, ETHUSDT, BNBUSDT, ADAUSDT, etc.).

### Order Questions

**Q: What's the difference between market and limit orders?**
A: Market orders execute immediately at the current market price. Limit orders only execute when the market reaches your specified price.

**Q: When should I use stop-limit orders?**
A: Use stop-limit orders for automated risk management. They trigger when the market reaches your stop price and then execute as a limit order.

**Q: What are OCO orders good for?**
A: OCO (One-Cancels-Other) orders let you set both a profit target and stop loss simultaneously. When one order fills, the other is automatically cancelled.

**Q: How does TWAP help with large orders?**
A: TWAP splits large orders into smaller chunks executed over time, reducing market impact and getting better average prices.

**Q: Is grid trading profitable?**
A: Grid trading can be profitable in ranging markets with price oscillations. It's less effective in strong trending markets.

### Technical Questions

**Q: Why isn't my order executing?**
A: Check: 1) Sufficient balance, 2) Valid symbol, 3) Correct price (limit orders), 4) Minimum quantity requirements, 5) Network connection.

**Q: Can I run multiple strategies simultaneously?**
A: Currently, only one grid strategy can run at a time. You can execute other order types while a grid is active.

**Q: How do I cancel an order?**
A: This bot doesn't include order cancellation. Use the Binance Testnet web interface to cancel orders, or use `stop-grid` for grid strategies.

**Q: Where are my orders stored?**
A: Orders are stored on Binance's servers. The bot logs order details to `bot.log` for your records.

**Q: Can I automate the bot without manual input?**
A: The current implementation requires manual input for each order. For automation, you would need to modify the code to accept command-line arguments or configuration files.

### Configuration Questions

**Q: Can I change the log file location?**
A: Yes, set `LOG_FILE` in your `.env` file to any path you prefer.

**Q: What log level should I use?**
A: Use `INFO` for normal operation, `DEBUG` for troubleshooting, `WARNING` for minimal logging, `ERROR` for errors only.

**Q: Can I use this with production API?**
A: Technically yes (set `BINANCE_TESTNET=false`), but it's strongly discouraged. This bot is for educational purposes and testnet use only.

**Q: How do I update my API keys?**
A: Edit the `.env` file and update `BINANCE_API_KEY` and `BINANCE_API_SECRET`. Restart the bot for changes to take effect.

### Troubleshooting Questions

**Q: The bot says "Symbol does not exist" but I know it's valid. Why?**
A: Ensure: 1) Symbol is uppercase, 2) Symbol exists on testnet (not all production symbols are on testnet), 3) No spaces in symbol name.

**Q: Why do my orders show as "NEW" instead of "FILLED"?**
A: Limit orders show as "NEW" until the market reaches your price. Market orders typically fill immediately and show as "FILLED".

**Q: The TWAP strategy stopped in the middle. What happened?**
A: Check `bot.log` for errors. Common causes: network issues, insufficient balance, API errors. Completed orders are logged.

**Q: Can I recover from a crash?**
A: The bot doesn't maintain state between runs. Check `bot.log` to see what orders were executed. Use the Binance web interface to check order status.

## Advanced Usage

### Custom Order Strategies

You can extend the bot with custom strategies by:

1. Creating a new strategy class in `src/advanced/`
2. Following the pattern of existing strategies (TWAP, Grid)
3. Adding validation logic
4. Integrating with the CLI

Example strategy structure:
```python
class CustomStrategy:
    def __init__(self, client: BinanceClient, logger: BotLogger):
        self.client = client
        self.logger = logger
    
    def execute(self, **params):
        # Your strategy logic here
        pass
```

### Batch Order Execution

For executing multiple orders from a file:

1. Create a JSON file with order details
2. Write a script to read the file
3. Use the order managers to execute each order
4. Log results for review

### Integration with Other Tools

The bot can be integrated with:
- Trading view alerts (via webhooks)
- Custom indicators (via Python libraries)
- Portfolio management tools
- Risk management systems
- Notification services (email, SMS, Telegram)

### Performance Monitoring

Monitor bot performance by:
1. Analyzing `bot.log` for execution times
2. Tracking order fill rates
3. Calculating average execution prices
4. Monitoring API response times
5. Reviewing error rates

## Contributing

This is an educational project. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## Changelog

### Version 1.0.0 (Current)
- Initial release
- Market order execution
- Limit order execution
- Stop-limit order execution
- OCO order execution
- TWAP strategy implementation
- Grid trading strategy implementation
- Comprehensive logging
- Input validation
- Interactive CLI interface
- Full documentation

## License

This project is for educational purposes only. Use at your own risk.

## Disclaimer

**IMPORTANT DISCLAIMERS:**

1. **Educational Purpose**: This bot is created for educational purposes to demonstrate trading bot development and API integration.

2. **Testnet Only**: This bot is designed exclusively for Binance Futures Testnet. Do not use with production API keys or real funds.

3. **No Warranty**: This software is provided "as is" without warranty of any kind. The authors are not responsible for any losses or damages.

4. **Trading Risks**: Cryptocurrency trading involves substantial risk of loss. This bot does not guarantee profits.

5. **Not Financial Advice**: This bot and its documentation do not constitute financial advice. Always do your own research.

6. **API Usage**: Ensure you comply with Binance's API terms of service and usage guidelines.

7. **Security**: Always keep your API keys secure. Never share them or commit them to version control.

8. **Testing Required**: Thoroughly test any modifications before use. Start with small quantities.

9. **No Support**: This is an educational project with no official support. Use community resources for help.

10. **Regulatory Compliance**: Ensure your trading activities comply with local laws and regulations.

## Acknowledgments

- Binance for providing the Futures Testnet API
- python-binance library for API integration
- The Python community for excellent libraries and tools

## Contact and Resources

- Binance Futures Testnet: https://testnet.binancefuture.com
- Binance API Documentation: https://binance-docs.github.io/apidocs/futures/en/
- python-binance Documentation: https://python-binance.readthedocs.io/

## Support

For issues and questions:
1. Check this README and documentation
2. Review the troubleshooting section
3. Check `bot.log` for error details
4. Review the requirements and design documents in `.kiro/specs/`
5. Consult Binance API documentation

---

**Happy Trading on Testnet! 🚀**

Remember: This is a learning tool. Always test thoroughly and never risk real funds without proper testing and risk management.
