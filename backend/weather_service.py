import requests
from datetime import datetime

def get_coordinates(city_name):
    """
    Get coordinates for a city in Florida using Open-Meteo Geocoding API.
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=10&language=en&format=json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data:
            for result in data["results"]:
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

def analyze_city(city_name, threshold, consecutive_days=3):
    """
    Analyze weather for a city and return forecast if criteria are met.
    """
    lat, lon, resolved_name = get_coordinates(city_name)
    if lat is None:
        return {"error": f"Could not resolve location for {city_name}"}

    weather_data = get_weather_forecast(lat, lon)
    if not weather_data or "daily" not in weather_data:
        return {"error": f"Could not fetch weather data for {city_name}"}

    daily = weather_data["daily"]
    dates = daily["time"]
    max_temps = daily["temperature_2m_max"]
    min_temps = daily["temperature_2m_min"]

    # Check for at least N consecutive days with predicted high >= threshold
    consecutive_count = 0
    meets_criteria = False
    
    for temp in max_temps:
        if temp is not None and temp >= threshold:
            consecutive_count += 1
            if consecutive_count >= consecutive_days:
                meets_criteria = True
                break
        else:
            consecutive_count = 0

    forecast = []
    for i in range(len(dates)):
        date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
        day_of_week = date_obj.strftime("%a")
        forecast.append({
            "date": dates[i],
            "day": day_of_week,
            "high": int(round(max_temps[i])) if max_temps[i] is not None else None,
            "low": int(round(min_temps[i])) if min_temps[i] is not None else None,
            "is_match": max_temps[i] >= threshold if max_temps[i] is not None else False
        })
        
    return {
        "name": resolved_name,
        "meets_criteria": meets_criteria,
        "forecast": forecast
    }
