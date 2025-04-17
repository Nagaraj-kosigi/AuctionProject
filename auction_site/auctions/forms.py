from django import forms
from .models import Auction, Bid, UserProfile

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['title', 'description', 'starting_price', 'image', 'category', 'end_date']
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
        
    def __init__(self, *args, auction=None, user=None, **kwargs):
        self.auction = auction
        self.user = user
        super().__init__(*args, **kwargs)
        
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= self.auction.current_price:
            raise forms.ValidationError("Your bid must be higher than the current price.")
        return amount

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']