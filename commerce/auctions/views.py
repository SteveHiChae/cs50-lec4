from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from decimal import Decimal 
from django.db.models import Count

from .models import *
from .forms import *
from . import utils

def index(request):
    listings = Listing.objects.filter(active_listing="YES")

    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlist_count": utils.get_watchlist_count(request) 
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def categories(request):
    categories = Listing.CATEGORY
    # [('COLTBLE', 'Collectible & art'), ('ELECTRO', 'Electronics'), ('FASHION', 'Fashion'), 
    #  ('HOME', 'Home & garden'), ('MUSIC', 'Musical Instruments & gear'), ('TOY', 'Toys & hobbies')]

    count = Listing.objects.values('category').annotate( Count('category' ) ).exclude(active_listing="NO")
    cnt_by_category = [ (cat['category'], cat['category__count']) for cat in count ]
    # [('ELECTRO', 4), ('MUSIC', 1), ('TOY', 2)]


    # Let's count All categories. 
    # [('COLTBLE', 'Collectible & art', 0), ('ELECTRO', 'Electronics', 4), ('FASHION', 'Fashion', 0), ... 
    ######################################
    # This one is not working, because of re using categories???
    # version 1
    ######################################
    # cats = []
    # for cat in cnt_by_category:
    #     cats += [ ( v[0], v[1], cat[1] ) for i, v in enumerate(categories) if v[0] == cat[0] ] 

    # for cat in cnt_by_category:
        # newlist = [x if x != "banana" else "orange" for x in fruits] 
        # l = next(( i for i, v in enumerate(categories) if v[0] == cat[0]), -1)
        # if l > 0: 
            # categories[l] += (cat[1],)  # cause error later in listing_page
            # cats += [( cat[0], categories[l][1], cat[1], )]  # cause error later in listing_page

    # version 2
    # This one also cause Error...
    # for cat in enumerate(cnt_by_category):
        # v = next(( v for v in enumerate(categories) if v[0] != cat[0]), None)
        # if v is not None:
            # cats += [(v[0], v[1], 0, )] # something wrong...
            
    # Make a NEW list of Category NOT reusing the categories variable
    # temporary solution.

    ######################################
    # version 3
    # cats = []
    # found = "No"
    # for i, cat in enumerate(categories):
    #     for c in cnt_by_category:
    #         if c[0] == cat[0]:
    #             cats += [( cat[0], cat[1], c[1], )]
    #             found = "Yes"
    #     if found != "Yes":
    #         cats += [( cat[0], cat[1], 0,  )]
    #         foud = "No"
    ######################################

    # version 4
    # cats = []
    # for cat in categories:
    #     cats += [ (cat[0], cat[1], v[1]) for v in cnt_by_category if v[0] == cat[0] ]

    # for cat in categories:
    #     l = next( (i for i,v in enumerate(cnt_by_category) if v[0] == cat[0]), -1 )
    #     if l == -1:
    #         cats += [ (cat[0], cat[1], 0 ) ]
    # WORKING. But....

    # Final version!
    cats = []
    for cat in categories:
        cats += [ (cat[0], cat[1], v[1]) for v in cnt_by_category if v[0] == cat[0] ]
        if not cat[0] in dict(cnt_by_category):
            cats += [ (cat[0], cat[1], 0 ) ]
    # Is it possible to get the all category sum from db level not python???
    
    return render(request, "auctions/category_page.html", {
        # "categories": categories
        "categories": cats,
        "watchlist_count": utils.get_watchlist_count(request)
    })

def listing_by_category(request, category):
    listings = Listing.objects.filter(category=category).exclude(active_listing="NO")
    return render(request, 'auctions/index.html', {
        'listings': listings,
        'watchlist_count': utils.get_watchlist_count(request)
    })

@login_required()
def watchlist(request):
    watchlists = Watchlist.objects.filter(watcher=request.user.id).all()
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlists,
        "watchlist_count": utils.get_watchlist_count(request)
    }) 

