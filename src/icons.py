from PIL import ImageDraw, ImageFont

class IconDrawer:
    """Weather icon renderer using weather-icons font."""
    
    # Mapping of WMO weather codes to weather-icons unicode characters
    # Reference: https://erikflowers.github.io/weather-icons/
    WMO_TO_ICON = {
        # Clear sky
        0: {'day': '\uf00d', 'night': '\uf02e'},  # day-sunny / night-clear
        
        # Mainly clear
        1: {'day': '\uf00c', 'night': '\uf086'},  # day-cloudy / night-alt-cloudy
        
        # Partly cloudy
        2: {'day': '\uf002', 'night': '\uf086'},  # day-cloudy / night-alt-cloudy
        
        # Overcast
        3: {'day': '\uf013', 'night': '\uf013'},  # cloudy / cloudy
        
        # Fog
        45: {'day': '\uf014', 'night': '\uf014'},  # fog / fog
        48: {'day': '\uf014', 'night': '\uf014'},  # fog / fog
        
        # Drizzle
        51: {'day': '\uf01c', 'night': '\uf01c'},  # sprinkle / sprinkle
        53: {'day': '\uf01c', 'night': '\uf01c'},  # sprinkle / sprinkle
        55: {'day': '\uf01c', 'night': '\uf01c'},  # sprinkle / sprinkle
        56: {'day': '\uf01c', 'night': '\uf01c'},  # sprinkle / sprinkle (freezing)
        57: {'day': '\uf01c', 'night': '\uf01c'},  # sprinkle / sprinkle (freezing)
        
        # Rain
        61: {'day': '\uf019', 'night': '\uf019'},  # rain / rain
        63: {'day': '\uf019', 'night': '\uf019'},  # rain / rain
        65: {'day': '\uf019', 'night': '\uf019'},  # rain / rain
        66: {'day': '\uf019', 'night': '\uf019'},  # rain / rain (freezing)
        67: {'day': '\uf019', 'night': '\uf019'},  # rain / rain (freezing)
        
        # Snow
        71: {'day': '\uf01b', 'night': '\uf01b'},  # snow / snow
        73: {'day': '\uf01b', 'night': '\uf01b'},  # snow / snow
        75: {'day': '\uf01b', 'night': '\uf01b'},  # snow / snow
        77: {'day': '\uf01b', 'night': '\uf01b'},  # snow / snow (grains)
        85: {'day': '\uf01b', 'night': '\uf01b'},  # snow / snow (showers)
        86: {'day': '\uf01b', 'night': '\uf01b'},  # snow / snow (showers)
        
        # Rain showers
        80: {'day': '\uf009', 'night': '\uf029'},  # day-showers / night-alt-showers
        81: {'day': '\uf009', 'night': '\uf029'},  # day-showers / night-alt-showers
        82: {'day': '\uf009', 'night': '\uf029'},  # day-showers / night-alt-showers
        
        # Thunderstorm
        95: {'day': '\uf010', 'night': '\uf010'},  # thunderstorm / thunderstorm
        96: {'day': '\uf010', 'night': '\uf010'},  # thunderstorm / thunderstorm (with hail)
        99: {'day': '\uf010', 'night': '\uf010'},  # thunderstorm / thunderstorm (with hail)
    }
    
    def __init__(self, draw: ImageDraw.ImageDraw, font_path: str, font_size: int = 35):
        """Initialize the icon drawer with weather-icons font.
        
        Args:
            draw: PIL ImageDraw object
            font_path: Path to weathericons-regular-webfont.ttf
            font_size: Size of the weather icon font
        """
        self.draw = draw
        try:
            self.icon_font = ImageFont.truetype(font_path, font_size)
        except IOError:
            # Fallback to default font if weather icons font not found
            print(f"Warning: Could not load weather icons font from {font_path}")
            self.icon_font = ImageFont.load_default()
    
    def get_icon_char(self, code, is_day=1):
        """Get the weather icon unicode character for a given WMO code.
        
        Args:
            code: WMO weather code
            is_day: 1 for day, 0 for night
            
        Returns:
            Unicode character for the weather icon
        """
        time_of_day = 'day' if is_day else 'night'
        
        if code in self.WMO_TO_ICON:
            return self.WMO_TO_ICON[code][time_of_day]
        else:
            # Default to cloudy icon
            return '\uf013'
    
    def draw_icon_for_code(self, code, x, y, size, is_day=1):
        """Draw weather icon for the given WMO code.
        
        Args:
            code: WMO weather code
            x, y: Position to draw the icon
            size: Icon size (used to create appropriately sized font)
            is_day: 1 for day, 0 for night
        """
        # Get the icon character
        icon_char = self.get_icon_char(code, is_day)
        
        # Create font with the requested size
        try:
            sized_font = ImageFont.truetype(self.icon_font.path, size)
        except (AttributeError, IOError):
            sized_font = self.icon_font
        
        # Draw the icon
        self.draw.text((x, y), icon_char, font=sized_font, fill=0)
