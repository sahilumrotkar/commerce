from django.contrib import admin
from .models import User, AuctionItem, Bid, Category, Comment

# Register your models here.
admin.site.register([User, AuctionItem, Bid, Category, Comment])
