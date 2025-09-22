from django.contrib import admin
from django.http import HttpResponse
import csv
from .models import SnaptradeUsers

class SnaptradeUsersAdmin(admin.ModelAdmin):
    list_display = ('user', 'userId', 'userSecret', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'userId')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['export_to_csv']
    
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="snaptrade_users.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'User ID', 'User Secret', 'Created At', 'Updated At'])
        
        for obj in queryset:
            writer.writerow([
                obj.user.username,
                obj.userId,
                obj.userSecret,
                obj.created_at,
                obj.updated_at
            ])
        
        return response
    
    export_to_csv.short_description = "Export selected items to CSV"

admin.site.register(SnaptradeUsers, SnaptradeUsersAdmin)
