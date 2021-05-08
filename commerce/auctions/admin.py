from django.contrib import admin
from .models import User, Listing, Comment, Bid,  Watchlist

class ListingAdmin(admin.ModelAdmin):
    readonly_fields = ('listing_datetime',)
class BidAdmin(admin.ModelAdmin):
    readonly_fields = ('bidding_datetime',)
class CommentAdmin(admin.ModelAdmin):
    readonly_fields = ('created_date',)

# Register your models here.
admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Watchlist)
