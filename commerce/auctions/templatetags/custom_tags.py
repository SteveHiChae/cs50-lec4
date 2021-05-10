from django import template

from auctions.models import *
from django.db.models import Max

register = template.Library()

# @register.simple_tag
def max_bid(bid_price, arg):
    max_bid = Bid.objects.filter(item=arg).values('item').annotate(Max('price'))
    if len(max_bid) == 0:
        listing = Listing.objects.get(pk=arg) 
        bid_price = listing.starting_bid
    else:
        bid_price = float(max_bid[0]['price__max'])

    return bid_price

register.filter('max_bid', max_bid)