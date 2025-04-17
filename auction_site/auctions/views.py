# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.utils import timezone
from django.db.models import Max, Count, Q
from django.core.paginator import Paginator
from .models import Auction, Bid, Category, UserProfile
from .forms import AuctionForm, BidForm, UserProfileForm
from django.core.management.base import BaseCommand
from auctions.models import Auction

from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, f"Account created for {username}! You are now logged in.")
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def user_logout(request):
    auth_logout(request)
    return redirect('index')

def index(request):
    categories = Category.objects.all()
    
    category_id = request.GET.get('category')
    search_query = request.GET.get('search')
    
    auctions = Auction.objects.filter(is_active=True, end_date__gt=timezone.now())
    
    if category_id:
        auctions = auctions.filter(category_id=category_id)
    
    if search_query:
        auctions = auctions.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    auctions = auctions.annotate(bid_count=Count('bids'))
    
    # Sorting
    sort_by = request.GET.get('sort', 'end_date')
    if sort_by == 'end_date':
        auctions = auctions.order_by('end_date')
    elif sort_by == 'price_low':
        auctions = auctions.order_by('current_price')
    elif sort_by == 'price_high':
        auctions = auctions.order_by('-current_price')
    elif sort_by == 'newest':
        auctions = auctions.order_by('-start_date')
    
    paginator = Paginator(auctions, 12)  # Show 12 auctions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'auctions/index.html', {
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'sort_by': sort_by
    })

def auction_detail(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    bids = auction.bids.order_by('-bid_time')[:10]
    bid_form = BidForm(auction=auction, user=request.user if request.user.is_authenticated else None)
    
    if request.method == 'POST' and request.user.is_authenticated:
        bid_form = BidForm(request.POST, auction=auction, user=request.user)
        if bid_form.is_valid():
            bid = bid_form.save(commit=False)
            bid.auction = auction
            bid.bidder = request.user
            bid.save()
            
            # Update auction current price
            auction.current_price = bid.amount
            auction.save()
            
            messages.success(request, "Your bid has been placed successfully!")
            return redirect('auction_detail', auction_id=auction.id)
    
    # Check if auction has ended but winner not determined yet
    if auction.has_ended and auction.is_active:
        highest_bid = auction.bids.order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder
            auction.is_active = False
            auction.save()
    
    return render(request, 'auctions/auction_detail.html', {
        'auction': auction,
        'bids': bids,
        'bid_form': bid_form,
    })

@login_required
def create_auction(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.created_by = request.user
            auction.current_price = auction.starting_price
            auction.save()
            messages.success(request, "Your auction has been created successfully!")
            return redirect('auction_detail', auction_id=auction.id)
    else:
        form = AuctionForm()
    
    return render(request, 'auctions/create_auction.html', {
        'form': form,
    })

@login_required
def my_auctions(request):
    user_auctions = Auction.objects.filter(created_by=request.user).order_by('-start_date')
    won_auctions = Auction.objects.filter(winner=request.user, is_active=False)
    active_bids = Bid.objects.filter(
        bidder=request.user, 
        auction__is_active=True
    ).values('auction').annotate(
        max_bid=Max('amount')
    ).order_by('-max_bid')
    
    active_bid_auctions = []
    for bid in active_bids:
        auction = Auction.objects.get(pk=bid['auction'])
        is_highest = auction.current_price == bid['max_bid']
        active_bid_auctions.append({
            'auction': auction,
            'max_bid': bid['max_bid'],
            'is_highest': is_highest
        })
    
    return render(request, 'auctions/my_auctions.html', {
        'user_auctions': user_auctions,
        'won_auctions': won_auctions,
        'active_bid_auctions': active_bid_auctions
    })

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)
        profile.save()
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'auctions/profile.html', {
        'form': form,
        'profile': profile
    })

def end_expired_auctions():
    """End auctions that have passed their end date"""
    expired_auctions = Auction.objects.filter(
        is_active=True,
        end_date__lt=timezone.now()
    )
    
    for auction in expired_auctions:
        highest_bid = auction.bids.order_by('-amount').first()
        if highest_bid:
            auction.winner = highest_bid.bidder
        auction.is_active = False
        auction.save()
    
    return len(expired_auctions)

@login_required
def edit_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id, created_by=request.user)

    if not auction.is_active:
        return HttpResponseForbidden("You can't edit an inactive or ended auction.")

    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES, instance=auction)
        if form.is_valid():
            form.save()
            messages.success(request, "Auction updated successfully.")
            return redirect('my_auctions')
    else:
        form = AuctionForm(instance=auction)

    return render(request, 'auctions/edit_auction.html', {'form': form, 'auction': auction})

@require_POST
@login_required
def delete_auction(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id, created_by=request.user)

    if auction.is_active and not auction.has_ended:
        auction.delete()
        messages.success(request, "Auction cancelled successfully.")
    else:
        messages.error(request, "Cannot cancel an ended or inactive auction.")

    return redirect('my_auctions')