from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Watchlist, Bid, ClosedAuction, Comment

categories = ["Fashion", "Toys", "Electornics", "Home"]


def index(request):
    closed = ClosedAuction.objects.all()
    auction_closed = []
    for auction in closed:
        auction_closed.append(Listing.objects.get(name=auction.item.name))

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "auction_closed": auction_closed
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


@login_required()
def create_listing(request):

    if request.method == "POST":

        # Get form input values and user
        category = request.POST["category"]
        name = request.POST["title"]
        price = request.POST["starting-bid"]
        description = request.POST["description"]
        listing_img = request.POST["image"]
        user = User.objects.get(pk=request.user.id)

        # Store the info in the model
        Listing.objects.create(user=user, category=category, image=listing_img,
                               name=name, price=price, description=description)

        return HttpResponseRedirect(reverse("index"))

    return render(request, "listings/create_listing.html", {
        "categories": categories,
    })


def listing_page(request, listing_id):

    # Get listing and check if has bids or is closed
    listing = Listing.objects.get(pk=listing_id)
    bids_exists = Bid.objects.filter(item=listing).exists()
    closed = ClosedAuction.objects.filter(item=listing).exists()

    # Set the winner if there is one
    if closed and not ClosedAuction.objects.get(item=listing).winner == None:
        winner = ClosedAuction.objects.filter(item=listing).first().winner.user
    else:
        winner = None

    # Set bids if there are any
    if bids_exists:
        bids = Bid.objects.filter(item=listing).order_by('bid')
    else:
        bids = None

    if request.user.is_authenticated:

        # Get user watchlist
        user = User.objects.get(pk=request.user.id)
        in_watchlist = Watchlist.objects.filter(
            user=user, item=listing).exists()

        if request.method == "POST":

            # Set the comment and render it on the page
            comment = request.POST["comment"]

            if len(comment) > 1:
                Comment.objects.create(
                    user=user, item=listing, comment=comment)

                return HttpResponseRedirect(reverse('listing_page', kwargs={"listing_id": listing_id}))
            else:
                return render(request, "listings/listing_page.html", {
                    "listing": listing,
                    "winner": winner,
                    "logged_user": user.username,
                    "comments": Comment.objects.filter(item=listing),
                    "closed": closed,
                    "watchlist": in_watchlist,
                    "bids": bids,
                    "message": 'Please type something.'
                })

        return render(request, "listings/listing_page.html", {
            "listing": listing,
            "logged_user": user.username,
            "closed": closed,
            "winner": winner,
            "bids": bids,
            "comments": Comment.objects.filter(item=listing),
            "watchlist": in_watchlist
        })

    return render(request, "listings/listing_page.html", {
        "listing": listing,
        "comments": Comment.objects.filter(item=listing),
        "closed": closed,
        "bids": bids,
    })


@login_required()
def add_to_watchlist(request, listing_id):

    # Get the listing and user and add it into watchlist model
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)
    Watchlist.objects.create(user=user, item=listing)

    return HttpResponseRedirect(reverse("listing_page", kwargs={"listing_id": listing_id}))


@login_required()
def remove_from_watchlist(request, listing_id):

    # Get the listing and user and remove it from the watchlist model
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)
    Watchlist.objects.filter(user=user, item=listing).delete()

    return HttpResponseRedirect(reverse("listing_page", kwargs={"listing_id": listing_id}))


@login_required()
def bid(request, listing_id):

    # Get the listing and the user, and check for bids on the listing
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)
    prev_bids = Bid.objects.filter(item=listing).exists()

    # Get the bid input value, set error messages, create bid and redirect to listing page
    if request.method == "POST":
        bid = request.POST["bid"]

        if len(bid) < 1 or int(bid) < listing.price:
            return render(request, "listings/bid.html", {
                "listing": listing,
                "message": 'Bid must be at least as large as the starting bid'
            })

        if prev_bids:
            if int(bid) <= Bid.objects.filter(item=listing).order_by('bid').last().bid:
                return render(request, "listings/bid.html", {
                    "listing": listing,
                    "message": 'Bid must be greater than the highest bid',
                })

        Bid.objects.create(item=listing, user=user, bid=bid)
        return HttpResponseRedirect(reverse("listing_page", kwargs={"listing_id": listing_id}))

    if prev_bids:
        return render(request, "listings/bid.html", {
            "listing": listing,
            "highest_bid": Bid.objects.filter(item=listing).order_by('bid').last().bid
        })

    return render(request, "listings/bid.html", {
        "listing": listing,
    })


def closed_auction(request, listing_id):

    # Get listing and the highest bid and set the winner
    listing = Listing.objects.get(pk=listing_id)
    bid = Bid.objects.filter(item=listing).exists()
    if bid:
        highest_bid = Bid.objects.filter(item=listing).order_by('bid').last()
        ClosedAuction.objects.create(item=listing, winner=highest_bid)
    else:
        ClosedAuction.objects.create(item=listing, winner=None)

    return HttpResponseRedirect(reverse("listing_page", kwargs={"listing_id": listing_id}))


def user_watchlist(request):

    # Get user watchlist and render it
    user = User.objects.get(pk=request.user.id)
    watchlist = Watchlist.objects.filter(user=user)

    return render(request, "listings/watchlist.html", {
        "watchlist": watchlist
    })


def listing_categories(request, category):

    # Get and render listings on it's category
    closed = ClosedAuction.objects.all()
    auction_closed = []

    for auction in closed:
        auction_closed.append(Listing.objects.get(name=auction.item.name))

    if category == "all":
        return render(request, "listings/categories.html", {
            "categories": categories})

    if category in categories:
        return render(request, "listings/categories.html", {
            "listings": Listing.objects.filter(category=category),
            "auction_closed": auction_closed,
            "category": category
        })
