from django.contrib import admin
from .models import AIModel

# Register your models here.

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'backend_model_name','provider', 'input_price_per_token', 'output_price_per_token', 'is_active', 'created_at')
    list_filter = ('provider', 'is_active', 'created_at')
    search_fields = ('model_name', 'provider')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Model Information', {
            'fields': ('model_name', 'backend_model_name', 'provider', 'is_active')
        }),
        ('Pricing', {
            'fields': ('input_price_per_token', 'output_price_per_token')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
