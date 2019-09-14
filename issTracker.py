import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import os
import json
import spidev
import requests
import logging
from datetime import datetime, date
from abc import ABC, abstractmethod
from threading import Thread
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

class Board:
    def __init__(self, btnPin, btnUp, btnDown):
        self.btnPin = btnPin
        self.btnUp = btnUp
        self.btnDown = btnDown

    def init(self):
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # Setting up button 
        GPIO.setup(self.btnPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Setting up Up button
        GPIO.setup(self.btnUp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Setting up Down button
        GPIO.setup(self.btnDown, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def is_button_pressed(self):
        return GPIO.input(self.btnPin) == GPIO.LOW

    def is_upbutton_pressed(self):
        return GPIO.input(self.btnUp) == GPIO.LOW

    def is_downbutton_pressed(self):
        return GPIO.input(self.btnDown) == GPIO.LOW

            
class Display:
    def __init__(self):
        self.init()

    def init(self):
        # Create the I2C interface.
        i2c = busio.I2C(SCL, SDA)

        self.disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

        # Clear display.
        self.disp.fill(0)
        self.disp.show()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))
        
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)
 
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        self.padding = -1
        self.top = self.padding
        self.bottom = self.height - self.padding

    def text(self, line, text, selected = False, center = False):
        fill = "white"
        x = 0
        font = ImageFont.load_default()

        if center:
            text = (" "*(int)((20- len(text))/2)) + text

        y = self.top + (line * 8)
        if selected:
            fill = "black"
            self.draw.rectangle((0, y + 2, self.width, y + 10), outline=0, fill=255)
            
        self.draw.text((x, y), str(text) , font=font, fill=fill)
        

    def clear(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        
        
    def show(self):
        # Display image.
        self.disp.image(self.image)
        self.disp.show()
    
class ISS:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.people = []
        self.times = []

    def track(self):
        self.get_pass_time(35.216087, -80.853537)
        self.get_current_location()
        self.get_people()
        #self.people = ["Juan", "Alberto", "Pepe", "Ramon", "Luis", "Julio", "Fabio"]

    def try_fetch_data(self, url):
        response = requests.get(url)

        return json.loads(response.content.decode('utf-8'))


    def get_current_location(self):
        obj = self.try_fetch_data("http://api.open-notify.org/iss-now.json")

        self.latitude = obj['iss_position']['latitude']
        self.longitude = obj['iss_position']['longitude']

    def get_pass_time(self, lat, long):
        obj = self.try_fetch_data("http://api.open-notify.org/iss-pass.json?lat=%s&lon=%s" % (lat, long))

        if obj:
            times = obj['response']

            self.times = [datetime.fromtimestamp(time['risetime']) for time in times]
        else:
            self.times = []

    def get_people(self):
        obj = self.try_fetch_data("http://api.open-notify.org/astros.json")

        if obj:
            people = obj['people']

            self.people = [person['name'] for person in people]
            

class ScreenLine:
    def __init__(self, text):
        self.text = text
        self.selected = False

    def select(self):
        self.selected = True

    def deSelect(self):
        self.selected = False

    def toggle(self):
        self.selected = not self.selected
        
class Screen(ABC):
    def __init__(self, name):
        self.name = name
        self.lines = None
       
    def paint(self, screen, iss_information):
        pass

    def on_up(self):
        pass

    def on_down(self):
        pass

    def on_click(self):
        pass


class MainMenuScreen(Screen):
    def __init__(self):
        Screen.__init__(self, "Main Menu")
        
        lines = [
            ScreenLine("Summary"),
            ScreenLine("People"),
            ScreenLine("Times")
            ]
        
        self.lines = lines
        self.selectedLine = 0

    def paint(self, display, iss):
        display.text(0, self.name, center = True)
        for index in range(0, len(self.lines)):
            if index == self.selectedLine:
                display.text(index+1, self.lines[index].text, selected = True)
            else:  
                display.text(index+1, self.lines[index].text)

    def on_up(self):
        self.selectedLine = (self.selectedLine - 1) % 3
        return self

    def on_down(self):
        self.selectedLine = (self.selectedLine + 1) % 3
        return self
    
    def on_click(self):
        if self.selectedLine == 0:
            return SummaryScreen()
        elif self.selectedLine == 1:
            return PeopleScreen()
        else:
            return TimesScreen()


class SummaryScreen(Screen):
    def __init__(self):
        Screen.__init__(self, "Summary")
                
    def paint(self, display, iss):
        display.text(0, self.name, center = True)
        display.text(1, "lt:" + str(iss.latitude))
        display.text(2, "ln:" + str(iss.longitude))

        if len(iss.times) > 0:
            display.text(3, iss.times[0].strftime('%Y-%m-%d %H:%M:%S'), center = True)
    
    def on_click(self):
        return MainMenuScreen()
    
class PeopleScreen(Screen):
    def __init__(self):
        Screen.__init__(self, "People")
        self.selectedItem = 0;
        self.list_base = 0

    def on_up(self):
        self.selectedItem = (self.selectedItem - 1) 
        return self

    def on_down(self):
        self.selectedItem = (self.selectedItem + 1)
        return self
    
    def paint(self, display, iss):
            display.text(0, self.name, center = True)

            if self.selectedItem < 0:
                self.list_base = len(iss.people) - (len(iss.people)%3)
                self.selectedItem = len(iss.people) - 1
            elif self.selectedItem >= (self.list_base + 3):
                self.list_base += 3
            elif self.selectedItem >= len(iss.people):
                self.list_base = 0
                self.selectedItem = 0
            elif self.selectedItem < self.list_base:
                self.list_base -= 3

            for index in range (self.list_base, self.list_base + 3):
                if index < len(iss.people):
                    line = (index - self.list_base) + 1
                    if index == self.selectedItem:
                        display.text(line, iss.people[index], selected = True)
                    else:
                        display.text(line, iss.people[index])

               
    def on_click(self):
        return MainMenuScreen()

class TimesScreen(Screen):
    def __init__(self):
        Screen.__init__(self, "Times")
        self.selectedItem = 0;
        self.list_base = 0

    def on_up(self):
        self.selectedItem = (self.selectedItem - 1) 
        return self

    def on_down(self):
        self.selectedItem = (self.selectedItem + 1)
        return self
    
    def paint(self, display, iss):
            display.text(0, self.name, center = True)

            if self.selectedItem < 0:
                self.list_base = len(iss.times) - (len(iss.times)%3)
                self.selectedItem = len(iss.times) - 1
            elif self.selectedItem >= (self.list_base + 3):
                self.list_base += 3
            elif self.selectedItem >= len(iss.times):
                self.list_base = 0
                self.selectedItem = 0
            elif self.selectedItem < self.list_base:
                self.list_base -= 3

            for index in range (self.list_base, self.list_base + 3):
                if index < len(iss.times):
                    line = (index - self.list_base) + 1
                    if index == self.selectedItem:
                        display.text(line, iss.times[index], selected = True)
                    else:
                        display.text(line, iss.times[index])

               
    def on_click(self):
        return MainMenuScreen()
    
class IssTracker:
    def __init__(self):
        self.current = SummaryScreen()
        self.display = Display()
        self.iss = ISS()
        self.board = Board(5, 25, 6) 
        
        
    def init(self):
        # Tracking ISS data every 5 seconds
        thread = Thread(target = self.track)
        thread.start()

        self.board.init()
        self.loop()

    def track(self):
        while True:
            self.iss.track()
            time.sleep(5)
            
    def loop(self):
        while True:
            self.display.clear()
            self.current.paint(self.display, self.iss)
            self.display.show()
            
            if self.board.is_button_pressed():
                self.current = self.current.on_click()

            if self.board.is_upbutton_pressed():
                self.current = self.current.on_up()

            if self.board.is_downbutton_pressed():
                self.current = self.current.on_down()
            pass

if __name__ == "__main__":
    tracker = IssTracker()
    tracker.init()
    tracker.loop()
