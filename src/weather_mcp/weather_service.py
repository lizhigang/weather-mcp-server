"""Mock weather data generation service."""

import hashlib
import random
from datetime import date, timedelta

# Supported cities with metadata: (country, latitude, longitude)
SUPPORTED_CITIES: dict[str, dict] = {
    "Beijing": {"country": "China", "lat": 39.9, "lon": 116.4},
    "Shanghai": {"country": "China", "lat": 31.2, "lon": 121.5},
    "Tokyo": {"country": "Japan", "lat": 35.7, "lon": 139.7},
    "Seoul": {"country": "South Korea", "lat": 37.6, "lon": 127.0},
    "Singapore": {"country": "Singapore", "lat": 1.4, "lon": 103.8},
    "Mumbai": {"country": "India", "lat": 19.1, "lon": 72.9},
    "Dubai": {"country": "UAE", "lat": 25.3, "lon": 55.3},
    "London": {"country": "UK", "lat": 51.5, "lon": -0.1},
    "Paris": {"country": "France", "lat": 48.9, "lon": 2.3},
    "Berlin": {"country": "Germany", "lat": 52.5, "lon": 13.4},
    "Moscow": {"country": "Russia", "lat": 55.8, "lon": 37.6},
    "New York": {"country": "USA", "lat": 40.7, "lon": -74.0},
    "Los Angeles": {"country": "USA", "lat": 34.1, "lon": -118.2},
    "Sydney": {"country": "Australia", "lat": -33.9, "lon": 151.2},
    "Sao Paulo": {"country": "Brazil", "lat": -23.5, "lon": -46.6},
}

CONDITIONS = ["sunny", "cloudy", "partly cloudy", "rainy", "stormy", "snowy", "foggy", "windy"]


def _get_seed(city: str, day: date) -> int:
    """Create a deterministic seed from city name and date."""
    key = f"{city.lower()}:{day.isoformat()}"
    return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)


def _base_temp(lat: float, month: int) -> float:
    """Calculate base temperature from latitude and month.

    Tropical regions stay warm year-round. Higher latitudes have seasonal variation.
    Southern hemisphere has inverted seasons.
    """
    # Seasonal offset: peaks in July (month 7) for northern hemisphere
    seasonal_factor = -((month - 7) ** 2) / 12 + 3  # range roughly -12 to 3
    # Latitude effect: equator ~28C, poles ~-10C
    lat_effect = 28 - abs(lat) * 0.6
    # Southern hemisphere inversion
    if lat < 0:
        seasonal_factor = -seasonal_factor
    return lat_effect + seasonal_factor


def get_current_weather(city: str) -> dict:
    """Get mock current weather for a city.

    Returns a dict with temperature, feels_like, humidity, wind_speed,
    conditions, and city metadata.
    """
    city_info = SUPPORTED_CITIES.get(city)
    if city_info is None:
        return {
            "error": f"City '{city}' is not supported.",
            "supported_cities": list(SUPPORTED_CITIES.keys()),
        }

    today = date.today()
    seed = _get_seed(city, today)
    rng = random.Random(seed)

    base = _base_temp(city_info["lat"], today.month)
    temperature = round(base + rng.uniform(-5, 5), 1)
    humidity = rng.randint(30, 90)
    wind_speed = round(rng.uniform(0, 35), 1)

    # Snowy only if cold enough
    available_conditions = [c for c in CONDITIONS if c != "snowy" or temperature < 2]
    condition = rng.choice(available_conditions)

    # Wind chill / heat index approximation
    if temperature < 10:
        feels_like = round(temperature - wind_speed * 0.15, 1)
    elif temperature > 27:
        feels_like = round(temperature + humidity * 0.05, 1)
    else:
        feels_like = temperature

    return {
        "city": city,
        "country": city_info["country"],
        "date": today.isoformat(),
        "temperature_celsius": temperature,
        "feels_like_celsius": feels_like,
        "humidity_percent": humidity,
        "wind_speed_kmh": wind_speed,
        "conditions": condition,
        "latitude": city_info["lat"],
        "longitude": city_info["lon"],
    }


def get_forecast(city: str, days: int = 3) -> dict:
    """Get mock multi-day weather forecast for a city.

    days: number of forecast days (clamped to 1-7).
    """
    city_info = SUPPORTED_CITIES.get(city)
    if city_info is None:
        return {
            "error": f"City '{city}' is not supported.",
            "supported_cities": list(SUPPORTED_CITIES.keys()),
        }

    days = max(1, min(days, 7))
    today = date.today()
    forecast_days = []

    for i in range(days):
        day = today + timedelta(days=i)
        seed = _get_seed(city, day)
        rng = random.Random(seed)

        base = _base_temp(city_info["lat"], day.month)
        high = round(base + rng.uniform(0, 6), 1)
        low = round(base + rng.uniform(-8, -1), 1)
        humidity = rng.randint(30, 90)
        wind_speed = round(rng.uniform(0, 35), 1)
        precipitation_chance = rng.randint(0, 100)

        available_conditions = [c for c in CONDITIONS if c != "snowy" or high < 2]
        condition = rng.choice(available_conditions)

        forecast_days.append({
            "date": day.isoformat(),
            "high_celsius": high,
            "low_celsius": low,
            "humidity_percent": humidity,
            "wind_speed_kmh": wind_speed,
            "precipitation_chance_percent": precipitation_chance,
            "conditions": condition,
        })

    return {
        "city": city,
        "country": city_info["country"],
        "days": days,
        "forecast": forecast_days,
    }


def get_cities() -> list[dict]:
    """List all supported cities with metadata."""
    return [
        {
            "city": name,
            "country": info["country"],
            "latitude": info["lat"],
            "longitude": info["lon"],
        }
        for name, info in SUPPORTED_CITIES.items()
    ]