@login_required()
def create_listing(request):

    if not request.user.is_authenticated: 
        message = "Invalid credentials"
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        listing_form = ListingForm(request.POST, request.FILES) 
        if listing_form.is_valid():
            listing_form.save()
            message = "Successfly saved!"
        else:
            message = "Value is not valid!"

        return render(request, "auctions/create_listing.html", {
            "message": message,
            "watchlist_count": utils.get_watchlist_count(request)
        })

    else:
        listing_form = ListingForm()        
        return render(request, "auctions/create_listing.html", {
            "form": listing_form,
            "watchlist_count": utils.get_watchlist_count(request)
        })

def listing_page(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    number_of_bids = Bid.objects.filter(item=listing).count()
    current_bidder = "" # default
    if number_of_bids == 0:
        highest_bid = listing.starting_bid
        bid_price = listing.starting_bid 
    else:
        highest_bid = Bid.objects.filter(item=listing).order_by('-price').first()
        bid_price = highest_bid.price

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        watchlist_count = Watchlist.objects.filter(watcher=user.id, item=listing).count()

        if number_of_bids > 1:
            if highest_bid.bidder.id == request.user.id:
                current_bidder = 'Your bid is the current bid.'
            else:
                current_bidder = "You've been outbid by " + highest_bid.bidder.username

        if user.id == listing.listed_by.id:
            close_auction_btn = "YES" 
        else:
            close_auction_btn = "NO"

        comments = Comment.objects.filter(item=listing)

        return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "bid_price": bid_price,
            "watchlist_count": watchlist_count,
            "number_of_bids": number_of_bids,
            "highest_bid": highest_bid,
            "current_bidder": current_bidder,
            "close_auction_btn": close_auction_btn,
            "comments": comments,
            "watchlist_count": utils.get_watchlist_count(request)
        })

    # No login user
    else:
        watchlist_count = 0
        return render(request, "auctions/listing_page.html", {
            "listing": listing,
            "bid_price": bid_price,
            "watchlist_count": watchlist_count
        })


@login_required()
def create_bid_comment_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)
    message = ""

    if request.method == "POST":

        if 'placebid' in request.POST:
            highest_bid = Bid.objects.filter(item=listing).values('price').order_by('-price').first()
            if not highest_bid: # no bidding yet
                highest_bid = 0
            else:
                highest_bid = highest_bid['price']

            bid_price = Decimal(request.POST['bid'])
            if bid_price < highest_bid: 
                message = "Please enter more then ..." + str(highest_bid)
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

        elif 'close-auction' in request.POST:
            listing.active_listing = "NO"
            listing.save()
            message = "Close the auction."

            num_bids = Bid.objects.filter(item=listing).count() 
            if num_bids == 0:
                winner = "No bidding :("
                winner_username = "No bidding"
                winner_price = 0 
                winner_item = ""

            else:
                winner = utils.highest_bid(listing_id)
                winner_username = winner.bidder.username
                winner_price = winner.price
                winner_item = winner.item.title


            return render(request, "auctions/auction_result.html", {
                "winner_username": winner_username,
                "winner_price": winner_price,
                "winner_item": winner_item
            })

        elif 'add-comment' in request.POST:
            comment = request.POST['your-comment']
            c = Comment(item=listing, author=user, comment=comment)
            c.save()
            message = "Successfully saved!"

    return HttpResponseRedirect(reverse('listing_page', args=(listing_id, )))

def closed_listing(request):
    listings = Listing.objects.filter(active_listing="NO")
    return render(request, "auctions/closed_listing.html", {
        "listings": listings
    })

def closed_listing_page(request, listing_id):
    """
    If a user is signed in on a closed listing page, 
    and the user has won that auction, the page should say so.
    """
    listing = Listing.objects.get(pk=listing_id)
    number_of_bids = Bid.objects.filter(item=listing).count()
    highest_bid = Bid.objects.filter(item=listing).order_by('-price').first()
    if number_of_bids == 0:
        winner_username = "No bidding :("
    else:
        winner_username = highest_bid.bidder.username

    comments = Comment.objects.filter(item=listing)

    return render(request, "auctions/closed_listing_page.html", {
        "listing": listing,
        "number_of_bids": number_of_bids,
        "highest_bid": highest_bid,
        "winner_username": winner_username,
        "comments": comments,
    })
