from PIL import Image, ImageFont, ImageDraw

import font_fredoka_one
import datetime
import time
import math


class Terminal:
    header = '\033[95m'
    okblue = '\033[94m'
    okcyan = '\033[96m'
    okgreen = '\033[92m'
    warning = '\033[93m'
    fail = '\033[91m'
    end_colours = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

    @classmethod
    def warn(cls, message):
        print(f"{cls.warning}{message}{cls.end_colours}")

    @classmethod
    def error(cls, message):
        print(f"{cls.fail}{message}{cls.end_colours}")


class Inkra:
    def __init__(self, flip: bool = True, weather_enabled: bool = False, city: str = "Guildford", country: str = "GB"):
        inky_real = True
        try:
            # noinspection PyUnresolvedReferences
            from inky.auto import auto
            inky_display = auto(verbose=True)

        except RuntimeError as e:  # Linux
            Terminal.warn(
                f"Could not initialise display, if you're debugging you can ignore this, \nPrinting exception:\n{e}\n")
            from inky.mock import InkyMockPHATSSD1608
            inky_real = False
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        except ImportError as e:  # Windows
            Terminal.warn("\nMissing dependencies,"
                          "If you're on windows you can ignore this,"
                          f"printing exception:\n{e}\n")
            from inky.mock import InkyMockPHATSSD1608
            inky_real = False
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        inky_display.set_border(inky_display.BLACK)
        self.width = inky_display.width
        self.height = inky_display.height
        self.display = inky_display

        self.image = Image.new("P", (self.width, self.height), self.display.WHITE)
        self.flip = flip
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(font_fredoka_one.font, 18)
        with open("assets/banana.otf", "rb") as font:
            self.font = ImageFont.truetype(font, 14)

        self.margin = 10
        self.lineoffset = 53

        self.display_real = inky_real
        self.enable_weather = weather_enabled

        if self.enable_weather:
            try:
                from modules import weather
                self.weather_city = city
                self.weather_country = country
                weather = weather.Weather(city, country)
            except ModuleNotFoundError:
                Terminal.error("\nOne or more modules required for the weather module missing. "
                               "Disabling module")

                self.enable_weather = False

    def __battery_icon(self, charge: int):

        if charge < 0:
            raise AttributeError("Battery can not be less than 0%!")

        if charge <= 15:
            icon = Image.open('assets/battery15.png')
        elif charge < 30:
            icon = Image.open('assets/battery30.png')
        elif charge < 50:
            icon = Image.open('assets/battery50.png')
        elif charge < 70:
            icon = Image.open('assets/battery70.png')
        else:
            icon = Image.open('assets/battery100.png')
        self.icon = icon

    def generate_image(self, show_time=True, show_logo=True, show_bat_icon=True, draw_lines=True, charge=0):

        # Reset canvas
        self.image = None
        self.image = Image.new("P", (self.width, self.height), self.display.WHITE)
        self.draw = ImageDraw.Draw(self.image)

        message = f"battery is {charge}%"
        message_bbox = display.font.getbbox(message)
        message_width = message_bbox[2]
        message_height = message_bbox[3]

        message_coords = (
            (display.width / 2) - (message_width / 2),
            (display.height / 2) - (message_height / 2)
        )
        display.draw.text(message_coords, message, display.display.RED, display.font)

        if show_time:
            time = datetime.datetime.now().strftime('%H:%M')
            date = datetime.datetime.now().strftime('%d/%m')
            datesize = display.font.getbbox(date)[2]
            datepos = ((self.width - datesize - 5), 0)
            print(datesize)
            self.draw.text(
                datepos,
                date,
                self.display.RED,
                self.font
            )

            self.draw.text((5, 0), time, self.display.RED, self.font)

        if show_logo:
            logo = Image.open("assets/Cupra-Logo.png")
            logo_pos = (
                math.ceil((self.width / 2) - (logo.width / 2)),
                0
            )
            self.image.paste(logo, logo_pos)
        if show_bat_icon:
            self.__battery_icon(charge)
            bat_pos = (
                math.ceil((self.width / 2) - (self.icon.width / 2)),
                (self.height - self.icon.height)
            )
            self.image.paste(self.icon, bat_pos)
        if draw_lines:
            self.draw.line((self.lineoffset, 0, self.lineoffset, self.height), fill=self.display.BLACK, width=3)
            self.draw.line((self.width - self.lineoffset, 0, self.width - self.lineoffset, self.height),
                           fill=display.display.BLACK,
                           width=3)
        return self.image

    def push_image(self):
        if self.flip:
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        self.display.set_image(self.image)
        self.display.show()


display = Inkra(flip=True, weather_enabled=True)

battery = 45

while True:
    if battery == -1:
        time.sleep(30)
        exit(0)

    display.generate_image(show_logo=True, show_bat_icon=True, show_time=True, charge=battery, draw_lines=True)
    display.push_image()
    if display.display_real:
        time.sleep(30)
    else:
        time.sleep(1)
