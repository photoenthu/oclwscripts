#!/usr/bin/env python3
"""Air quality skill for zip code 33558 (Lutz/Odessa, FL).

Fetches current US AQI data from the Open-Meteo Air Quality API (no API key required).
"""

import json
import sys
import urllib.request

# Zip code 33558 coordinates (Lutz/Odessa, FL)
LATITUDE = 28.1758
LONGITUDE = -82.5762
ZIP_CODE = "33558"
TIMEZONE = "America/New_York"

AQI_CATEGORIES = [
    (50, "Good", "Air quality is satisfactory with little or no risk."),
    (100, "Moderate", "Acceptable; moderate health concern for sensitive individuals."),
    (150, "Unhealthy for Sensitive Groups", "Sensitive groups may experience health effects."),
    (200, "Unhealthy", "Everyone may begin to experience health effects."),
    (300, "Very Unhealthy", "Health alert: everyone may experience serious effects."),
    (500, "Hazardous", "Health emergency: the entire population is affected."),
]


def get_aqi_category(aqi):
    for threshold, label, description in AQI_CATEGORIES:
        if aqi <= threshold:
            return label, description
    return "Hazardous", "Health emergency: the entire population is affected."


def fetch_air_quality():
    params = (
        f"latitude={LATITUDE}&longitude={LONGITUDE}"
        f"&current=us_aqi,us_aqi_pm2_5,us_aqi_pm10,us_aqi_ozone,"
        f"us_aqi_nitrogen_dioxide,us_aqi_sulphur_dioxide,us_aqi_carbon_monoxide,"
        f"pm2_5,pm10,ozone"
        f"&timezone={TIMEZONE}"
    )
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?{params}"

    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def display_report(data):
    current = data["current"]
    aqi = current["us_aqi"]
    category, description = get_aqi_category(aqi)

    print(f"{'=' * 50}")
    print(f"  Air Quality Report — Zip Code {ZIP_CODE}")
    print(f"  (Lutz / Odessa, FL)")
    print(f"{'=' * 50}")
    print(f"  Time:      {current['time']} ({TIMEZONE})")
    print(f"  US AQI:    {aqi} — {category}")
    print(f"  Status:    {description}")
    print(f"{'-' * 50}")
    print(f"  Pollutant Breakdown (US AQI):")
    print(f"    PM2.5:            {current['us_aqi_pm2_5']:>4}  ({current['pm2_5']} µg/m³)")
    print(f"    PM10:             {current['us_aqi_pm10']:>4}  ({current['pm10']} µg/m³)")
    print(f"    Ozone:            {current['us_aqi_ozone']:>4}  ({current['ozone']} µg/m³)")
    print(f"    Nitrogen Dioxide: {current['us_aqi_nitrogen_dioxide']:>4}")
    print(f"    Sulphur Dioxide:  {current['us_aqi_sulphur_dioxide']:>4}")
    print(f"    Carbon Monoxide:  {current['us_aqi_carbon_monoxide']:>4}")
    print(f"{'=' * 50}")

    if "--json" in sys.argv:
        print("\nRaw JSON:")
        print(json.dumps(data, indent=2))


def main():
    try:
        data = fetch_air_quality()
        display_report(data)
    except urllib.error.URLError as e:
        print(f"Error: Could not reach air quality API — {e}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error: Unexpected API response — {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
