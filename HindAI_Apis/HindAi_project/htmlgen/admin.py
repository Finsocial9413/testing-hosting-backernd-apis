from django.contrib import admin
from .models import HtmlGeneration

@admin.register(HtmlGeneration)
class HtmlGenerationAdmin(admin.ModelAdmin):
    list_display = ('user', 'prompt', 'answer','created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'prompt')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')