from PIL import Image, ImageFont, ImageDraw

import font_fredoka_one
import datetime
import time
import math
import yaml
import os

# Terminal interface
from interface.terminal import Terminal


class Inkra:
    def __init__(self, options: dict, city: str = "Guildford", country: str = "GB"):
        self.debug = False

        # Load config and set display options
        if os.path.exists("config.yml"):
            with open("config.yml", "r") as config_file:
                config = yaml.safe_load(config_file)
        else:
            Terminal.fatal("Missing config.yml, please create file.")
        self.options = config["Options"]
        self.flip = self.options["FlipScreen"]
        self.enable_weather = self.options["ShowWeather"]

        try:
            # Try to initialize our display,
            # if it fails, we fall back to a mock display from the Inky library

            # noinspection PyUnresolvedReferences
            from inky.auto import auto
            inky_display = auto(verbose=True)

        except RuntimeError as e:  # Linux
            self.debug = True
            Terminal.warn(
                "Could not initialise display, if you're debugging you can ignore this,\n"
                "Printing exception:\n"
                f"{Terminal.underline}{e}\n")
            from inky.mock import InkyMockPHATSSD1608
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        except ImportError as e:  # Windows
            self.debug = True
            Terminal.warn("\nMissing dependencies,"
                          "If you're on windows you can ignore this,"
                          f"printing exception:\n{Terminal.underline}{e}\n")
            from inky.mock import InkyMockPHATSSD1608
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        inky_display.set_border(inky_display.BLACK)

        self.height = inky_display.height
        self.display = inky_display

        self.image = Image.new("P", (self.display.width, self.height), self.display.WHITE)
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(font_fredoka_one.font, 18)
        with open("assets/banana.otf", "rb") as font:
            self.font = ImageFont.truetype(font, 14)

        self.margin = 10
        self.line_offset = 53

        from interface import cupra
        self.cupra = cupra.Cupra()
        if self.enable_weather:
            try:
                from interface import weather
                self.weather = weather.Weather(city, country)
            except ModuleNotFoundError:
                Terminal.error("\nOne or more modules required for the weather interface missing.\n"
                               "Disabling module")
                self.enable_weather = False
            except RuntimeError:
                Terminal.error("Weather interface failed to init, disabling.")

    def __battery_icon(self, charge: int):

        if charge < 0:
            raise AttributeError("Battery can not be less than 0%!")
        elif charge <= 15:
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

    def __draw_time(self):
        time_now = datetime.datetime.now().strftime('%H:%M')
        date = datetime.datetime.now().strftime('%d/%m')

        time_size = self.font.getbbox(time_now)
        # date_size = self.font.getbbox(date)
        self.draw.text(
            (9, (time_size[3] + 5)),
            date,
            self.display.RED,
            self.font
        )
        # 9 is chosen as the x because
        # line-offset/2 = 26.5px
        # length of date or time = 17.5px
        # 26.5 - 17.5 = 9px putting them in the centre
        self.draw.text((9, 0), time_now, self.display.RED, self.font)

    def generate_image(self, charge=0):

        # Reset canvas
        self.image = None
        self.image = Image.new("P", (self.display.width, self.height), self.display.WHITE)
        self.draw = ImageDraw.Draw(self.image)

        message = f"battery is {charge}%"
        message_bbox = self.font.getbbox(message)
        message_width = message_bbox[2]
        message_height = message_bbox[3]

        message_coords = (
            (self.display.width / 2) - (message_width / 2),
            (self.height / 2) - (message_height / 2)
        )
        self.draw.text(message_coords, message, self.display.RED, self.font)

        if self.options["ShowTime"]:
            self.__draw_time()

        if self.options["ShowLogo"]:
            logo = Image.open("assets/Cupra-Logo.png")
            logo_pos = (
                math.ceil((self.display.width / 2) - (logo.width / 2)),
                0
            )
            self.image.paste(logo, logo_pos)

        if self.options["ShowBatteryIcon"]:
            self.__battery_icon(charge)
            bat_pos = (
                math.ceil((self.display.width / 2) - (self.icon.width / 2)),
                (self.height - self.icon.height)
            )
            self.image.paste(self.icon, bat_pos)
        if self.options["DrawLines"]:
            self.draw.line((self.line_offset, 0, self.line_offset, self.height), fill=self.display.BLACK, width=3)
            self.draw.line(
                (self.display.width - self.line_offset, 0, self.display.width - self.line_offset, self.height),
                fill=self.display.BLACK,
                width=3)
        if self.options["ShowWeather"]:
            weather = self.weather.get_weather()
            self.image.paste(weather["icon"], (self.display.width - weather["icon"].width, 0))
            icon_box = (weather["icon"].width, weather["icon"].height)
            temperature_pos = (
                # math.floor(
                (self.display.width - icon_box[0]),
                5 + icon_box[1])
            Terminal.debug(temperature_pos)
            self.draw.text(temperature_pos, weather["temperature"], self.display.RED, self.font)

        return self.image

    def push_image(self):
        if self.flip:
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        self.display.set_image(self.image)

        self.display.show()


def main():
    display_options = {
        "flip": True,
        "show_logo": True,
        "show_battery_icon": True,
        "show_time": True,
        "show_weather": True,
        "draw_lines": True,
    }
    display = Inkra(options=display_options)

    battery = 10

    while True:
        if battery == -1:
            time.sleep(30)
            exit(0)

        display.generate_image(charge=battery)

        try:
            display.push_image()
        except RuntimeError:
            break

        if not display.debug:
            time.sleep(30)
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()
