from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Recreate UserCredit table with clean decimal data'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # Backup existing data (only valid entries)
                cursor.execute("""
                    CREATE TEMPORARY TABLE temp_credits AS
                    SELECT id, user_id, username, is_active, created_at, updated_at
                    FROM user_credits_usercredit
                """)
                
                # Drop and recreate the table
                cursor.execute("DROP TABLE user_credits_usercredit")
                
                cursor.execute("""
                    CREATE TABLE user_credits_usercredit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL REFERENCES HindAi_users_hindaiuser(id),
                        username VARCHAR(150) UNIQUE NOT NULL,
                        current_credits DECIMAL(10,2) DEFAULT '0.00',
                        total_credits_purchased DECIMAL(10,2) DEFAULT '0.00',
                        total_credits_used DECIMAL(10,2) DEFAULT '0.00',
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """)
                
                # Restore data with default decimal values
                cursor.execute("""
                    INSERT INTO user_credits_usercredit 
                    (id, user_id, username, current_credits, total_credits_purchased, total_credits_used, is_active, created_at, updated_at)
                    SELECT id, user_id, username, '0.00', '0.00', '0.00', is_active, created_at, updated_at
                    FROM temp_credits
                """)
                
                cursor.execute("DROP TABLE temp_credits")
                
                self.stdout.write(self.style.SUCCESS("Successfully recreated UserCredit table"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error recreating table: {e}"))