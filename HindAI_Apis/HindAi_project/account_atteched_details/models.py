from django.db import models
from HindAi_users.models import HindAIUser

# Create your models here.

class AccountAttachedDetail(models.Model):
    user = models.ForeignKey(HindAIUser, on_delete=models.CASCADE, related_name='attached_accounts')
    platform_name = models.CharField(max_length=1000, help_text="Name of the trading platform (e.g., TD Ameritrade, E*TRADE)")
    account_id = models.CharField(max_length=1000, help_text="Account ID from the platform")
    brokerage_authorization = models.CharField(max_length=1000, help_text="Brokerage authorization ID")
    is_active = models.BooleanField(default=True, help_text="Whether the account connection is active")
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform_name', 'account_id']
        verbose_name = "Account Attached Detail"
        verbose_name_plural = "Account Attached Details"
    
    def __str__(self):
        return f"{self.user.username} - {self.platform_name} ({self.account_id})"


