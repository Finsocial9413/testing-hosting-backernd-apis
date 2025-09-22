from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fix invalid decimal data using raw SQL'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Update NULL or invalid decimal values to 0.00
                cursor.execute("""
                    UPDATE user_credits_usercredit 
                    SET current_credits = '0.00' 
                    WHERE current_credits IS NULL 
                    OR current_credits = '' 
                    OR current_credits = 'NULL'
                    OR LENGTH(current_credits) = 0
                """)
                
                cursor.execute("""
                    UPDATE user_credits_usercredit 
                    SET total_credits_purchased = '0.00' 
                    WHERE total_credits_purchased IS NULL 
                    OR total_credits_purchased = '' 
                    OR total_credits_purchased = 'NULL'
                    OR LENGTH(total_credits_purchased) = 0
                """)
                
                cursor.execute("""
                    UPDATE user_credits_usercredit 
                    SET total_credits_used = '0.00' 
                    WHERE total_credits_used IS NULL 
                    OR total_credits_used = '' 
                    OR total_credits_used = 'NULL'
                    OR LENGTH(total_credits_used) = 0
                """)
                
                # Try to fix any non-numeric values
                cursor.execute("""
                    UPDATE user_credits_usercredit 
                    SET current_credits = '0.00' 
                    WHERE current_credits NOT GLOB '[0-9]*.[0-9][0-9]'
                    AND current_credits NOT GLOB '[0-9]*'
                """)
                
                cursor.execute("""
                    UPDATE user_credits_usercredit 
                    SET total_credits_purchased = '0.00' 
                    WHERE total_credits_purchased NOT GLOB '[0-9]*.[0-9][0-9]'
                    AND total_credits_purchased NOT GLOB '[0-9]*'
                """)
                
                cursor.execute("""
                    UPDATE user_credits_usercredit 
                    SET total_credits_used = '0.00' 
                    WHERE total_credits_used NOT GLOB '[0-9]*.[0-9][0-9]'
                    AND total_credits_used NOT GLOB '[0-9]*'
                """)
                
                self.stdout.write(self.style.SUCCESS("Successfully fixed decimal data using SQL"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error fixing data: {e}"))