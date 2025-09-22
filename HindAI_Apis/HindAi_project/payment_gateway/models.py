from django.db import models
from django.db import models
from HindAi_users.models import HindAIUser

class RazorpayPaymentGateway(models.Model):
    # Razorpay order fields
    razorpay_order_id = models.CharField(max_length=100, unique=True, db_index=True)
    entity = models.CharField(max_length=50, default="order")
    amount = models.IntegerField()  # Amount in paise
    currency = models.CharField(max_length=10, default="INR")
    receipt = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default="created")
    created_at = models.IntegerField()  # Razorpay timestamp
    
    # Foreign key relationship with HindAIUser
    user = models.ForeignKey(
        HindAIUser, 
        on_delete=models.CASCADE, 
        related_name='razorpay_orders',
        null=True, 
        blank=True
    )
    notes = models.JSONField(default=dict, blank=True)
    
    # Django timestamps
    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'razorpay_payment_gateway'
        verbose_name = 'Razorpay Payment Gateway'
        verbose_name_plural = 'Razorpay Payment Gateways'
        ordering = ['-created_timestamp']
    
    def __str__(self):
        user_info = f" - {self.user.username}" if self.user else ""
        return f"Order {self.razorpay_order_id} - ₹{self.amount_in_rupees}{user_info}"
    
    @property
    def amount_in_rupees(self):
        """Convert amount from paise to rupees"""
        return self.amount / 100
