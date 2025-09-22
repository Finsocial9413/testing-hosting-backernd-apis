from django.contrib import admin
from .models import RazorpayPaymentGateway

@admin.register(RazorpayPaymentGateway)
class RazorpayPaymentGatewayAdmin(admin.ModelAdmin):
    list_display = [
        'razorpay_order_id', 
        'user_username', 
        'amount_in_rupees', 
        'currency', 
        'receipt', 
        'status', 
        'created_timestamp'
    ]
    
    list_filter = [
        'status', 
        'currency', 
        'created_timestamp', 
        'updated_timestamp'
    ]
    
    search_fields = [
        'razorpay_order_id', 
        'receipt', 
        'user__username', 
        'user__email'
    ]
    
    readonly_fields = [
        'razorpay_order_id', 
        'entity', 
        'created_at', 
        'created_timestamp', 
        'updated_timestamp',
        'amount_in_rupees'
    ]
    
    fieldsets = (
        ('Razorpay Order Information', {
            'fields': (
                'razorpay_order_id', 
                'entity', 
                'amount', 
                'amount_in_rupees', 
                'currency', 
                'receipt', 
                'status'
            )
        }),
        ('User Information', {
            'fields': ('user',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 
                'created_timestamp', 
                'updated_timestamp'
            ),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'created_timestamp'
    ordering = ['-created_timestamp']
    
    def user_username(self, obj):
        """Display username in list view"""
        return obj.user.username if obj.user else 'No User'
    user_username.short_description = 'Username'
    user_username.admin_order_field = 'user__username'
    
    def amount_in_rupees(self, obj):
        """Display amount in rupees with currency symbol"""
        return f"₹{obj.amount_in_rupees}"
    amount_in_rupees.short_description = 'Amount (₹)'
    
    def has_delete_permission(self, request, obj=None):
        """Restrict deletion of orders"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Optimize queries by selecting related user"""
        return super().get_queryset(request).select_related('user')
