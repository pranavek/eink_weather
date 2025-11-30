import sys
import os
import time
import logging

# Add lib to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))

try:
    from src.weather_service import WeatherService
    from src.display_service import DisplayService
except ImportError:
    from weather_service import WeatherService
    from display_service import DisplayService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Weather Display...")
    weather_service = WeatherService()
    display_service = DisplayService()

    locations = [
        {"name": "Birmingham, AL", "lat": 33.5186, "lon": -86.8104},
        #{"name": "Calicut, Kerala", "lat": 11.2588, "lon": 75.7804}
    ]
    current_location_index = 0

    try:
        while True:
            location = locations[current_location_index]
            logger.info(f"Fetching weather data for {location['name']}...")
            weather = weather_service.get_current_weather(lat=location['lat'], lon=location['lon'])
            
            if weather:
                logger.info(f"Weather fetched: {weather}")
                logger.info("Updating display...")
                display_service.update_display(weather, location_name=location['name'])
            else:
                logger.error("Failed to fetch weather data")

            # Cycle to next location
            current_location_index = (current_location_index + 1) % len(locations)

            # Sleep for 60 minutes
            logger.info("Sleeping for 60 minutes...")
            time.sleep(60 * 60) 
            
    except KeyboardInterrupt:
        logger.info("Exiting...")
        display_service.clear()
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        display_service.clear()

if __name__ == "__main__":
    main()
