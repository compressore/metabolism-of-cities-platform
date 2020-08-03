from django.urls import path
from . import views
from core import views as core
from library import views as library
from ie.urls_baseline import baseline_urlpatterns

app_name = "stocks"
urlpatterns = baseline_urlpatterns + [
    path("", views.landing, name="landing"),
    path("home/", views.index, name="index"),
    path("contribute/", views.contribute, name="contribute"),
    path("publications/", library.list, {"type": "stock"}, name="publications"),
    path("cities/", views.cities, name="cities"),
    path("cities/<slug:slug>/", views.city, name="city"),
    path("cities/<slug:slug>/data/", views.data, name="data"),
    path("cities/<slug:slug>/archetypes/", views.archetypes, name="archetypes"),
    path("cities/<slug:slug>/maps/", views.maps, name="maps"),
    path("cities/<slug:slug>/map/<int:id>/", views.map, name="map"),
    path("cities/<slug:slug>/compare/", views.compare, name="compare"),
    path("cities/<slug:slug>/modeller/", views.modeller, name="modeller"),
    path("cities/<slug:slug>/stories/", views.stories, name="stories"),
    path("cities/<slug:slug>/stories/<slug:title>", views.story, name="story"),
    path("dataset_editor/", views.dataset_editor, name="dataset_editor"),
    path("dataset_editor/chart/", views.chart_editor, name="chart_editor"),
    path("dataset_editor/map/", views.map_editor, name="map_editor"),
]
