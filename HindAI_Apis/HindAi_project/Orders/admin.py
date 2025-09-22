from django.contrib import admin

from HindAi_users.models import HindAIUser as User
# Register your models here.

from .models import MarketOrder, LimitOrder, StopOrder, StopLimitOrder

@admin.register(MarketOrder)
class MarketOrderAdmin(admin.ModelAdmin):
    list_display = [
        'brokerage_order_id', 'user', 'action', 'raw_symbol', 
        'total_quantity', 'status', 'time_placed'
    ]
    list_filter = ['action', 'status', 'time_placed', 'exchange_code']
    search_fields = ['brokerage_order_id', 'raw_symbol', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action', 'brokerage_order_id', 'status')
        }),
        ('Order Details', {
            'fields': (
                'total_quantity', 'filled_quantity', 'canceled_quantity', 'open_quantity',
                'execution_price', 'limit_price', 'stop_price', 'order_type', 'time_in_force'
            )
        }),
        ('Symbol Information', {
            'fields': (
                'symbol', 'raw_symbol', 'symbol_name', 'description', 
                'figi_code', 'logo_url', 'option_symbol'
            )
        }),
        ('Exchange & Currency', {
            'fields': (
                'exchange_code', 'exchange_name', 'exchange_mic_code', 'exchange_timezone',
                'currency_code', 'currency_name', 'quote_currency'
            )
        }),
        ('Timestamps', {
            'fields': ('time_placed', 'time_executed', 'time_updated', 'expiry_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(LimitOrder)
class LimitOrderAdmin(admin.ModelAdmin):
    list_display = [
        'brokerage_order_id', 'user', 'action', 'raw_symbol', 
        'total_quantity', 'limit_price', 'stop_price', 'status', 'time_placed'
    ]
    list_filter = ['action', 'status', 'time_placed', 'time_in_force', 'exchange_code', 'security_type_code']
    search_fields = ['brokerage_order_id', 'raw_symbol', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action', 'brokerage_order_id', 'status')
        }),
        ('Order Details', {
            'fields': (
                'total_quantity', 'filled_quantity', 'canceled_quantity', 'open_quantity',
                'execution_price', 'limit_price', 'stop_price', 'order_type', 'time_in_force'
            )
        }),
        ('Symbol Information', {
            'fields': (
                'symbol', 'universal_symbol_id', 'raw_symbol', 'symbol_name', 'description', 
                'figi_code', 'figi_share_class', 'logo_url', 'option_symbol'
            )
        }),
        ('Exchange Details', {
            'fields': (
                'exchange_id', 'exchange_code', 'exchange_name', 'exchange_mic_code', 
                'exchange_timezone', 'exchange_suffix', 'exchange_start_time', 'exchange_close_time'
            )
        }),
        ('Currency Details', {
            'fields': (
                'currency_id', 'currency_code', 'currency_name', 'quote_currency'
            )
        }),
        ('Security Type', {
            'fields': (
                'security_type_id', 'security_type_code', 'security_type_description', 
                'security_type_is_supported'
            )
        }),
        ('Timestamps', {
            'fields': ('time_placed', 'time_executed', 'time_updated', 'expiry_date')
        }),
        ('Additional Information', {
            'fields': ('child_brokerage_order_ids', 'quote_universal_symbol'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(StopOrder)
class StopOrderAdmin(admin.ModelAdmin):
    list_display = [
        'brokerage_order_id', 'user', 'action', 'raw_symbol', 
        'total_quantity', 'stop_price', 'status', 'time_placed'
    ]
    list_filter = ['action', 'status', 'time_placed', 'time_in_force', 'exchange_code', 'security_type_code']
    search_fields = ['brokerage_order_id', 'raw_symbol', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action', 'brokerage_order_id', 'status')
        }),
        ('Order Details', {
            'fields': (
                'total_quantity', 'filled_quantity', 'canceled_quantity', 'open_quantity',
                'execution_price', 'limit_price', 'stop_price', 'order_type', 'time_in_force'
            )
        }),
        ('Symbol Information', {
            'fields': (
                'symbol', 'universal_symbol_id', 'raw_symbol', 'symbol_name', 'description', 
                'figi_code', 'figi_share_class', 'logo_url', 'option_symbol'
            )
        }),
        ('Exchange Details', {
            'fields': (
                'exchange_id', 'exchange_code', 'exchange_name', 'exchange_mic_code', 
                'exchange_timezone', 'exchange_suffix', 'exchange_start_time', 'exchange_close_time'
            )
        }),
        ('Currency Details', {
            'fields': (
                'currency_id', 'currency_code', 'currency_name', 'quote_currency'
            )
        }),
        ('Security Type', {
            'fields': (
                'security_type_id', 'security_type_code', 'security_type_description', 
                'security_type_is_supported'
            )
        }),
        ('Timestamps', {
            'fields': ('time_placed', 'time_executed', 'time_updated', 'expiry_date')
        }),
        ('Additional Information', {
            'fields': ('child_brokerage_order_ids', 'quote_universal_symbol'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(StopLimitOrder)
class StopLimitOrderAdmin(admin.ModelAdmin):
    list_display = [
        'brokerage_order_id', 'user', 'action', 'raw_symbol', 
        'total_quantity', 'limit_price', 'stop_price', 'status', 'time_placed'
    ]
    list_filter = ['action', 'status', 'time_placed', 'time_in_force', 'exchange_code', 'security_type_code']
    search_fields = ['brokerage_order_id', 'raw_symbol', 'user__username', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'action', 'brokerage_order_id', 'status')
        }),
        ('Order Details', {
            'fields': (
                'total_quantity', 'filled_quantity', 'canceled_quantity', 'open_quantity',
                'execution_price', 'limit_price', 'stop_price', 'order_type', 'time_in_force'
            )
        }),
        ('Symbol Information', {
            'fields': (
                'symbol', 'universal_symbol_id', 'raw_symbol', 'symbol_name', 'description', 
                'figi_code', 'figi_share_class', 'logo_url', 'option_symbol'
            )
        }),
        ('Exchange Details', {
            'fields': (
                'exchange_id', 'exchange_code', 'exchange_name', 'exchange_mic_code', 
                'exchange_timezone', 'exchange_suffix', 'exchange_start_time', 'exchange_close_time'
            )
        }),
        ('Currency Details', {
            'fields': (
                'currency_id', 'currency_code', 'currency_name', 'quote_currency'
            )
        }),
        ('Security Type', {
            'fields': (
                'security_type_id', 'security_type_code', 'security_type_description', 
                'security_type_is_supported'
            )
        }),
        ('Timestamps', {
            'fields': ('time_placed', 'time_executed', 'time_updated', 'expiry_date')
        }),
        ('Additional Information', {
            'fields': ('child_brokerage_order_ids', 'quote_universal_symbol'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
