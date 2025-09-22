from django.db import models
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

from HindAi_users.models import HindAIUser

class UserCredit(models.Model):
    user = models.OneToOneField(HindAIUser, on_delete=models.CASCADE, related_name='credit_account')
    username = models.CharField(max_length=150, unique=True, help_text="Username for credit tracking")
    current_credits = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Current available credits for the user"
    )
    total_credits_purchased = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Total credits ever purchased by user"
    )
    total_credits_used = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Total credits used by user"
    )
    is_active = models.BooleanField(default=True, help_text="Whether the user account is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Credit"
        verbose_name_plural = "User Credits"
        ordering = ['-updated_at']
    
    def clean(self):
        """Validate decimal fields"""
        try:
            if self.current_credits is not None:
                self.current_credits = Decimal(str(self.current_credits))
            if self.total_credits_purchased is not None:
                self.total_credits_purchased = Decimal(str(self.total_credits_purchased))
            if self.total_credits_used is not None:
                self.total_credits_used = Decimal(str(self.total_credits_used))
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid decimal value: {e}")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.username} - Credits: {self.current_credits}"
    
    def add_credits(self, amount):
        """Add credits to user account"""
        try:
            amount = Decimal(str(amount))
            self.current_credits = (self.current_credits or Decimal('0.00')) + amount
            self.total_credits_purchased = (self.total_credits_purchased or Decimal('0.00')) + amount
            self.save()
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid amount: {e}")
    
    def deduct_credits(self, amount):
        """Deduct credits from user account"""
        try:
            amount = Decimal(str(amount))
            current = self.current_credits or Decimal('0.00')
            if current >= amount:
                self.current_credits = current - amount
                self.total_credits_used = (self.total_credits_used or Decimal('0.00')) + amount
                self.save()
                return True
            return False
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Invalid amount: {e}")
