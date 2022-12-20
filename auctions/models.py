from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    category = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    description = models.TextField()
    image = models.TextField(blank=True)
    user = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id} / {self.name} / {self.price} / {self.description}"


class Bid(models.Model):
    bid = models.IntegerField()
    item = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bidded_item")
    user = models.CharField(max_length=64, default='none')

    def __str__(self):
        return f"{self.bid}$ for: {self.item.name}"


class Comment(models.Model):
    user = models.CharField(max_length=64, default='none')
    comment = models.TextField()
    item = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="auction_comment")

    def __str__(self):
        return f"{self.comment}"


class Watchlist(models.Model):
    user = models.CharField(max_length=64, default='none')
    item = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="watchlist_items")

    def __str__(self):
        return f"{self.user}: {self.item.name}"


class ClosedAuction(models.Model):
    item = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="closed_auction")
    winner = models.ForeignKey(
        Bid, on_delete=models.CASCADE, related_name="auction_winner", blank=True, null=True)
