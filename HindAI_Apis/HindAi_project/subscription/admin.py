from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils import timezone
import csv
import json
from .models import SubscriptionPlan, UserSubscription

# Custom form for SubscriptionPlan with validation
class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        duration = cleaned_data.get('duration')
        
        if name and duration:
            # Check for duplicates
            existing_plan = SubscriptionPlan.objects.filter(
                name=name, 
                duration=duration
            )
            
            # If this is an update, exclude the current instance
            if self.instance.pk:
                existing_plan = existing_plan.exclude(pk=self.instance.pk)
            
            if existing_plan.exists():
                raise ValidationError(f"A {name} plan with {dict(SubscriptionPlan.DURATION_CHOICES)[duration]} duration already exists.")
        
        return cleaned_data

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    form = SubscriptionPlanForm
    
    list_display = [
        'name', 
        'duration', 
        'days',  # Added days field
        'price', 
        'credits', 
        'is_active', 
        'is_popular',
        'created_at'
    ]
    list_filter = [
        'duration', 
        'days',  # Added days filter
        'is_active', 
        'is_popular',
        'created_at'
    ]
    search_fields = ['name', 'features']
    list_editable = ['is_active', 'is_popular', 'price', 'days']  # Added days to editable fields
    ordering = ['name', 'duration']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'duration', 'days')  # Added days field
        }),
        ('Pricing & Credits', {
            'fields': ('price', 'credits')
        }),
        ('Features & Status', {
            'fields': ('features', 'is_active', 'is_popular')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_as_csv', 'export_as_json']
    
    def export_as_csv(self, request, queryset):
        """Export selected subscription plans as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="subscription_plans_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'Name', 'Duration', 'Days', 'Price', 'Credits', 'Features', 
            'Is Active', 'Is Popular', 'Created At', 'Updated At'
        ])
        
        # Write data
        for plan in queryset:
            writer.writerow([
                plan.id,
                plan.name,
                plan.get_duration_display(),
                plan.days,  # Added days field
                plan.price,
                plan.credits,
                plan.features.replace('\n', ' | '),  # Replace newlines with separator
                'Yes' if plan.is_active else 'No',
                'Yes' if plan.is_popular else 'No',
                plan.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                plan.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_as_csv.short_description = "Export selected plans as CSV"
    
    def export_as_json(self, request, queryset):
        """Export selected subscription plans as JSON"""
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="subscription_plans_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        data = []
        for plan in queryset:
            data.append({
                'id': plan.id,
                'name': plan.name,
                'duration': plan.duration,
                'duration_display': plan.get_duration_display(),
                'days': plan.days,  # Added days field
                'price': str(plan.price),
                'credits': plan.credits,
                'features': plan.get_features_list(),
                'is_active': plan.is_active,
                'is_popular': plan.is_popular,
                'created_at': plan.created_at.isoformat(),
                'updated_at': plan.updated_at.isoformat(),
            })
        
        response.write(json.dumps(data, indent=2))
        return response
    export_as_json.short_description = "Export selected plans as JSON"


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'plan_name', 
        'plan_days',  # Added plan days display
        'status', 
        'start_date', 
        'end_date',
        'credits_awarded',
        'is_auto_renewal',
        'days_remaining_display'
    ]
    list_filter = [
        'status', 
        'is_auto_renewal', 
        'plan__duration',
        'plan__days',  # Added plan days filter
        'start_date',
        'end_date'
    ]
    search_fields = [
        'user__email', 
        'user__username', 
        'plan__name',
        'payment_reference'
    ]
    list_editable = ['status', 'is_auto_renewal']
    ordering = ['-created_at']
    readonly_fields = ['start_date', 'created_at', 'updated_at', 'days_remaining_display']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('user', 'plan', 'status')
        }),
        ('Dates & Duration', {
            'fields': ('start_date', 'end_date', 'days_remaining_display')
        }),
        ('Credits & Payment', {
            'fields': ('credits_awarded', 'payment_reference')
        }),
        ('Settings', {
            'fields': ('is_auto_renewal',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email in list view"""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def plan_name(self, obj):
        """Display plan name in list view"""
        return obj.plan.name
    plan_name.short_description = 'Plan'
    plan_name.admin_order_field = 'plan__name'
    
    def plan_days(self, obj):
        """Display plan days in list view"""
        return f"{obj.plan.days} days"
    plan_days.short_description = 'Plan Duration (Days)'
    plan_days.admin_order_field = 'plan__days'
    
    def days_remaining_display(self, obj):
        """Display days remaining in admin"""
        days = obj.days_remaining()
        if days > 0:
            return f"{days} days"
        elif obj.status == 'active':
            return "Expired"
        else:
            return "N/A"
    days_remaining_display.short_description = 'Days Remaining'
    
    actions = ['activate_subscriptions', 'cancel_subscriptions', 'export_as_csv', 'export_as_json', 'export_detailed_report']
    
    def activate_subscriptions(self, request, queryset):
        """Admin action to activate selected subscriptions"""
        activated_count = 0
        for subscription in queryset.filter(status='pending'):
            try:
                subscription.activate_subscription()
                activated_count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error activating subscription for {subscription.user.email}: {str(e)}", 
                    level='ERROR'
                )
        
        if activated_count > 0:
            self.message_user(
                request, 
                f"Successfully activated {activated_count} subscription(s).", 
                level='SUCCESS'
            )
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def cancel_subscriptions(self, request, queryset):
        """Admin action to cancel selected subscriptions"""
        cancelled_count = queryset.filter(status__in=['active', 'pending']).update(status='cancelled')
        if cancelled_count > 0:
            self.message_user(
                request, 
                f"Successfully cancelled {cancelled_count} subscription(s).", 
                level='SUCCESS'
            )
    cancel_subscriptions.short_description = "Cancel selected subscriptions"
    
    def export_as_csv(self, request, queryset):
        """Export selected user subscriptions as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="user_subscriptions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID', 'User Email', 'User Username', 'Plan Name', 'Plan Duration', 'Plan Days',
            'Status', 'Start Date', 'End Date', 'Credits Awarded', 'Auto Renewal',
            'Payment Reference', 'Days Remaining', 'Created At', 'Updated At'
        ])
        
        # Write data
        for subscription in queryset:
            writer.writerow([
                subscription.id,
                subscription.user.email,
                subscription.user.username,
                subscription.plan.name,
                subscription.plan.get_duration_display(),
                subscription.plan.days,  # Added plan days
                subscription.get_status_display(),
                subscription.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.end_date.strftime('%Y-%m-%d %H:%M:%S') if subscription.end_date else 'Not Set',
                subscription.credits_awarded,
                'Yes' if subscription.is_auto_renewal else 'No',
                subscription.payment_reference or 'N/A',
                subscription.days_remaining(),
                subscription.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_as_csv.short_description = "Export selected subscriptions as CSV"
    
    def export_as_json(self, request, queryset):
        """Export selected user subscriptions as JSON"""
        response = HttpResponse(content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="user_subscriptions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.json"'
        
        data = []
        for subscription in queryset:
            data.append({
                'id': subscription.id,
                'user': {
                    'email': subscription.user.email,
                    'username': subscription.user.username,
                },
                'plan': {
                    'name': subscription.plan.name,
                    'duration': subscription.plan.duration,
                    'duration_display': subscription.plan.get_duration_display(),
                    'days': subscription.plan.days,  # Added plan days
                    'price': str(subscription.plan.price),
                    'credits': subscription.plan.credits,
                },
                'status': subscription.status,
                'status_display': subscription.get_status_display(),
                'start_date': subscription.start_date.isoformat(),
                'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
                'credits_awarded': subscription.credits_awarded,
                'is_auto_renewal': subscription.is_auto_renewal,
                'payment_reference': subscription.payment_reference,
                'days_remaining': subscription.days_remaining(),
                'created_at': subscription.created_at.isoformat(),
                'updated_at': subscription.updated_at.isoformat(),
            })
        
        response.write(json.dumps(data, indent=2))
        return response
    export_as_json.short_description = "Export selected subscriptions as JSON"
    
    def export_detailed_report(self, request, queryset):
        """Export detailed subscription report with analytics"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="subscription_detailed_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header with additional analytics columns
        writer.writerow([
            'ID', 'User Email', 'User Username', 'Plan Name', 'Plan Duration', 'Plan Days', 'Plan Price',
            'Status', 'Start Date', 'End Date', 'Days Active', 'Days Remaining', 
            'Credits Awarded', 'Auto Renewal', 'Payment Reference', 'Is Active Now',
            'Revenue Generated', 'Plan Features', 'Created At', 'Updated At'
        ])
        
        # Write data with additional calculations
        for subscription in queryset:
            days_active = (timezone.now().date() - subscription.start_date.date()).days if subscription.start_date else 0
            revenue = subscription.plan.price if subscription.status in ['active', 'expired'] else 0
            
            writer.writerow([
                subscription.id,
                subscription.user.email,
                subscription.user.username,
                subscription.plan.name,
                subscription.plan.get_duration_display(),
                subscription.plan.days,  # Added plan days
                subscription.plan.price,
                subscription.get_status_display(),
                subscription.start_date.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.end_date.strftime('%Y-%m-%d %H:%M:%S') if subscription.end_date else 'Not Set',
                days_active,
                subscription.days_remaining(),
                subscription.credits_awarded,
                'Yes' if subscription.is_auto_renewal else 'No',
                subscription.payment_reference or 'N/A',
                'Yes' if subscription.is_active() else 'No',
                revenue,
                ' | '.join(subscription.plan.get_features_list()),
                subscription.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                subscription.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    export_detailed_report.short_description = "Export detailed analytics report"
