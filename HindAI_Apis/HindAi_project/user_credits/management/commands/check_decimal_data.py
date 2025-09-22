from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check raw decimal data in UserCredit table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, current_credits, total_credits_purchased, total_credits_used FROM user_credits_usercredit")
            rows = cursor.fetchall()
            
            self.stdout.write("Raw data from database:")
            for row in rows:
                self.stdout.write(f"ID: {row[0]}, Username: {row[1]}, Current: {row[2]}, Purchased: {row[3]}, Used: {row[4]}")