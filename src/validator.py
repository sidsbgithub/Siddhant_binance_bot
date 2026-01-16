"""Input validation for trading bot."""

from typing import Tuple, Optional, Dict, Any
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class InputValidator:
    """
    Validates trading inputs against business rules and API constraints.
    Returns tuple of (is_valid, error_message) for clear error reporting.
    """
    
    def __init__(self, binance_client):
        """
        Initialize validator with Binance client for symbol info lookups.
        
        Args:
            binance_client: BinanceClient instance for retrieving symbol information.
        """
        self.client = binance_client
        self.valid_sides = ["BUY", "SELL"]
        self._symbol_cache: Dict[str, Dict[str, Any]] = {}
    
    def _get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get symbol information with caching.
        
        Args:
            symbol: Trading pair symbol.
            
        Returns:
            dict: Symbol information or None if not found.
        """
        # Check cache first
        if symbol in self._symbol_cache:
            return self._symbol_cache[symbol]
        
        try:
            symbol_info = self.client.get_symbol_info(symbol)
            self._symbol_cache[symbol] = symbol_info
            return symbol_info
        except Exception:
            return None
    
    def _get_filter_value(self, symbol_info: Dict[str, Any], filter_type: str, key: str) -> Optional[str]:
        """
        Extract filter value from symbol info.
        
        Args:
            symbol_info: Symbol information dictionary.
            filter_type: Type of filter (e.g., 'LOT_SIZE', 'PRICE_FILTER').
            key: Key to extract from filter (e.g., 'minQty', 'minPrice').
            
        Returns:
            str: Filter value or None if not found.
        """
        filters = symbol_info.get('filters', [])
        for f in filters:
            if f.get('filterType') == filter_type:
                return f.get(key)
        return None
    
    def validate_symbol(self, symbol: str) -> Tuple[bool, str]:
        """
        Validate symbol exists and is tradeable.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT').
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not symbol:
            return False, "Symbol cannot be empty"
        
        # Convert to uppercase for consistency
        symbol = symbol.upper()
        
        # Get symbol info
        symbol_info = self._get_symbol_info(symbol)
        
        if not symbol_info:
            return False, f"Symbol '{symbol}' not found or not available"
        
        # Check if symbol is tradeable
        status = symbol_info.get('status')
        if status != 'TRADING':
            return False, f"Symbol '{symbol}' is not tradeable (status: {status})"
        
        return True, ""
    
    def validate_quantity(self, quantity: float, symbol: str) -> Tuple[bool, str]:
        """
        Validate quantity meets minimum requirements and precision.
        
        Args:
            quantity: Order quantity.
            symbol: Trading pair symbol.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if quantity is positive
        if quantity <= 0:
            return False, "Quantity must be greater than zero"
        
        # Get symbol info
        symbol_info = self._get_symbol_info(symbol)
        if not symbol_info:
            return False, f"Cannot validate quantity: symbol '{symbol}' not found"
        
        # Get LOT_SIZE filter
        min_qty = self._get_filter_value(symbol_info, 'LOT_SIZE', 'minQty')
        max_qty = self._get_filter_value(symbol_info, 'LOT_SIZE', 'maxQty')
        step_size = self._get_filter_value(symbol_info, 'LOT_SIZE', 'stepSize')
        
        # Validate minimum quantity
        if min_qty:
            try:
                min_qty_decimal = Decimal(min_qty)
                if Decimal(str(quantity)) < min_qty_decimal:
                    return False, f"Quantity {quantity} is below minimum {min_qty} for {symbol}"
            except (InvalidOperation, ValueError):
                pass
        
        # Validate maximum quantity
        if max_qty:
            try:
                max_qty_decimal = Decimal(max_qty)
                if Decimal(str(quantity)) > max_qty_decimal:
                    return False, f"Quantity {quantity} exceeds maximum {max_qty} for {symbol}"
            except (InvalidOperation, ValueError):
                pass
        
        # Validate step size (precision)
        if step_size:
            try:
                step_decimal = Decimal(step_size)
                quantity_decimal = Decimal(str(quantity))
                min_qty_decimal = Decimal(min_qty) if min_qty else Decimal('0')
                
                # Check if quantity matches step size
                remainder = (quantity_decimal - min_qty_decimal) % step_decimal
                if remainder != 0:
                    return False, f"Quantity {quantity} does not match step size {step_size} for {symbol}"
            except (InvalidOperation, ValueError):
                pass
        
        return True, ""
    
    def validate_price(self, price: float, symbol: str) -> Tuple[bool, str]:
        """
        Validate price is within acceptable range and precision.
        
        Args:
            price: Order price.
            symbol: Trading pair symbol.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if price is positive
        if price <= 0:
            return False, "Price must be greater than zero"
        
        # Get symbol info
        symbol_info = self._get_symbol_info(symbol)
        if not symbol_info:
            return False, f"Cannot validate price: symbol '{symbol}' not found"
        
        # Get PRICE_FILTER
        min_price = self._get_filter_value(symbol_info, 'PRICE_FILTER', 'minPrice')
        max_price = self._get_filter_value(symbol_info, 'PRICE_FILTER', 'maxPrice')
        tick_size = self._get_filter_value(symbol_info, 'PRICE_FILTER', 'tickSize')
        
        # Validate minimum price
        if min_price:
            try:
                min_price_decimal = Decimal(min_price)
                if Decimal(str(price)) < min_price_decimal:
                    return False, f"Price {price} is below minimum {min_price} for {symbol}"
            except (InvalidOperation, ValueError):
                pass
        
        # Validate maximum price
        if max_price:
            try:
                max_price_decimal = Decimal(max_price)
                if Decimal(str(price)) > max_price_decimal:
                    return False, f"Price {price} exceeds maximum {max_price} for {symbol}"
            except (InvalidOperation, ValueError):
                pass
        
        # Validate tick size (price precision)
        if tick_size:
            try:
                tick_decimal = Decimal(tick_size)
                price_decimal = Decimal(str(price))
                
                # Check if price matches tick size
                remainder = price_decimal % tick_decimal
                if remainder != 0:
                    return False, f"Price {price} does not match tick size {tick_size} for {symbol}"
            except (InvalidOperation, ValueError):
                pass
        
        return True, ""
    
    def validate_side(self, side: str) -> Tuple[bool, str]:
        """
        Validate order side is BUY or SELL.
        
        Args:
            side: Order side.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not side:
            return False, "Side cannot be empty"
        
        # Convert to uppercase for consistency
        side = side.upper()
        
        if side not in self.valid_sides:
            return False, f"Side must be either 'BUY' or 'SELL', got '{side}'"
        
        return True, ""
    
    def validate_market_order(self, symbol: str, side: str, quantity: float) -> Tuple[bool, str]:
        """
        Validate all market order parameters.
        
        Args:
            symbol: Trading pair symbol.
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate symbol
        is_valid, error_msg = self.validate_symbol(symbol)
        if not is_valid:
            return False, error_msg
        
        # Validate side
        is_valid, error_msg = self.validate_side(side)
        if not is_valid:
            return False, error_msg
        
        # Validate quantity
        is_valid, error_msg = self.validate_quantity(quantity, symbol.upper())
        if not is_valid:
            return False, error_msg
        
        return True, ""
    
    def validate_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float
    ) -> Tuple[bool, str]:
        """
        Validate all limit order parameters.
        
        Args:
            symbol: Trading pair symbol.
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            price: Limit price.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate symbol
        is_valid, error_msg = self.validate_symbol(symbol)
        if not is_valid:
            return False, error_msg
        
        # Validate side
        is_valid, error_msg = self.validate_side(side)
        if not is_valid:
            return False, error_msg
        
        # Validate quantity
        is_valid, error_msg = self.validate_quantity(quantity, symbol.upper())
        if not is_valid:
            return False, error_msg
        
        # Validate price
        is_valid, error_msg = self.validate_price(price, symbol.upper())
        if not is_valid:
            return False, error_msg
        
        return True, ""
    
    def validate_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        limit_price: float
    ) -> Tuple[bool, str]:
        """
        Validate all stop-limit order parameters.
        
        Args:
            symbol: Trading pair symbol.
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            stop_price: Stop price to trigger the order.
            limit_price: Limit price for the order.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate symbol
        is_valid, error_msg = self.validate_symbol(symbol)
        if not is_valid:
            return False, error_msg
        
        # Validate side
        is_valid, error_msg = self.validate_side(side)
        if not is_valid:
            return False, error_msg
        
        # Validate quantity
        is_valid, error_msg = self.validate_quantity(quantity, symbol.upper())
        if not is_valid:
            return False, error_msg
        
        # Validate stop price
        is_valid, error_msg = self.validate_price(stop_price, symbol.upper())
        if not is_valid:
            return False, f"Stop price validation failed: {error_msg}"
        
        # Validate limit price
        is_valid, error_msg = self.validate_price(limit_price, symbol.upper())
        if not is_valid:
            return False, f"Limit price validation failed: {error_msg}"
        
        # Validate price relationship based on side
        if side.upper() == 'BUY':
            # For buy stop-limit: stop_price should be >= current market price
            # and limit_price should be >= stop_price
            if limit_price < stop_price:
                return False, f"For BUY stop-limit, limit price ({limit_price}) should be >= stop price ({stop_price})"
        elif side.upper() == 'SELL':
            # For sell stop-limit: stop_price should be <= current market price
            # and limit_price should be <= stop_price
            if limit_price > stop_price:
                return False, f"For SELL stop-limit, limit price ({limit_price}) should be <= stop price ({stop_price})"
        
        return True, ""
    
    def validate_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        stop_limit_price: float
    ) -> Tuple[bool, str]:
        """
        Validate all OCO order parameters.
        
        Args:
            symbol: Trading pair symbol.
            side: Order side ('BUY' or 'SELL').
            quantity: Order quantity.
            price: Limit order price.
            stop_price: Stop price to trigger stop-limit order.
            stop_limit_price: Limit price for stop-limit order.
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Validate symbol
        is_valid, error_msg = self.validate_symbol(symbol)
        if not is_valid:
            return False, error_msg
        
        # Validate side
        is_valid, error_msg = self.validate_side(side)
        if not is_valid:
            return False, error_msg
        
        # Validate quantity
        is_valid, error_msg = self.validate_quantity(quantity, symbol.upper())
        if not is_valid:
            return False, error_msg
        
        # Validate limit order price
        is_valid, error_msg = self.validate_price(price, symbol.upper())
        if not is_valid:
            return False, f"Limit price validation failed: {error_msg}"
        
        # Validate stop price
        is_valid, error_msg = self.validate_price(stop_price, symbol.upper())
        if not is_valid:
            return False, f"Stop price validation failed: {error_msg}"
        
        # Validate stop limit price
        is_valid, error_msg = self.validate_price(stop_limit_price, symbol.upper())
        if not is_valid:
            return False, f"Stop limit price validation failed: {error_msg}"
        
        # Validate price relationships based on side
        side_upper = side.upper()
        
        if side_upper == 'SELL':
            # For SELL OCO:
            # - Limit price should be above current price (take profit)
            # - Stop price should be below current price (stop loss)
            # - Stop limit price should be <= stop price
            if price <= stop_price:
                return False, f"For SELL OCO, limit price ({price}) should be > stop price ({stop_price})"
            if stop_limit_price > stop_price:
                return False, f"For SELL OCO, stop limit price ({stop_limit_price}) should be <= stop price ({stop_price})"
        
        elif side_upper == 'BUY':
            # For BUY OCO:
            # - Limit price should be below current price (take profit on short)
            # - Stop price should be above current price (stop loss on short)
            # - Stop limit price should be >= stop price
            if price >= stop_price:
                return False, f"For BUY OCO, limit price ({price}) should be < stop price ({stop_price})"
            if stop_limit_price < stop_price:
                return False, f"For BUY OCO, stop limit price ({stop_limit_price}) should be >= stop price ({stop_price})"
        
        return True, ""
    
    def clear_cache(self) -> None:
        """Clear the symbol info cache."""
        self._symbol_cache.clear()
