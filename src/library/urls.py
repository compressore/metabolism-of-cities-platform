from django.urls import path
from . import views
from core import views as core

app_name = "library"

urlpatterns = [
    path("", views.index, name="index"),
    path("casestudies/", views.casestudies, name="casestudies"),
    path("tags/", views.tags, name="tags"),
    path("tags/json/", views.tags_json, name="tags_json"),
    path("list/", views.list, name="list"),
    path("list/<slug:type>/", views.list, name="list"),
    path("casestudies/map/", views.map, { "article": 50 }, name="map"),
    path("casestudies/<slug:slug>/", views.casestudies, name="casestudies"),
    path("download/", views.download, name="download"),
    path("journals/", views.journals, { "article": 41 }, name="journals"),
    path("journals/<slug:slug>/", views.journal, name="journal"),
    path("items/<int:id>/", views.item, name="item"),
    path("authors/", views.authors, name="authors"),
    path("contribute/", views.contribute, name="contribute"),
    path("create/", views.form, name="form"),

    # Accounts functions
    path("accounts/login/", core.user_login, name="login"),

]
