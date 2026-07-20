import json
import threading
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.shortcuts import render
from django.db import connection

from .models import Country, City
from .utils import normalize_name
from django.http import JsonResponse


def search_countries(request):
    q = request.GET.get("q", "").strip()

    countries = Country.objects.all()

    if q:
        countries = countries.filter(name_en__icontains=q)

    data = [
        {
            "id": country.id,
            "text": country.name_en,
        }
        for country in countries[:20]
    ]

    return JsonResponse({"results": data})


def search_cities(request):
    q = request.GET.get("q", "").strip()
    country_id = request.GET.get("country_id")

    cities = City.objects.all()

    if country_id:
        cities = cities.filter(country_id=country_id)

    if q:
        cities = cities.filter(name_en__icontains=q)

    data = [
        {
            "id": city.id,
            "text": city.name_en,
        }
        for city in cities[:30]
    ]

    return JsonResponse({"results": data})


def cities_by_country(request):
    country_id = request.GET.get("country_id")

    cities = City.objects.filter(country_id=country_id).order_by("name_en")

    data = [
        {
            "id": city.id,
            "name": city.name_en,
        }
        for city in cities
    ]

    return JsonResponse({"cities": data})


def run_seed_locations():
    cache.set("locations_import_progress", {
        "status": "running",
        "percent": 0,
        "message": "Starting import..."
    }, timeout=3600)

    fixtures_path = Path(settings.BASE_DIR) / "fixtures"
    countries_file = fixtures_path / "countries.json"
    cities_path = fixtures_path / "cities"

    with open(countries_file, "r", encoding="utf-8") as f:
        countries_data = json.load(f)

    if isinstance(countries_data, dict):
        countries_data = countries_data.values()

    country_map = {}

    for item in countries_data:
        country, _ = Country.objects.update_or_create(
            name_en=item["country_eng"],
            defaults={
                "name_ua": item["country_ukr"],
                "flag_url": item.get("country_flag"),
                "phone_code": item.get("country_phone_code"),
            }
        )
        country_map[normalize_name(country.name_en)] = country

    city_files = list(cities_path.glob("*.json"))
    total_files = len(city_files)

    for index, city_file in enumerate(city_files, start=1):
        country_key = normalize_name(city_file.stem)
        country = country_map.get(country_key)

        if not country:
            continue

        with open(city_file, "r", encoding="utf-8") as f:
            cities_data = json.load(f)

        if isinstance(cities_data, dict):
            cities_data = cities_data.values()

        for city_item in cities_data:
            City.objects.update_or_create(
                country=country,
                name_en=city_item["en"],
                defaults={
                    "name_ua": city_item.get("ua", city_item["en"])
                }
            )

        percent = int((index / total_files) * 100)

        cache.set("locations_import_progress", {
            "status": "running",
            "percent": percent,
            "message": f"Imported {city_file.name}"
        }, timeout=3600)

    cache.set("locations_import_progress", {
        "status": "done",
        "percent": 100,
        "message": "Import completed"
    }, timeout=3600)


@staff_member_required
def start_seed_locations(request):
    City.objects.all().delete()
    Country.objects.all().delete()

    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE locations_country_id_seq RESTART WITH 1;")
        cursor.execute("ALTER SEQUENCE locations_city_id_seq RESTART WITH 1;")
    thread = threading.Thread(target=run_seed_locations)
    thread.start()

    return JsonResponse({"status": "started"})


@staff_member_required
def seed_locations_progress(request):
    progress = cache.get("locations_import_progress", {
        "status": "idle",
        "percent": 0,
        "message": "Not started"
    })

    return JsonResponse(progress)