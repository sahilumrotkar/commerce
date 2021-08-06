from django import template

register = template.Library()

"""
Returns the price of themost recent bid placed by the user on a particular 
auction item.

eg. user|latest_bid_price_for_auction:auction_item
"""


@register.filter(name='latest_bid_price_for_auction')
def latest_bid_price_for_auction(obj, auction_item):
    if auction_item is not None:
        return obj.bids.filter(auction_item=auction_item).latest('creation_date').price
    else:
        return None


"""
Returns the number of bids that are higher than the price passed as argument, for
a particular auction item.

eg. auction_item|get_number_of_higher_bids:price
"""


@register.filter(name='number_of_higher_bids')
def number_of_higher_bids(obj, price):
    if price is not None:
        return obj.bids.filter(price__gt=price).count()
    else:
        return None


@register.filter(name='has_bid_on_auction')
def has_bid_on_auction_item(obj, auction_item):
    queryset = obj.bids.filter(auction_item=auction_item)
    return True if queryset else False
