from django.core.management.base import BaseCommand
from django.utils import timezone
from auctions.models import Auction
from auctions.views import end_expired_auctions

class Command(BaseCommand):
    help = 'End auctions that have passed their end date'

    def handle(self, *args, **options):
        count = end_expired_auctions()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully ended {count} expired auctions')
        )