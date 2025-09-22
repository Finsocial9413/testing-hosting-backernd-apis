from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import AvailablePlatforms, UserConnect, PlatformModel

# Register your models here.




class PlatformModelInline(admin.TabularInline):
    model = PlatformModel
    extra = 1
    fields = ('model', 'is_active')
    show_change_link = True



@admin.register(AvailablePlatforms)
class AvailablePlatformsAdmin(ImportExportModelAdmin):
    list_display = ('platform_name', 'access_link')
    search_fields = ('platform_name',)
    list_filter = ('platform_name',)
    ordering = ('platform_name',)


@admin.register(UserConnect)
class UserConnectAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'model_name', 'is_active', 'created_at')
    search_fields = ('user__username', 'platform__platform_name', 'model_name')
    list_filter = ('platform', 'is_active', 'created_at')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Connection Details', {
            'fields': ('user', 'platform', 'model_name')
        }),
        ('API Configuration', {
            'fields': ('api_key', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    
@admin.register(PlatformModel)
class PlatformModelAdmin(admin.ModelAdmin):
    list_display = ('platform', 'model', 'is_active', 'added_at')
    list_filter = ('platform', 'is_active', 'added_at')
    search_fields = ('platform__platform_name', 'model')
    ordering = ('platform', 'model')
    list_editable = ('is_active',)
    readonly_fields = ('added_at',)