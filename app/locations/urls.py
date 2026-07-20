from django.urls import path
from . import views

app_name = "locations"

urlpatterns = [
    path("seed/start/", views.start_seed_locations, name="seed_locations_start"),
    path("seed/progress/", views.seed_locations_progress, name="seed_locations_progress"),
    path("cities/", views.cities_by_country, name="cities_by_country"),
    path("search-countries/", views.search_countries, name="search_countries"),
    path("search-cities/", views.search_cities, name="search_cities"),
]