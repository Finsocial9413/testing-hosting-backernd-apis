from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import HindAIUser, ActiveInactiveUsers, UserProfile

@admin.register(ActiveInactiveUsers)
class ActiveInactiveUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'minute', 'start_time', 'end_time')
    list_filter = ('minute',)
    search_fields = ('user__email', 'user__username')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'location')
    search_fields = ('user__email', 'user__username', 'phone_number', 'location')
    list_filter = ('location',)
    readonly_fields = ('user',)
    
    fieldsets = (
        ('User Information', {'fields': ('user',)}),
        ('Contact Information', {'fields': ('phone_number', 'location', 'website')}),
        ('Profile', {'fields': ('profile_picture', 'bio')}),
        ('Social Media', {'fields': ('twitter_handle', 'facebook_handle', 
                                    'linkedin_handle', 'instagram_handle', 'github_handle')})
    )

@admin.register(HindAIUser)
class HindAIUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    # Add custom fields to fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
