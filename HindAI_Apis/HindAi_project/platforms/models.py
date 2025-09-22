from django.db import models

from HindAi_users.models import HindAIUser
# Create your models here.

class AvailablePlatforms(models.Model):
    platform_name = models.CharField(max_length=100, unique=True)
    icon = models.URLField(max_length=300)
    access_link = models.URLField(max_length=300, blank=True, null=True)
    class Meta:
        verbose_name = "Available Platform"
        verbose_name_plural = "Available Platforms"
    
    def __str__(self):
        return self.platform_name

class UserConnect(models.Model):
    user = models.ForeignKey(HindAIUser, on_delete=models.CASCADE, related_name='platform_connections')
    platform = models.ForeignKey(AvailablePlatforms, on_delete=models.CASCADE, related_name='user_connections')
    api_key = models.CharField(max_length=500)
    model_name = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "User Platform Connection"
        verbose_name_plural = "User Platform Connections"
        unique_together = ['user', 'platform']  # Only one connection per user per platform
    
    def __str__(self):
        return f"{self.user.username} - {self.platform.platform_name} - {self.model_name}"

class PlatformModel(models.Model):
    platform = models.ForeignKey(AvailablePlatforms, on_delete=models.CASCADE, related_name='platform_model_links')
    model = models.CharField(max_length=200)
    support = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Platform Model Availability"
        verbose_name_plural = "Platform Model Availabilities"
        unique_together = ('platform', 'model')

    def __str__(self):
        return f"{self.platform.platform_name} -> {self.model}"


