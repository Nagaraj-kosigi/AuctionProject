from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def get_default_end_date():
    return timezone.now() + timedelta(days=7)

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Auction(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='auction_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='auctions')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='won_auctions', null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=get_default_end_date)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.current_price:
            self.current_price = self.starting_price
        super().save(*args, **kwargs)
    
    @property
    def time_remaining(self):
        if self.end_date > timezone.now():
            return self.end_date - timezone.now()
        return timedelta(0)
    
    @property
    def has_ended(self):
        return self.end_date < timezone.now()

class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.auction.title}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"