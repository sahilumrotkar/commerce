from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required

from .models import User, AuctionItem, Comment, Category, Bid


class AuctionItemForm(ModelForm):
    class Meta:
        model = AuctionItem
        exclude = ['creator', 'is_active', 'winner', 'creation_date']


def index(request):
    return render(request, "auctions/index.html")


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


# TODO: add redirects from login using @login_required decorator
def new_auction(request):

    if request.method == 'POST':
        # retrieve form data and create a new auction item in the database
        form = AuctionItemForm(request.POST, request.FILES)

        if form.is_valid():
            auction_item = form.save(commit=False)
            auction_item.creator = User.objects.get(pk=request.user.id)
            auction_item.save()

            # TODO: redirect user to auction page
            # return HttpResponseRedirect(reverse('auction_item', args=[auction_item.id]))
            return HttpResponseRedirect(reverse('index'))

        else:
            message = "There was an error creating your auction."
            return render(request, "auctions/new_auction.html", {
                'message': message,
                'auction_item_form': form
            })

    else:
        # render create form template (depending on whether user in authenticated
        # or not)
        return render(request, "auctions/new_auction.html", {
            'auction_item_form': AuctionItemForm()
        })
