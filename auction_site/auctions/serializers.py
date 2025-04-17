# serializers.py (for API if needed)
from rest_framework import serializers
from .models import Auction, Bid, Category, UserProfile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BidSerializer(serializers.ModelSerializer):
    bidder_name = serializers.ReadOnlyField(source='bidder.username')
    
    class Meta:
        model = Bid
        fields = ['id', 'amount', 'bid_time', 'bidder_name']

class AuctionSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    created_by_name = serializers.ReadOnlyField(source='created_by.username')
    bids = BidSerializer(many=True, read_only=True)
    
    class Meta:
        model = Auction
        fields = [
            'id', 'title', 'description', 'starting_price', 'current_price',
            'image', 'category', 'category_name', 'created_by', 'created_by_name',
            'winner', 'start_date', 'end_date', 'is_active', 'bids'
        ]