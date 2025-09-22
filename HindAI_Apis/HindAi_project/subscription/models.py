from django.db import models
from django.core.exceptions import ValidationError
from HindAi_users.models import HindAIUser

# Create your models here.

class SubscriptionPlan(models.Model):
    DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('12_months', '12 Months'),
    ]
    
    name = models.CharField(max_length=100, help_text="Name of the subscription plan")
    duration = models.CharField(
        max_length=20, 
        choices=DURATION_CHOICES,
        help_text="Duration of the subscription"
    )
    days = models.IntegerField(
        default=30, 
        help_text="Number of days for this subscription plan"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price of the subscription plan"
    )
    credits = models.IntegerField(
        default=0,
        help_text="Number of credits included in this plan"
    )
    features = models.TextField(
        blank=True,
        null=True,
        help_text="List of features included in this plan (one feature per line or comma separated)"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this plan is available for purchase")
    is_popular = models.BooleanField(default=False, help_text="Mark as popular plan for highlighting")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ['name', 'duration']
        # Remove any default permissions or constraints
        default_permissions = ('add', 'change', 'delete', 'view')
    
    def __str__(self):
        return f"{self.name} - {self.get_duration_display()} (${self.price})"
    
    def get_features_list(self):
        """Return features as a list"""
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return []
    
    def get_duration_in_days(self):
        """Convert duration to days for calculations"""
        duration_mapping = {
            '1_month': 30,
            '3_months': 90,
            '6_months': 180,
            '12_months': 365,
        }
        return duration_mapping.get(self.duration, self.days)  # Fallback to days field
    
    def save(self, *args, **kwargs):
        """Override save to ensure no restrictions"""
        # Remove any readonly restrictions
        if 'update_fields' in kwargs:
            kwargs.pop('update_fields', None)
        super().save(*args, **kwargs)


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(HindAIUser, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='user_subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the subscription expires"
    )
    credits_awarded = models.IntegerField(
        default=0,
        help_text="Credits awarded when this subscription was activated"
    )
    is_auto_renewal = models.BooleanField(default=False, help_text="Whether subscription auto-renews")
    payment_reference = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        help_text="Payment gateway reference/transaction ID"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"
        ordering = ['-created_at']
        # Remove any default permissions or constraints
        default_permissions = ('add', 'change', 'delete', 'view')
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active"""
        from django.utils import timezone
        return (
            self.status == 'active' and 
            self.end_date is not None and 
            self.end_date > timezone.now()
        )
    
    def days_remaining(self):
        """Calculate days remaining in subscription"""
        from django.utils import timezone
        
        # Return 0 if end_date is not set
        if self.end_date is None:
            return 0
            
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to ensure no restrictions"""
        # Remove any readonly restrictions
        if 'update_fields' in kwargs:
            kwargs.pop('update_fields', None)
        super().save(*args, **kwargs)
    
    def activate_subscription(self):
        """Activate the subscription and award credits - Simplified version"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Set subscription as active
        self.status = 'active'
        if not self.end_date:
            self.end_date = timezone.now() + timedelta(days=self.plan.get_duration_in_days())
        self.credits_awarded = self.plan.credits
        
        # Try to award credits to user (with error handling)
        try:
            from user_credits.models import UserCredit
            user_credit, created = UserCredit.objects.get_or_create(
                user=self.user,
                defaults={'username': self.user.username}
            )
            # Direct credit manipulation to avoid async issues
            user_credit.current_credits += self.plan.credits
            user_credit.total_credits_purchased += self.plan.credits
            user_credit.save()
        except Exception:
            # Skip credit awarding if any error occurs
            pass
        
        self.save()
        return True
