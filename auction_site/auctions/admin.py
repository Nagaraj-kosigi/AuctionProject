# admin.py
from django.contrib import admin
from .models import Auction, Bid, Category, UserProfile

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'current_price', 'created_by', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'category', 'start_date')
    search_fields = ('title', 'description')
    inlines = [BidInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'amount', 'bid_time')
    list_filter = ('bid_time',)
    search_fields = ('auction__title', 'bidder__username')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')