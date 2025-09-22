from django.db import models

from HindAi_users.models import HindAIUser as User

class MarketOrder(models.Model):
    # Foreign key to User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_orders')
    
    # Basic order info
    action = models.CharField(max_length=10)
    brokerage_order_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20)
    
    # Quantities
    total_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    canceled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    open_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Prices
    execution_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    limit_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    stop_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Order details
    order_type = models.CharField(max_length=20, null=True, blank=True)
    time_in_force = models.CharField(max_length=20, null=True, blank=True)
    symbol = models.CharField(max_length=255)
    option_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    time_placed = models.DateTimeField(null=True, blank=True)
    time_executed = models.DateTimeField(null=True, blank=True)
    time_updated = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Universal Symbol details
    raw_symbol = models.CharField(max_length=20, null=True, blank=True)
    symbol_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    figi_code = models.CharField(max_length=50, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    
    # Exchange details
    exchange_code = models.CharField(max_length=20, null=True, blank=True)
    exchange_name = models.CharField(max_length=100, null=True, blank=True)
    exchange_mic_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_timezone = models.CharField(max_length=50, null=True, blank=True)
    
    # Currency details
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    quote_currency = models.CharField(max_length=10, null=True, blank=True)
    
    # Additional fields
    child_brokerage_order_ids = models.JSONField(null=True, blank=True)
    quote_universal_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time_placed']
        verbose_name = 'Market Order'
        verbose_name_plural = 'Market Orders'
    
    def __str__(self):
        return f"{self.action} {self.total_quantity} {self.raw_symbol} - {self.status}"

class LimitOrder(models.Model):
    # Foreign key to User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='limit_orders')
    
    # Basic order info
    action = models.CharField(max_length=10)
    brokerage_order_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20)
    
    # Quantities
    total_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    canceled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    open_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Prices
    execution_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    limit_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    stop_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Order details
    order_type = models.CharField(max_length=20, null=True, blank=True)
    time_in_force = models.CharField(max_length=20, null=True, blank=True)
    symbol = models.CharField(max_length=255)  # This stores the UUID from API
    option_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    time_placed = models.DateTimeField(null=True, blank=True)
    time_executed = models.DateTimeField(null=True, blank=True)
    time_updated = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Universal Symbol details
    universal_symbol_id = models.CharField(max_length=255, null=True, blank=True)
    raw_symbol = models.CharField(max_length=20, null=True, blank=True)
    symbol_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    figi_code = models.CharField(max_length=50, null=True, blank=True)
    figi_share_class = models.CharField(max_length=50, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    
    # Exchange details
    exchange_id = models.CharField(max_length=255, null=True, blank=True)
    exchange_code = models.CharField(max_length=20, null=True, blank=True)
    exchange_name = models.CharField(max_length=100, null=True, blank=True)
    exchange_mic_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_timezone = models.CharField(max_length=50, null=True, blank=True)
    exchange_suffix = models.CharField(max_length=10, null=True, blank=True)
    exchange_start_time = models.TimeField(null=True, blank=True)
    exchange_close_time = models.TimeField(null=True, blank=True)
    
    # Currency details
    currency_id = models.CharField(max_length=255, null=True, blank=True)
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    quote_currency = models.CharField(max_length=10, null=True, blank=True)
    
    # Security type details
    security_type_id = models.CharField(max_length=255, null=True, blank=True)
    security_type_code = models.CharField(max_length=10, null=True, blank=True)
    security_type_description = models.CharField(max_length=100, null=True, blank=True)
    security_type_is_supported = models.BooleanField(default=True)
    
    # Additional fields
    child_brokerage_order_ids = models.JSONField(null=True, blank=True)
    quote_universal_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time_placed']
        verbose_name = 'Limit Order'
        verbose_name_plural = 'Limit Orders'
    
    def __str__(self):
        return f"{self.action} {self.total_quantity} {self.raw_symbol} - {self.status}"

class StopOrder(models.Model):
    # Foreign key to User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stop_orders')
    
    # Basic order info
    action = models.CharField(max_length=10)
    brokerage_order_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20)
    
    # Quantities
    total_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    canceled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    open_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Prices
    execution_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    limit_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    stop_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Order details
    order_type = models.CharField(max_length=20, null=True, blank=True)
    time_in_force = models.CharField(max_length=20, null=True, blank=True)
    symbol = models.CharField(max_length=255)  # This stores the UUID from API
    option_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    time_placed = models.DateTimeField(null=True, blank=True)
    time_executed = models.DateTimeField(null=True, blank=True)
    time_updated = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Universal Symbol details
    universal_symbol_id = models.CharField(max_length=255, null=True, blank=True)
    raw_symbol = models.CharField(max_length=20, null=True, blank=True)
    symbol_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    figi_code = models.CharField(max_length=50, null=True, blank=True)
    figi_share_class = models.CharField(max_length=50, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    
    # Exchange details
    exchange_id = models.CharField(max_length=255, null=True, blank=True)
    exchange_code = models.CharField(max_length=20, null=True, blank=True)
    exchange_name = models.CharField(max_length=100, null=True, blank=True)
    exchange_mic_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_timezone = models.CharField(max_length=50, null=True, blank=True)
    exchange_suffix = models.CharField(max_length=10, null=True, blank=True)
    exchange_start_time = models.TimeField(null=True, blank=True)
    exchange_close_time = models.TimeField(null=True, blank=True)
    
    # Currency details
    currency_id = models.CharField(max_length=255, null=True, blank=True)
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    quote_currency = models.CharField(max_length=10, null=True, blank=True)
    
    # Security type details
    security_type_id = models.CharField(max_length=255, null=True, blank=True)
    security_type_code = models.CharField(max_length=10, null=True, blank=True)
    security_type_description = models.CharField(max_length=100, null=True, blank=True)
    security_type_is_supported = models.BooleanField(default=True)
    
    # Additional fields
    child_brokerage_order_ids = models.JSONField(null=True, blank=True)
    quote_universal_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time_placed']
        verbose_name = 'Stop Order'
        verbose_name_plural = 'Stop Orders'
    
    def __str__(self):
        return f"{self.action} {self.total_quantity} {self.raw_symbol} - {self.status}"

class StopLimitOrder(models.Model):
    # Foreign key to User
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stoplimit_orders')
    
    # Basic order info
    action = models.CharField(max_length=10)
    brokerage_order_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20)
    
    # Quantities
    total_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    canceled_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    open_quantity = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Prices
    execution_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    limit_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    stop_price = models.DecimalField(max_digits=15, decimal_places=9, null=True, blank=True)
    
    # Order details
    order_type = models.CharField(max_length=20, null=True, blank=True)
    time_in_force = models.CharField(max_length=20, null=True, blank=True)
    symbol = models.CharField(max_length=255)  # This stores the UUID from API
    option_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Timestamps
    time_placed = models.DateTimeField(null=True, blank=True)
    time_executed = models.DateTimeField(null=True, blank=True)
    time_updated = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    
    # Universal Symbol details
    universal_symbol_id = models.CharField(max_length=255, null=True, blank=True)
    raw_symbol = models.CharField(max_length=20, null=True, blank=True)
    symbol_name = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    figi_code = models.CharField(max_length=50, null=True, blank=True)
    figi_share_class = models.CharField(max_length=50, null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    
    # Exchange details
    exchange_id = models.CharField(max_length=255, null=True, blank=True)
    exchange_code = models.CharField(max_length=20, null=True, blank=True)
    exchange_name = models.CharField(max_length=100, null=True, blank=True)
    exchange_mic_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_timezone = models.CharField(max_length=50, null=True, blank=True)
    exchange_suffix = models.CharField(max_length=10, null=True, blank=True)
    exchange_start_time = models.TimeField(null=True, blank=True)
    exchange_close_time = models.TimeField(null=True, blank=True)
    
    # Currency details
    currency_id = models.CharField(max_length=255, null=True, blank=True)
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    currency_name = models.CharField(max_length=50, null=True, blank=True)
    quote_currency = models.CharField(max_length=10, null=True, blank=True)
    
    # Security type details
    security_type_id = models.CharField(max_length=255, null=True, blank=True)
    security_type_code = models.CharField(max_length=10, null=True, blank=True)
    security_type_description = models.CharField(max_length=100, null=True, blank=True)
    security_type_is_supported = models.BooleanField(default=True)
    
    # Additional fields
    child_brokerage_order_ids = models.JSONField(null=True, blank=True)
    quote_universal_symbol = models.CharField(max_length=255, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time_placed']
        verbose_name = 'Stop Limit Order'
        verbose_name_plural = 'Stop Limit Orders'
    
    def __str__(self):
        return f"{self.action} {self.total_quantity} {self.raw_symbol} - {self.status}"
