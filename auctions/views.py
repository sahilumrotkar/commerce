from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm, widgets, Textarea
from django.contrib.auth.decorators import login_required

from .models import User, AuctionItem, Comment, Category, Bid


class AuctionItemForm(ModelForm):
    class Meta:
        model = AuctionItem
        exclude = ['creator', 'is_active', 'winner', 'creation_date']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        exclude = ['creator', 'auction_item', 'creation_date']
        labels = {
            'price': "Bid Amount"
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ['creator', 'parent_auction', 'creation_date']
        labels = {
            'text': ""
        }
        widgets = {
            'text': Textarea(attrs={'cols': 45, 'rows': 4}),
        }


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

            return HttpResponseRedirect(reverse('auction_view', args=[auction_item.id]))
            # return HttpResponseRedirect(reverse('index'))

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


def auction_view(request, id):
    # TODO: Ensure bid amount is greater than current price of item
    if request.method == 'POST':
        auction_item = AuctionItem.objects.get(pk=id)
        bid_form = BidForm(request.POST)
        if bid_form.is_valid():
            bid = bid_form.save(commit=False)
            bid.creator = request.user
            bid.auction_item = auction_item
            bid.save()

            new_price = bid.price
            updated_rows = AuctionItem.objects.filter(
                id=id).update(current_price=new_price)

            return render(request, "auctions/auction_view.html", {
                'auction_item': AuctionItem.objects.get(pk=id),
                'bid_form': bid_form,
                'total_bids': AuctionItem.objects.get(pk=id).bids.count(),
                # TODO: in message, add link to direct user to their bids placed page
                'message': "Bid created successfully.",
                'comment_form': CommentForm()
            })

        else:
            return render(request, "auctions/auction_view.html", {
                'auction_item': auction_item,
                'bid_form': bid_form,
                'total_bids': Bid.objects.all().count(),
                'message': "Error placing bid.",
                'comment_form': CommentForm()
            })

    else:
        # render auction view
        auction_items_queryset = AuctionItem.objects.filter(pk=id)

        if auction_items_queryset.exists():
            auction_item = auction_items_queryset.first()
            return render(request, "auctions/auction_view.html", {
                'auction_item': auction_item,
                'bid_form': BidForm(),
                'total_bids': auction_item.bids.count(),
                'comment_form': CommentForm()
            })
        else:
            # TODO: render an item does not exist template
            pass


def new_comment(request, auction_id):
    if request.method == 'POST':
        auction_item = AuctionItem.objects.get(pk=auction_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.creator = request.user
            comment.parent_auction = auction_item
            comment.save()
            return HttpResponseRedirect(reverse('auction_view', args=[auction_id]))

        else:
            return render(request, "auctions/auction_view.html", {
                'comment_error': "Failed to add comment.",
                'auction_item': auction_item,
                'bid_form': BidForm(),
                'total_bids': auction_item.bids.count()
            })

    else:
        # TODO: render 403 forbidden template
        pass
