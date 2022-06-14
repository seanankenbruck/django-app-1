"""
Command to make app wait for database
"""
import time

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""
    def handle(self, *args, **options):
        """Standard function for commands"""
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                time.sleep(3)
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Datbase unavailable, waiting 1 seconds...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
