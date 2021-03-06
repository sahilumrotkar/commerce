from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm, widgets, Textarea
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .models import User, AuctionItem, Comment, Category, Bid
from datetime import datetime


class AuctionItemForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.has_bids = kwargs.pop('has_bids', None)
        super(AuctionItemForm, self).__init__(*args, **kwargs)
        if self.has_bids is not None and self.has_bids == 1:
            del self.fields['current_price']

    class Meta:
        model = AuctionItem
        exclude = ['creator', 'is_active', 'winner',
                   'creation_date', 'closing_date']


# def create_edit_auction_item_form(has_bids=True):

#     class EditAuctionItemForm(ModelForm):

#         class Meta:
#             model = AuctionItem
#             exclude = ['creator', 'is_active', 'winner',
#                        'creation_date', 'closing_date']

#             if has_bids:
#                 exclude.append('current_price')

#     return EditAuctionItemForm


class BidForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.old_price = kwargs.get('old_price', None)
        if self.old_price is not None:
            kwargs.pop('old_price')
        super(BidForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Bid
        exclude = ['creator', 'auction_item', 'creation_date']
        labels = {
            'price': "Bid Amount"
        }
        widgets = {
            'price': widgets.Input(attrs={
                'title': "Value must be greater than current price",
                'type': 'number',
                'step': '0.01'
            })
        }
        help_texts = {
            'price': "Enter an amount greater than the current price."
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')

        # perform validation on price
        if price < 0:
            raise ValidationError("Amount must be greater than zero.")

        if self.old_price is not None and price <= self.old_price:
            raise ValidationError(
                "Amount must be greater than the current price.")

        return price


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ['creator', 'parent_auction',
                   'creation_date', 'parent_comment']
        labels = {
            'text': ""
        }
        widgets = {
            'text': Textarea(attrs={'cols': 45, 'rows': 4}),
        }


def index(request):
    auction_items = AuctionItem.objects.filter(is_active=True)
    return render(request, "auctions/auction_list_view.html", {
        'auction_list': auction_items,
        'title': "Active Listings"
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
    if request.method == 'POST':
        auction_item = AuctionItem.objects.get(pk=id)
        bid_form = BidForm(request.POST, old_price=auction_item.current_price)
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
                'success_message': "Bid created successfully.",
                'comment_form': CommentForm()
            })

        else:
            return render(request, "auctions/auction_view.html", {
                'auction_item': auction_item,
                'bid_form': bid_form,
                'total_bids': AuctionItem.objects.get(pk=id).bids.count(),
                'error_message': "Error placing bid.",
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
                'total_bids': auction_item.bids.count(),
                'comment_form': form
            })

    else:
        # TODO: render 403 forbidden template
        pass


def categories(request):

    return render(request, "auctions/categories.html", {
        'categories': Category.objects.all()
    })


def category_view(request, category_name):

    category = Category.objects.filter(name=category_name).first()
    auction_items = category.auction_items.all()

    return render(request, "auctions/auction_list_view.html", {
        'auction_list': auction_items,
        'title': category_name
    })


def display_all_auction_items(request):
    auction_items = AuctionItem.objects.all()

    return render(request, "auctions/auction_list_view.html", {
        'auction_list': auction_items,
        'title': "All Auctions"
    })


def display_closed_auction_items(request):
    auction_items = AuctionItem.objects.filter(is_active=False)

    return render(request, "auctions/auction_list_view.html", {
        'auction_list': auction_items,
        'title': "Closed Auctions"
    })


def watchlist_view(request, user_id):

    user_qs = User.objects.filter(pk=user_id)

    if user_qs:
        user = user_qs.first()
        watchlist = user.watching.all()

        return render(request, "auctions/auction_list_view.html", {
            'auction_list': watchlist,
            'title': "Watchlist"
        })

    else:
        # TODO: render 404 page
        pass


def update_watchlist(request, user_id, auction_id):

    if request.method == 'POST':
        user_qs = User.objects.filter(pk=user_id)
        auction_item_qs = AuctionItem.objects.filter(pk=auction_id)

        if user_qs and auction_item_qs:
            user = user_qs.first()
            auction_item = auction_item_qs.first()

            watchlist = user.watching.all()
            if auction_item in watchlist:
                user.watching.remove(auction_item)
                message = "Removed from Watchlist Successfully"
            else:
                user.watching.add(auction_item)
                message = "Added to Watchlist Successfully"

            return render(request, "auctions/auction_view.html", {
                'auction_item': auction_item,
                'bid_form': BidForm(),
                'total_bids': auction_item.bids.count(),
                'comment_form': CommentForm(),
                'success_message': message
            })

        else:
            # TODO: forbidden
            pass

    else:
        # TODO: render 403 forbidden template
        pass


def close_auction(request, auction_id):

    if request.method == 'POST':
        auction_item_qs = AuctionItem.objects.filter(pk=auction_id)

        if auction_item_qs:
            auction_item = auction_item_qs.first()
            winner = auction_item.get_highest_bid().creator
            title = f"{auction_item.title} (Closed)"
            auction_item.winner = winner
            auction_item.closing_date = datetime.now()
            auction_item.is_active = False
            auction_item.title = title
            auction_item.save()

            return render(request, "auctions/auction_view.html", {
                'auction_item': auction_item,
                'bid_form': BidForm(),
                'total_bids': auction_item.bids.count(),
                'comment_form': CommentForm(),
                'success_message': "Auction has been closed successfully"
            })

        else:
            # TODO: forbidden
            pass

    else:
        # TODO: render forbidden template
        pass


def update_auction_item(request, auction_id):

    try:
        auction_item = AuctionItem.objects.get(pk=auction_id)
    except ObjectDoesNotExist:
        # render does not exist template
        pass

    has_bids = 1 if auction_item.bids.count() > 0 else 0

    if request.method == 'POST':

        auction_item_form = AuctionItemForm(
            request.POST, request.FILES, instance=auction_item, has_bids=has_bids)

        if auction_item_form.is_valid():

            auction_item_form.save()

            return render(request, "auctions/auction_view.html", {
                'auction_item': auction_item,
                'bid_form': BidForm(),
                'total_bids': auction_item.bids.count(),
                'comment_form': CommentForm(),
                'success_message': "Auction has been updated successfully"
            })

        else:
            return render(request, "auctions/update_auction.html", {
                'auction_item': auction_item,
                'auction_item_form': auction_item_form,
                'title': f"Error Updating {auction_item.title}"
            })

    else:

        auction_item_form = AuctionItemForm(
            instance=auction_item, has_bids=has_bids)

        return render(request, "auctions/update_auction.html", {
            'auction_item': auction_item,
            'auction_item_form': auction_item_form,
            'title': f"Update {auction_item.title}"
        })

# handles deleting/canceling (if 1 or more bids have been placed) an auction item


def delete_auction_item(request, auction_id):

    pass


def user_profile(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        # return user does not exist template
        pass

    return render(request, "auctions/user_profile.html")


def user_bids(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        # return user does not exist template
        pass

    return None


def user_auctions(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        # return user does not exist template
        pass

    return render(request, "auctions/user_auctions.html", {
        'auctions_won': user.auctions_won.all(),
        'auctions_created_active': user.auctions_created.filter(is_active=True),
        'auctions_created_closed': user.auctions_created.filter(is_active=False)
    })
