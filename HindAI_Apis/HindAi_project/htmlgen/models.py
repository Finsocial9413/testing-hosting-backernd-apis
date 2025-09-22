from django.db import models
from HindAi_users.models import HindAIUser

# Create your models here.
class HtmlGeneration(models.Model):
    user = models.ForeignKey(HindAIUser, on_delete=models.CASCADE, related_name='html_generations')
    prompt = models.TextField(help_text="user prompt")
    answer = models.TextField(help_text="The prompt answer")
    html = models.TextField(help_text="The generated HTML code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"HTML for {self.user.username}: {self.prompt[:30]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'HTML Generation'
        verbose_name_plural = 'HTML Generations'
