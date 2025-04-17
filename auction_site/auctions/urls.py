# urls.py (auctions app)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('auctions/<int:auction_id>/', views.auction_detail, name='auction_detail'),
    path('auctions/create/', views.create_auction, name='create_auction'),
    path('my-auctions/', views.my_auctions, name='my_auctions'),
    path('profile/', views.profile, name='profile'),
    path('auctions/<int:auction_id>/edit/', views.edit_auction, name='edit_auction'),
    path('auctions/<int:auction_id>/delete/', views.delete_auction, name='delete_auction'),

]