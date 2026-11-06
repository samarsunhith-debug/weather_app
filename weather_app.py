"""Weather App with the live OpenWeather API (InternCircle Project 5).

Asks for a city and shows the current temperature, humidity, conditions and
wind, followed by a 5-day forecast table. The API key is read from a .env file
(or an environment variable) and is never written in the code.
"""

import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()  # reads OPENWEATHER_KEY from the .env file, if there is one

API_KEY = os.getenv("OPENWEATHER_KEY")
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
UNITS = "metric"          # metric = Celsius and metres per second
TIMEOUT = 10              # seconds to wait for the API
CACHE_SECONDS = 600       # remember results for 10 minutes (saves free requests)
FORECAST_DAYS = 5

_cache = {}  # (kind, city) -> (time saved, data)


# ---------- API access ----------

def api_get(url, city):
    """Call the API for a city. Return parsed JSON, or None after printing why.

    Error messages never include the request URL, because the URL contains the
    API key.
    """
    try:
        response = requests.get(
            url,
            params={"q": city, "appid": API_KEY, "units": UNITS},
            timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        print("Network problem. Check your internet connection and try again.")
        return None

    if response.status_code == 404:
        print(f"City '{city}' was not found. Check the spelling.")
        return None
    if response.status_code == 401:
        print("The API key was rejected (401). New keys can take a couple of "
              "hours to start working; otherwise check your .env file.")
        return None
    if response.status_code == 429:
        print("Too many requests (429). Please wait a minute and try again.")
        return None
    if response.status_code != 200:
        print(f"The weather service returned an error ({response.status_code}).")
        return None
    try:
        return response.json()
    except ValueError:
        print("The weather service sent a reply that could not be read.")
        return None


def cached_get(kind, url, city):
    """Like api_get, but reuses a recent answer for the same city."""
    key = (kind, city.lower())
    saved = _cache.get(key)
    if saved and time.time() - saved[0] < CACHE_SECONDS:
        return saved[1]
    data = api_get(url, city)
    if data is not None:
        _cache[key] = (time.time(), data)
    return data


# ---------- Extracting fields (.get() so missing data never crashes) ----------

def first_description(data):
    """Return the weather description from a reply, or 'n/a'."""
    weather = data.get("weather") or [{}]
    return weather[0].get("description", "n/a")


def summarise_current(data):
    """Turn the current-weather JSON into a dict of display values."""
    main = data.get("main", {})
    return {
        "city": data.get("name", "Unknown"),
        "country": data.get("sys", {}).get("country", ""),
        "temp": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "humidity": main.get("humidity"),
        "description": first_description(data),
        "wind": data.get("wind", {}).get("speed"),
    }


def pick_daily_entries(data, max_days=FORECAST_DAYS):
    """Pick one forecast entry per day (the one closest to midday)."""
    best = {}  # date string -> (distance from 12:00, entry)
    for entry in data.get("list", []):
        stamp = entry.get("dt_txt", "")
        try:
            moment = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        distance = abs(moment.hour - 12)
        day = stamp[:10]
        if day not in best or distance < best[day][0]:
            best[day] = (distance, entry)
    return [best[day][1] for day in sorted(best)][:max_days]


# ---------- Display ----------

def fmt(value, unit="", digits=1):
    """Format a number with a unit, or 'n/a' if the value is missing."""
    if value is None:
        return "n/a"
    if isinstance(value, float):
        value = round(value, digits)
    return f"{value}{unit}"


def show_current(info):
    """Print the current weather."""
    place = f"{info['city']}, {info['country']}" if info["country"] else info["city"]
    print(f"\n{place}")
    print(f"  Temperature : {fmt(info['temp'], ' °C')} "
          f"(feels like {fmt(info['feels_like'], ' °C')})")
    print(f"  Humidity    : {fmt(info['humidity'], '%')}")
    print(f"  Conditions  : {info['description']}")
    print(f"  Wind        : {fmt(info['wind'], ' m/s')}")


def show_forecast(entries):
    """Print the forecast as a small table."""
    if not entries:
        print("\nNo forecast available.")
        return
    print(f"\n{len(entries)}-day forecast")
    print(f"{'Date':<12}{'Temp':>10}   Conditions")
    print("-" * 40)
    for entry in entries:
        temp = fmt(entry.get("main", {}).get("temp"), " °C")
        print(f"{entry['dt_txt'][:10]:<12}{temp:>10}   {first_description(entry)}")


def report(city):
    """Fetch and print current weather plus forecast for one city."""
    current = cached_get("current", CURRENT_URL, city)
    if current is None:
        return
    show_current(summarise_current(current))
    forecast = cached_get("forecast", FORECAST_URL, city)
    if forecast is not None:
        show_forecast(pick_daily_entries(forecast))


def main():
    """Ask for cities until the user enters nothing."""
    if not API_KEY:
        print("No API key found. Create a .env file containing the line:")
        print("OPENWEATHER_KEY=your_key_here")
        sys.exit(1)
    while True:
        city = input("\nCity (blank to quit): ").strip()
        if not city:
            print("Goodbye!")
            break
        report(city)


if __name__ == "__main__":
    main()
