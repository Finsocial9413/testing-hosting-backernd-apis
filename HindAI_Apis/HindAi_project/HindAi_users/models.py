from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class HindAIUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        app_label = 'HindAi_users'
        
# New model for user profiles with social media handles
class UserProfile(models.Model):
    user = models.OneToOneField(HindAIUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(max_length=500, null=True, blank=True)
    
    # Social media handles
    twitter_handle = models.CharField(max_length=50, null=True, blank=True)
    facebook_handle = models.CharField(max_length=50, null=True, blank=True)
    linkedin_handle = models.CharField(max_length=50, null=True, blank=True)
    instagram_handle = models.CharField(max_length=50, null=True, blank=True)
    github_handle = models.CharField(max_length=50, null=True, blank=True)
    
    # Additional profile information
    location = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
        
# New model for active/inactive user timings
class ActiveInactiveUsers(models.Model):
    minute = models.IntegerField(null=True, blank=True)  # integer field for hour input
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    user = models.ForeignKey(HindAIUser, on_delete=models.CASCADE, related_name="active_status")
    
    def __str__(self):
        return f"{self.user.email} active from {self.start_time} to {self.end_time}"
