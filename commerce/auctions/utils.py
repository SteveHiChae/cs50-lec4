from .models import *
from django.http import HttpResponse, HttpResponseRedirect

def get_watchlist_count(request):
    listing = Listing.objects.filter(active_listing="YES")    
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        watchlist_count = Watchlist.objects.filter(watcher=user.id).count()
    else:
        watchlist_count = 0

    return str(watchlist_count)

def highest_bid(listing_id):
    listing = Listing.objects.get(pk=listing_id)
    highest_bid = Bid.objects.filter(item=listing).order_by('-price').first()
    return highest_bid

def bid_info(listing_id):
    listing = Listing.objects.get(pk=listing_id)

    number_of_bids = Bid.objects.filter(item=listing).count()
    if number_of_bids == 0:
        highest_bid = listing.starting_bid
        bid_price = highest_bid + decimal.Decimal('0.1')
        current_bidder = ""
    else:
        highest_bid = Bid.objects.filter(item=listing).order_by('-price').first()
        bid_price = highest_bid.price + decimal.Decimal('0.1')

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)

        if number_of_bids > 1:
            if highest_bid.bidder == request.user.username:
                current_bidder = 'Current bid is your.'
            else:
                current_bidder = "You've been outbid by " + highest_bid.bidder.username

        bid_info = {
            "listing": listing,
            "number_of_bids": number_of_bids,
            "highest_bid": highest_bid,
            "bid_price": bid_price,
            "current_bidder": current_bidder
        }

    else:
        watchlist_count = 0

        bid_info = {
            "listing": listing,
            "bid_price": bid_price
        }
    
    return bid_info

# def add_watchlist(listing_id):

# def close(listing_id):

# def add_comment(listing_id):

def bidding(listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)

    if request.method == "POST":
        if 'placebid' in request.POST:
            highest_bid = Bid.objects.filter(item=listing).values('price').order_by('-price').first()
            bid = request.POST['bid']
            if bid < highest_bid: 
                message = "Please enter more then ..." 
            else:
                # bid = Bid.objects.create(price=bid_price, bidder=user, item=listing)
                bid = Bid(price=bid_price, bidder=user, item=listing)
                bid.save()
                message = "Successfully updated bidding!"

        elif 'add-watchlist' in request.POST:
            listing.watchlist = "YES"
            listing.save()
            # user = User.objects.get(pk=request.user.id)
            w = Watchlist(watcher=user, item=listing)
            w.save()
            message = "Successfully added to watch list!"

        elif 'remove-watchlist' in request.POST:
            listing.watchlist = "NO"
            listing.save()
            # user = User.objects.get(pk=request.user.id)
            w = Watchlist.objects.filter(watcher=user, item=listing).delete()
            message = "Delete the watch list!"


    return render(request, "auctions/listing_page.html", {
        "listing": listing,
        "message": message
    })