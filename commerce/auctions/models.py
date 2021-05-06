from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    CATEGORY = [
        ("COLTBLE", "Collectible & art"),
        ("ELECTRO", "Electronics"),
        ("FASHION", "Fashion"),
        ("HOME", "Home & garden"),
        ("MUSIC", "Musical Instruments & gear"),
        ("TOY", "Toys & hobbies")
    ] 
    category = models.CharField(null=True, blank=True, max_length=10, choices=CATEGORY, default="TOY")
    description = models.CharField(null=True, blank=True, max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=1)
    photo = models.ImageField(null=True, blank=True, upload_to='images/')
    YES_NO = [ ("YES", "Yes"), ("NO", "No") ]
    active_listing = models.CharField(max_length=3, choices=YES_NO, default="YES")
    listed_by = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user" )
    listing_datetime = models.DateTimeField(auto_now_add=True, blank=True)
    watchlist = models.CharField(max_length=3, choices=YES_NO, default="NO")
    starting_bid = models.DecimalField(max_digits=7, decimal_places=1, default=1.0)

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bidding_item")
    price = models.DecimalField(max_digits=7, decimal_places=1)
    bidding_datetime = models.DateTimeField(auto_now_add=True, blank=False)

class Comment(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment_item")
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

class Watchlist(models.Model):
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist_item")