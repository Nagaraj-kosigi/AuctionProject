from django.utils import timezone


class AuctionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from .models import Auction
        # Check for auctions that ended but still marked as active
        if request.user.is_authenticated:
            # Only check occasionally to avoid performance issues
            Auction.objects.filter(
                is_active=True,
                end_date__lt=timezone.now()
            ).update(is_active=False)
        
        response = self.get_response(request)
        return response