from django.contrib import admin
from django.forms import ModelForm
from decimal import Decimal, InvalidOperation
from .models import UserCredit

class UserCreditForm(ModelForm):
    class Meta:
        model = UserCredit
        fields = '__all__'
    
    def clean_current_credits(self):
        value = self.cleaned_data.get('current_credits')
        try:
            return Decimal(str(value)) if value is not None else Decimal('0.00')
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Invalid decimal value for current credits")
    
    def clean_total_credits_purchased(self):
        value = self.cleaned_data.get('total_credits_purchased')
        try:
            return Decimal(str(value)) if value is not None else Decimal('0.00')
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Invalid decimal value for total credits purchased")
    
    def clean_total_credits_used(self):
        value = self.cleaned_data.get('total_credits_used')
        try:
            return Decimal(str(value)) if value is not None else Decimal('0.00')
        except (InvalidOperation, ValueError):
            raise forms.ValidationError("Invalid decimal value for total credits used")

@admin.register(UserCredit)
class UserCreditAdmin(admin.ModelAdmin):
    form = UserCreditForm
    list_display = ('username', 'current_credits', 'total_credits_purchased', 'total_credits_used', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('username', 'user__email', 'user__first_name', 'user__last_name')
    list_editable = ('current_credits', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'total_credits_purchased', 'total_credits_used')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'username', 'is_active')
        }),
        ('Credit Information', {
            'fields': ('current_credits', 'total_credits_purchased', 'total_credits_used')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('user', 'username')
        return self.readonly_fields
