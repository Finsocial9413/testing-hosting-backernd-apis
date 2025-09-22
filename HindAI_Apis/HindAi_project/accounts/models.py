from django.db import models


from HindAi_users.models import HindAIUser 

# Create your models here.

class SnaptradeUsers(models.Model):
    user = models.OneToOneField(HindAIUser, on_delete=models.CASCADE, related_name='snaptrade_user')
    userId = models.CharField(max_length=100, unique=True)
    userSecret = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Snaptrade User'
        verbose_name_plural = 'Snaptrade Users'
    
    def __str__(self):
        return f"{self.user.username} - {self.userId}"
