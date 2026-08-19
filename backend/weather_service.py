import requests
import time

# Simple in-memory cache to prevent exceeding free-tier limits
WEATHER_CACHE = {}

def get_weather_data(lat: float, lon: float):
    """
    Fetch current weather and 5-day forecast from Open-Meteo API for given lat, lon.
    Also reverse geocode location using OpenStreetMap Nominatim API.
    """
    cache_key = f"{round(lat, 2)}_{round(lon, 2)}"
    now = time.time()
    
    # Return cache if valid (10 min TTL)
    if cache_key in WEATHER_CACHE:
        cached_time, cached_data = WEATHER_CACHE[cache_key]
        if now - cached_time < 600:
            return cached_data
            
    try:
        # Open-Meteo Weather API (No key required)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,relative_humidity_2m_mean&timezone=auto"
        res = requests.get(weather_url, timeout=5)
        res_data = res.json()
        
        current = res_data.get("current_weather", {})
        daily = res_data.get("daily", {})
        
        temp = current.get("temperature", 25.0)
        # Average relative humidity from forecast or fallback
        humidity_list = daily.get("relative_humidity_2m_mean", [65.0])
        humidity = humidity_list[0] if humidity_list else 65.0
        
        # Estimate annual or seasonal rainfall equivalent from 5-day sum or average
        precip_list = daily.get("precipitation_sum", [5.0])
        recent_rain = sum(precip_list) if precip_list else 10.0
        # Scaled seasonal rainfall approximation for India (in mm)
        estimated_seasonal_rainfall = max(40.0, min(350.0, recent_rain * 15.0 + 80.0))
        
        # Reverse geocoding via Nominatim
        location_name = get_location_name(lat, lon)
        
        result = {
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(estimated_seasonal_rainfall, 1),
            "windspeed": current.get("windspeed", 10.0),
            "weathercode": current.get("weathercode", 0),
            "location_name": location_name,
            "forecast": [
                {
                    "date": daily.get("time", ["Today"])[i] if i < len(daily.get("time", [])) else f"Day {i+1}",
                    "max_temp": daily.get("temperature_2m_max", [temp])[i] if i < len(daily.get("temperature_2m_max", [])) else temp,
                    "min_temp": daily.get("temperature_2m_min", [temp-5])[i] if i < len(daily.get("temperature_2m_min", [])) else temp-5,
                    "precip": daily.get("precipitation_sum", [0])[i] if i < len(daily.get("precipitation_sum", [])) else 0
                }
                for i in range(min(5, len(daily.get("time", []))))
            ]
        }
        
        WEATHER_CACHE[cache_key] = (now, result)
        return result
    except Exception as e:
        print(f"Weather API error: {e}")
        # Fallback realistic weather data for India
        return {
            "temperature": 26.5,
            "humidity": 65.0,
            "rainfall": 120.0,
            "windspeed": 12.0,
            "weathercode": 1,
            "location_name": f"Location ({lat:.2f}, {lon:.2f})",
            "forecast": [
                {"date": "Day 1", "max_temp": 30.0, "min_temp": 21.0, "precip": 2.0},
                {"date": "Day 2", "max_temp": 31.5, "min_temp": 22.0, "precip": 5.0},
                {"date": "Day 3", "max_temp": 29.0, "min_temp": 20.5, "precip": 12.0},
                {"date": "Day 4", "max_temp": 28.5, "min_temp": 19.5, "precip": 0.0},
                {"date": "Day 5", "max_temp": 30.0, "min_temp": 21.0, "precip": 1.0}
            ]
        }

def get_location_name(lat: float, lon: float) -> str:
    """Reverse geocode using OpenStreetMap Nominatim API"""
    try:
        headers = {'User-Agent': 'FarmerCropAdvisoryPlatform/1.0'}
        geo_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10"
        res = requests.get(geo_url, headers=headers, timeout=4)
        data = res.json()
        address = data.get("address", {})
        
        district = address.get("state_district") or address.get("county") or address.get("city") or address.get("town")
        state = address.get("state", "")
        country = address.get("country", "")
        
        parts = [p for p in [district, state, country] if p]
        return ", ".join(parts) if parts else f"Lat: {lat:.2f}, Lon: {lon:.2f}"
    except Exception:
        return f"Location ({lat:.2f}, {lon:.2f})"
