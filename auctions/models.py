from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related import ManyToManyField
import os


def get_image_path(instance, filename):
    return os.path.join('images', str(instance.id), filename)


class User(AbstractUser):
    watching = ManyToManyField(
        'AuctionItem',
        blank=True,
        related_name='watched_by'
    )

    def __str__(self):
        return f"User {self.pk}: {self.first_name} {self.last_name}"


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"Category: {self.name}"


class AuctionItem(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    current_price = models.DecimalField(max_digits=8, decimal_places=2)
    item_image = models.ImageField(
        upload_to=get_image_path,
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='auction_items'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auctions_created'
    )
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='auctions_won'
    )
    # TODO: Add code to controller to display creation date in user's timezone
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Item: {self.title} listed by {self.creator.first_name}"


class Bid(models.Model):
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    auction_item = models.ForeignKey(
        AuctionItem,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Bid {self.id}: {self.creator.first_name} bids ${self.price} on {self.auction_item.title}"


class Comment(models.Model):
    text = models.TextField()
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent_auction = models.ForeignKey(
        AuctionItem,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    # TODO: Add code to controller to display creation date in user's timezone
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment: {self.text}, made by {self.creator.first_name}"
