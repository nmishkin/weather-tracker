import argparse
import requests
import sys
from datetime import datetime

def get_coordinates(city_name):
    """
    Get coordinates for a city in Florida using Open-Meteo Geocoding API.
    """
    # Open-Meteo Geocoding API needs the name as a query parameter
    # We should search for the city name and then filter for Florida
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=en&format=json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            for result in data["results"]:
                # Check if it's in Florida
                if result.get("admin1") == "Florida" and result.get("country_code") == "US":
                    return result["latitude"], result["longitude"], result["name"]
        return None, None, None
    except Exception as e:
        print(f"Error geocoding {city_name}: {e}")
        return None, None, None

def get_weather_forecast(lat, lon):
    """
    Fetch 14-day forecast for given coordinates.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&temperature_unit=fahrenheit&forecast_days=14&timezone=auto"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def analyze_city(city_name, threshold):
    """
    Analyze weather for a city and return forecast if criteria are met.
    """
    lat, lon, resolved_name = get_coordinates(city_name)
    if lat is None:
        print(f"Skipping {city_name}: Could not resolve location.")
        return None

    weather_data = get_weather_forecast(lat, lon)
    if not weather_data or "daily" not in weather_data:
        print(f"Skipping {city_name}: Could not fetch weather data.")
        return None

    daily = weather_data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]

    # Check for at least three consecutive days with predicted high >= threshold
    consecutive_count = 0
    meets_criteria = False
    
    for temp in max_temps:
        if temp is not None and temp >= threshold:
            consecutive_count += 1
            if consecutive_count >= 3:
                meets_criteria = True
                break
        else:
            consecutive_count = 0

    if meets_criteria:
        forecast = []
        for i in range(len(dates)):
            date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
            day_of_week = date_obj.strftime("%a")
            forecast.append({
                "date": dates[i],
                "day": day_of_week,
                "high": max_temps[i],
                "low": min_temps[i]
            })
        return {
            "name": resolved_name,
            "forecast": forecast
        }
    return None

def main():
    parser = argparse.ArgumentParser(description="Florida Weather Tracker")
    parser.add_argument("threshold", type=int, help="Target high temperature threshold in Fahrenheit")
    parser.add_argument("cities", nargs="+", help="Names of cities in Florida")
    
    args = parser.parse_args()

    results = []
    for city in args.cities:
        analysis = analyze_city(city, args.threshold)
        if analysis:
            results.append(analysis)

    if not results:
        print(f"\nNo cities found with at least 3 consecutive days >= {args.threshold}°F.")
    else:
        for city_data in results:
            print(f"\n--- {city_data['name']} ---")
            print(f"Meets criteria: At least 3 consecutive days with high >= {args.threshold}°F")
            print(f"{'Date':<12} | {'Day':<4} | {'High':<6} | {'Low':<6} | {'Match?'}")
            print("-" * 47)
            for day in city_data["forecast"]:
                high_val = day['high']
                high = f"{int(round(high_val))}°F" if high_val is not None else "N/A"
                low_val = day['low']
                low = f"{int(round(low_val))}°F" if low_val is not None else "N/A"
                match = "*" if high_val is not None and high_val >= args.threshold else ""
                print(f"{day['date']:<12} | {day['day']:<4} | {high:<6} | {low:<6} | {match:<5}")

if __name__ == "__main__":
    main()
