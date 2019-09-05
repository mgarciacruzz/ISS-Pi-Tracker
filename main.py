import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import json
import requests
import logging
from datetime import datetime, date


def try_fetch_data(url):
    response = requests.get(url)

    obj = json.loads(response.content.decode('utf-8'))

    return obj


def get_pass_time(lat, long):
    obj = try_fetch_data("http://api.open-notify.org/iss-pass.json?lat=%s&lon=%s" % (lat, long))

    if obj:
        times = obj['response']

        return datetime.fromtimestamp(times[0]['risetime'])
    return None           

def get_current_location():
    obj = try_fetch_data("http://api.open-notify.org/iss-now.json")

    latitude = obj['iss_position']['latitude']
    longitude = obj['iss_position']['longitude']

    return latitude,longitude


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)
 
# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)
 
# Clear display.
disp.fill(0)
disp.show()
 
# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
 
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
 
# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)
 
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
#padding = -2
padding = -1
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
 
 
# Load default font.
font = ImageFont.load_default()
logReported = False;
logging.basicConfig(filename="issTracker.log", level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.info("ISS Tracker started!")
while True:
 
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    latitude, longitude = get_current_location()
    # Write four lines of text.

    nextDate = get_pass_time(35.216087, -80.853537)

    today = datetime.now()
    delta = abs (nextDate - today).total_seconds()

    if delta > 300:
        logReported = False;
        draw.text((x, top+0), "  ISS Tracker ", font=font, fill=255)
        draw.text((x, top+8), "lat:" + str(latitude) , font=font, fill=255)
        draw.text((x, top+16), "ln:" + str(longitude) , font=font, fill=255)
        draw.text((x, top+24), nextDate.strftime('%Y-%m-%d %H:%M:%S') , font=font, fill=255)

    else:
        if not logReported:
            logging.info("ISS will pass around " + nextDate.strftime('%Y-%m-%d %H:%M:%S'))
            logReported = True
            
        draw.text((x, top+8), '   PASSING SOON!' , font=font, fill=255)
        draw.text((x, top+24), nextDate.strftime('%Y-%m-%d %H:%M:%S') , font=font, fill=255)

 
    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(5)


def get_crew_members():
    obj = try_fetch_data("http://api.open-notify.org/astros.json")

    if obj:
        people = obj['people']

        print("People in the ISS:")

        for key, group in itertools.groupby(people, key=lambda x: x['craft']):
            print('CRAFT: %s' % key)
            for person in list(group):
                print("- %s " % person['name'])

