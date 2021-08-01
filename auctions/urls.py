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
         views.new_comment, name="new_comment")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
