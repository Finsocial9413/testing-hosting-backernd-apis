from django.db import models

# Create your models here.

class AIModel(models.Model):
    model_name = models.CharField(max_length=100, unique=True, help_text="Name of the AI model")
    backend_model_name = models.CharField(max_length=100, help_text="Backend identifier for the model")
    input_price_per_token = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        help_text="Price per input token in USD"
    )
    output_price_per_token = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        help_text="Price per output token in USD"
    )
    provider = models.CharField(max_length=50, blank=True, help_text="Model provider (e.g., OpenAI, Anthropic)")
    is_active = models.BooleanField(default=True, help_text="Whether the model is currently available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        ordering = ['model_name']
    
    def __str__(self):
        return f"{self.model_name} - Input: ${self.input_price_per_token}/token, Output: ${self.output_price_per_token}/token"
