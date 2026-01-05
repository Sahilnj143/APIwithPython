"""
Part 5: Real-World APIs - Weather, Crypto & AQI Dashboard
=========================================================
Includes:
- Weather (OpenWeatherMap API key via env + Open-Meteo fallback)
- Crypto prices (CoinPaprika)
- Air Quality Index (Last 7 days – Open-Meteo AQI)
"""

import requests
import json
import os
from datetime import datetime


# -------------------- LOAD API KEY --------------------
OPENWEATHER_API_KEY = os.environ.get("ce3ad724b5c4fabbba109ce7276d1aa1")
5

# -------------------- CITY COORDINATES --------------------
CITIES = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "pune": (18.5204, 73.8567),
    "chennai": (13.0827, 80.2707),
}


# -------------------- CRYPTO IDS --------------------
CRYPTO_IDS = {
    "bitcoin": "btc-bitcoin",
    "ethereum": "eth-ethereum",
    "dogecoin": "doge-dogecoin",
    "cardano": "ada-cardano",
    "solana": "sol-solana",
}


# -------------------- WEATHER --------------------
def get_weather(city):
    city = city.lower().strip()

    if city not in CITIES:
        print("City not available!")
        return None

    lat, lon = CITIES[city]

    # Preferred: OpenWeatherMap
    if OPENWEATHER_API_KEY:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        res = requests.get(url, params=params)
        if res.status_code == 200:
            data = res.json()
            return {
                "source": "OpenWeatherMap",
                "temp": data["main"]["temp"],
                "wind": data["wind"]["speed"],
                "condition": data["weather"][0]["description"]
            }

    # Fallback: Open-Meteo
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True}
    res = requests.get(url, params=params)

    if res.status_code == 200:
        w = res.json()["current_weather"]
        return {
            "source": "Open-Meteo",
            "temp": w["temperature"],
            "wind": w["windspeed"],
            "condition": "N/A"
        }

    return None


def display_weather(city):
    data = get_weather(city)
    if not data:
        return

    print(f"\nWeather in {city.title()} ({data['source']})")
    print("-" * 35)
    print("Temperature:", data["temp"], "°C")
    print("Wind Speed:", data["wind"], "km/h")
    print("Condition:", data["condition"])


# -------------------- AQI (LIVE + LAST 7 DAYS) --------------------
def display_aqi(city):
    city = city.lower().strip()

    if city not in CITIES:
        print("City not available!")
        return

    lat, lon = CITIES[city]

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5",
        "timezone": "auto",
        "past_days": 7
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Failed to fetch AQI data")
        return

    data = response.json()
    pm25_values = data["hourly"]["pm2_5"]

    # ✅ LIVE AQI = latest PM2.5 value
    live_pm25 = pm25_values[-1]

    # ---------------- AQI CLASSIFICATION ----------------
    if live_pm25 <= 12:
        category = "Good 😊"
        advice = "Air quality is satisfactory."
    elif live_pm25 <= 35.4:
        category = "Moderate 🙂"
        advice = "Sensitive people should limit outdoor activity."
    elif live_pm25 <= 55.4:
        category = "Unhealthy for Sensitive Groups 😷"
        advice = "Children & elderly should avoid prolonged outdoor exposure."
    elif live_pm25 <= 150.4:
        category = "Unhealthy 🚫"
        advice = "Everyone should reduce outdoor activities."
    elif live_pm25 <= 250.4:
        category = "Very Unhealthy ⚠️"
        advice = "Avoid outdoor activities."
    else:
        category = "Hazardous ☠️"
        advice = "Serious health risk. Stay indoors!"

    print(f"\n🌫️ LIVE AQI REPORT – {city.title()}")
    print("-" * 45)
    print(f"PM2.5 Value: {live_pm25:.2f} µg/m³")
    print(f"AQI Category: {category}")
    print(f"Health Advice: {advice}")

    # Optional: show last 7 days average
    avg_pm25 = sum(pm25_values) / len(pm25_values)
    print(f"\n7-Day Average PM2.5: {avg_pm25:.2f} µg/m³")
    print("Higher PM2.5 = Poor air quality")


# -------------------- CRYPTO --------------------
def get_crypto(coin):
    coin_id = CRYPTO_IDS.get(coin.lower(), coin)
    url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None


def display_crypto(coin):
    data = get_crypto(coin)
    if not data:
        print("Crypto not found")
        return

    usd = data["quotes"]["USD"]
    print(f"\n{data['name']} ({data['symbol']})")
    print("-" * 30)
    print("Price: $", round(usd["price"], 2))
    print("24h Change:", usd["percent_change_24h"], "%")


# -------------------- DASHBOARD --------------------
def dashboard():
    while True:
        print("\n=== REAL-WORLD API DASHBOARD ===")
        print("1. Check Weather")
        print("2. Check Crypto Price")
        print("3. Check AQI (Last 7 Days)")
        print("4. Save Weather + Crypto to JSON")
        print("5. Exit")

        choice = input("Choose (1-5): ").strip()

        if choice == "1":
            print("Cities:", ", ".join(CITIES.keys()))
            display_weather(input("Enter city: "))

        elif choice == "2":
            print("Cryptos:", ", ".join(CRYPTO_IDS.keys()))
            display_crypto(input("Enter crypto: "))

        elif choice == "3":
            print("Cities:", ", ".join(CITIES.keys()))
            display_aqi(input("Enter city: "))

        elif choice == "4":
            city = input("City: ")
            coin = input("Crypto: ")
            data = {
                "timestamp": datetime.now().isoformat(),
                "weather": get_weather(city),
                "crypto": get_crypto(coin)
            }
            with open("dashboard_data.json", "w") as f:
                json.dump(data, f, indent=2)
            print("Saved to dashboard_data.json")

        elif choice == "5":
            print("Goodbye 👋")
            break

        else:
            print("Invalid choice")


# -------------------- RUN --------------------
if __name__ == "__main__":
    dashboard()
