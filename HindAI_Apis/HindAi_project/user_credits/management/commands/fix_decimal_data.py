from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal, InvalidOperation
from user_credits.models import UserCredit

class Command(BaseCommand):
    help = 'Fix invalid decimal data in UserCredit model'

    def handle(self, *args, **options):
        with transaction.atomic():
            for credit in UserCredit.objects.all():
                try:
                    # Validate and fix current_credits
                    if credit.current_credits is None:
                        credit.current_credits = Decimal('0.00')
                    
                    # Validate and fix total_credits_purchased
                    if credit.total_credits_purchased is None:
                        credit.total_credits_purchased = Decimal('0.00')
                    
                    # Validate and fix total_credits_used
                    if credit.total_credits_used is None:
                        credit.total_credits_used = Decimal('0.00')
                    
                    credit.save()
                    self.stdout.write(f"Fixed credit data for user: {credit.username}")
                    
                except (InvalidOperation, ValueError) as e:
                    self.stdout.write(f"Error fixing user {credit.username}: {e}")