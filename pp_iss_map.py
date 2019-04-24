import time
import math
import board
import displayio
from adafruit_pyportal import PyPortal
from adafruit_display_shapes.circle import Circle

#--| USER CONFIG |--------------------------
MARK_SIZE = 10           # marker radius
MARK_COLOR = 0xFF0000    # marker color
MARK_THICKNESS = 5       # marker thickness
UPDATE_RATE = 10         # update rate in seconds
#-------------------------------------------

DATA_SOURCE = "http://api.open-notify.org/iss-now.json"
DATA_LOCATION = ["iss_position"]

WIDTH = board.DISPLAY.width
HEIGHT = board.DISPLAY.height

# determine the current working directory needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
default_bg=cwd+"/map.bmp")

# Connect to the internet and get local time
pyportal.get_local_time()

# ISS location indicator
#iss_location = Circle(0, 0, MARK_SIZE, outline=MARK_COLOR)
marker = displayio.Group(max_size=MARK_THICKNESS)
for r in range(MARK_SIZE, MARK_SIZE - MARK_THICKNESS, -1):
    marker.append(Circle(0, 0, r, outline=MARK_COLOR))
pyportal.splash.append(marker)

def get_location(width=WIDTH, height=HEIGHT):
    """Fetch current lat/lon, convert to (x, y) tuple scaled to width/height."""

    # Get location
    location = pyportal.fetch()

    # Compute (x, y) coordinates
    lat = float(location["latitude"])   # degrees, 0 to 180
    lon = float(location["longitude"])  # degrees, -180 to 180

    # Mercator projection math
    # https://stackoverflow.com/a/14457180
    x = lon + 180
    x = width * x / 360

    y = math.radians(lat)
    y = math.tan(math.pi / 4 + y / 2)
    y = math.log(y)
    y = (width * y) / (2 * math.pi)
    y = height / 2 - y

    return int(x), int(y)

while True:
    x, y = get_location()
    print(x, y)
    marker.x = x - MARK_SIZE
    marker.y = y - MARK_SIZE
    board.DISPLAY.refresh_soon()
    time.sleep(UPDATE_RATE)
