import os
import sys
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Ensure lib is in path if running directly (for testing)
if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib'))

try:
    from waveshare_epd import epd2in13_V4
except (ImportError, RuntimeError, Exception) as e:
    # Mock for testing on non-Pi systems or if driver fails to init
    print(f"Warning: waveshare_epd driver could not be loaded ({e}). Using mock.")
    class MockEPD:
        width = 122
        height = 250
        def init(self): pass
        def Clear(self, color): pass
        def display(self, image): pass
        def getbuffer(self, image): return []
        def sleep(self): pass
    
    class MockModule:
        EPD = MockEPD
    
    epd2in13_V4 = MockModule()

try:
    from src.icons import IconDrawer
except ImportError:
    from icons import IconDrawer

class DisplayService:
    def __init__(self):
        self.epd = epd2in13_V4.EPD()
        self.epd.init()
        self.epd.Clear(0xFF)
        # Use default font for simplicity
        self.font = ImageFont.load_default()
        # Try to load Montserrat fonts
        font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
        try:
            self.font_location = ImageFont.truetype(os.path.join(font_dir, "Montserrat-Bold.ttf"), 24)
            self.font_temp = ImageFont.truetype(os.path.join(font_dir, "Montserrat-Bold.ttf"), 36)
            self.font_detail = ImageFont.truetype(os.path.join(font_dir, "Montserrat-Regular.ttf"), 18)
            self.font_forecast = ImageFont.truetype(os.path.join(font_dir, "Montserrat-Bold.ttf"), 22)
        except IOError:
            self.font_location = ImageFont.load_default()
            self.font_temp = ImageFont.load_default()
            self.font_detail = ImageFont.load_default()
            self.font_forecast = ImageFont.load_default()

    def update_display(self, weather_data, location_name="Weather"):
        if not weather_data:
            return
        
        current = weather_data.get('current', {})
        daily = weather_data.get('daily', {})
        
        if not current:
            return

        # EPD_WIDTH = 122, EPD_HEIGHT = 250
        # Landscape mode: 250x122
        width = self.epd.height
        height = self.epd.width
        
        image = Image.new('1', (width, height), 255)
        draw = ImageDraw.Draw(image)
        
        # --- Current Weather ---
        # Icon
        icon_size = 50
        icon_x = 10
        icon_y = 10
        
        # Initialize icon drawer
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts', 'weathericons-regular-webfont.ttf')
        icon_drawer = IconDrawer(draw, font_path, icon_size)
        
        code = current.get('weathercode')
        is_day = current.get('is_day', 1)
        icon_drawer.draw_icon_for_code(code, icon_x, icon_y, icon_size, is_day)
        
        # Main Temp
        temp_c = current.get('temperature')
        # temp_f = (temp_c * 9/5) + 32
        temp_text = f"{int(temp_c)}°C"
        draw.text((70, 5), temp_text, font=self.font_temp, fill=0)
        
        # High / Low
        # daily_max/min are lists, get today's (index 0)
        daily_max = daily.get('temperature_2m_max', [0])
        daily_min = daily.get('temperature_2m_min', [0])
        high = daily_max[0] if daily_max else 0
        low = daily_min[0] if daily_min else 0
        
        # Using simple text arrows or H/L if font issues arise. 
        # Montserrat should support ↑ ↓.
        hl_text = f"↑{int(high)}° ↓{int(low)}°"
        draw.text((170, 15), hl_text, font=self.font_detail, fill=0)

        # Feels Like
        app_temp = current.get('apparent_temperature')
        feels_text = f"Feels: {int(app_temp)}°C"
        draw.text((70, 45), feels_text, font=self.font_detail, fill=0)
        
        # UV Index
        uv_max = daily.get('uv_index_max', [0])
        uv_val = uv_max[0] if uv_max else 0
        uv_text = f"UV: {uv_val}"
        draw.text((170, 45), uv_text, font=self.font_detail, fill=0)
        
        # Wind
        wind_kmh = current.get('windspeed')
        wind_dir = current.get('winddirection', 0)
        def get_cardinal(d):
            dirs = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            ix = round(d / (360. / len(dirs)))
            return dirs[ix % len(dirs)]
        wind_cardinal = get_cardinal(wind_dir)
        wind_text = f"Wind: {wind_kmh} km/h {wind_cardinal}"
        draw.text((70, 70), wind_text, font=self.font_detail, fill=0)

        # Severe Weather Alert
        is_severe = weather_data.get('severe_weather', False)
        if is_severe:
            # Draw a black bar at the bottom
            draw.rectangle((0, 95, width, height), fill=0)
            alert_text = "! SEVERE WEATHER IN 24H !"
            # Center the text
            bbox = draw.textbbox((0, 0), alert_text, font=self.font_forecast)
            w = bbox[2] - bbox[0]
            draw.text(((width - w) // 2, 98), alert_text, font=self.font_forecast, fill=1) # fill=1 for white text on black


        # Rotate image 180 degrees
        image = image.rotate(180)
        
        self.epd.display(self.epd.getbuffer(image))

    def clear(self):
        self.epd.Clear(0xFF)
        self.epd.sleep()

if __name__ == "__main__":
    ds = DisplayService()
    # Test data
    test_data = {
        'current': {
            'temperature': 20.5,
            'apparent_temperature': 18.0,
            'windspeed': 12.5,
            'winddirection': 180,
            'weathercode': 1,
            'is_day': 1
        },
        'daily': {
            'temperature_2m_max': [22.0],
            'temperature_2m_min': [15.0],
            'uv_index_max': [5.5],
            'weathercode': [1]
        },
        'severe_weather': True
    }
    ds.update_display(test_data)
