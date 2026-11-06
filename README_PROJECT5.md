# Weather App with the Live OpenWeather API

A command-line app that shows the current temperature, humidity, conditions and
wind for any city, plus a 5-day forecast table, using the OpenWeather REST API.

## Setup
1. Install Python 3.10+ and the libraries:
   ```
   pip install requests python-dotenv
   ```
2. Get a free API key: sign up at https://openweathermap.org, then copy your key
   from the "API keys" page. **New keys can take up to a couple of hours to start
   working** (a 401 error just after signing up is normal).
3. Create a file named `.env` next to `weather_app.py` (copy `.env.example`):
   ```
   OPENWEATHER_KEY=your_key_here
   ```
4. Run:
   ```
   python weather_app.py
   ```
   Type a city name and press Enter. Press Enter on an empty line to quit.

## What it shows
- Temperature (°C, with "feels like"), humidity, description and wind speed
- A forecast table with one entry per day (the one closest to midday)

## Error handling
Unknown city (404), bad key (401), too many requests (429), other API errors,
network problems, unreadable replies and missing fields all give a friendly
message instead of a crash.

## How the API key is protected
- The key lives only in `.env`, which is listed in `.gitignore` and never committed.
- The code reads it with `os.getenv("OPENWEATHER_KEY")`; it is not written anywhere in the code.
- Error messages never print the request URL (the URL contains the key).
- Check before pushing: run `git status` and confirm `.env` is not listed.
- If a key is ever leaked, delete it in your OpenWeather account and create a new one.

## Other details
- Results are cached for 10 minutes so repeated lookups do not use up the free request limit.
- Requests use `units=metric` (Celsius) and a 10-second timeout.

## Files
- `weather_app.py` - the program
- `.env.example` - template for your `.env` (contains no real key)
- `.gitignore` - keeps `.env` out of the repository
