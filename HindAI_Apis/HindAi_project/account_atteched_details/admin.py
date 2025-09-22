from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from HindAi_users.models import HindAIUser as User

from .models import AccountAttachedDetail

# Inline admin for AccountAttachedDetail
class AccountAttachedDetailInline(admin.TabularInline):
    model = AccountAttachedDetail
    extra = 0
    readonly_fields = ['connected_at', 'updated_at']
    fields = ['platform_name', 'account_id', 'brokerage_authorization', 'is_active', 'connected_at', 'updated_at']

# Register your models here.
@admin.register(AccountAttachedDetail)
class AccountAttachedDetailAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform_name', 'account_id', 'brokerage_authorization', 'is_active', 'connected_at', 'updated_at']
    list_filter = ['platform_name', 'is_active', 'connected_at']
    search_fields = ['user__username', 'platform_name', 'account_id', 'brokerage_authorization']
    readonly_fields = ['connected_at', 'updated_at']
    list_editable = ['is_active']
    ordering = ['-connected_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'platform_name', 'account_id', 'brokerage_authorization')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('connected_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Extend the User admin to include AccountAttachedDetail inline
class CustomUserAdmin(UserAdmin):
    inlines = [AccountAttachedDetailInline]

# Unregister the default User admin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
