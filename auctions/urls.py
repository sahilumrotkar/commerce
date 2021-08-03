from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new_auction", views.new_auction, name="new_auction"),
    path("auction/<int:id>", views.auction_view, name="auction_view"),
    path("auction/<int:auction_id>/new_comment",
         views.new_comment, name="new_comment"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category_name>",
         views.category_view, name='category_view'),
    path("<int:user_id>/watchlist/update/<int:auction_id>",
         views.update_watchlist, name='update_watchlist'),
    path("<int:user_id>/watchlist", views.watchlist_view, name='watchlist_view'),
    path("close_auction/<int:auction_id>",
         views.close_auction, name='close_auction')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
