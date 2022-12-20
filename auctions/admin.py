from django.contrib import admin
from .models import Listing, Bid, Comment, User, Watchlist, ClosedAuction


# Register your models here.
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Watchlist)
admin.site.register(ClosedAuction)
