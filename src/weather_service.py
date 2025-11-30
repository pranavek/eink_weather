import requests

class WeatherService:
    def __init__(self, lat=40.7128, lon=-74.0060): # Default to New York
        self.lat = lat
        self.lon = lon
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    def get_current_weather(self, lat=None, lon=None):
        params = {
            "latitude": lat if lat is not None else self.lat,
            "longitude": lon if lon is not None else self.lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m",
            "daily": "weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset,uv_index_max",
            "hourly": "weather_code",
            "timezone": "auto",
            "forecast_days": 2 # We only need today and tomorrow for 24h check
        }
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Transform to match expected format
            current_data = data.get("current", {})
            daily_data = data.get("daily", {})
            hourly_data = data.get("hourly", {})
            
            # Check for severe weather in next 24 hours
            # Severe codes: 95, 96, 99 (Thunderstorm), 65 (Heavy Rain), 75 (Heavy Snow)
            severe_codes = [65, 75, 95, 96, 99]
            severe_weather = False
            if hourly_data and "weather_code" in hourly_data:
                # Get current hour index (approximate)
                # API returns time in ISO8601, but lists are aligned with time.
                # We can just check the first 24 entries if we assume the response starts from now or 00:00 today.
                # OpenMeteo hourly usually starts at 00:00 of the current day.
                # We should find the index of the current hour.
                current_time_str = current_data.get("time") # "2023-10-27T10:00"
                try:
                    # Simple string matching to find start index
                    start_idx = 0
                    if current_time_str in hourly_data["time"]:
                        start_idx = hourly_data["time"].index(current_time_str)
                    
                    # Check next 24 hours
                    next_24_codes = hourly_data["weather_code"][start_idx:start_idx+24]
                    if any(code in severe_codes for code in next_24_codes):
                        severe_weather = True
                except ValueError:
                    pass # Fallback to False if time parsing fails

            return {
                "current": {
                    "temperature": current_data.get("temperature_2m"),
                    "apparent_temperature": current_data.get("apparent_temperature"),
                    "windspeed": current_data.get("wind_speed_10m"),
                    "winddirection": current_data.get("wind_direction_10m"),
                    "weathercode": current_data.get("weather_code"),
                    "is_day": 1 if current_data.get("is_day") else 0,
                    "time": current_data.get("time")
                },
                "daily": {
                    "temperature_2m_max": daily_data.get("temperature_2m_max", []),
                    "temperature_2m_min": daily_data.get("temperature_2m_min", []),
                    "uv_index_max": daily_data.get("uv_index_max", []),
                    "weathercode": daily_data.get("weathercode", [])
                },
                "severe_weather": severe_weather
            }
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None

if __name__ == "__main__":
    ws = WeatherService()
    print(ws.get_current_weather())
