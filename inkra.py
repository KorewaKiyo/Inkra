import logging
import datetime
import time
import math
import yaml
import os
import signal
import font_fredoka_one

from PIL import Image, ImageFont, ImageDraw

# Terminal interface
from interface.terminal import Terminal

# Setup logging and formatting
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(module)s - %(message)s")
logger = logging.getLogger("Inkra")


# Allows clean break without tkinter messages while debugging
# noinspection PyUnusedLocal
def interrupt(signum, frame):
    print(f"Exiting cleanly, signal given was {signum}")
    exit(0)


class Inkra:
    def __init__(self, city: str = "Guildford", country: str = "GB"):
        self.debug = False

        # Load config and set display options
        if os.path.exists("config.yml"):
            with open("config.yml", "r") as config_file:
                config = yaml.safe_load(config_file)
        else:
            Terminal.fatal("Missing config.yml, please create file.")
        self.options = config["Options"]

        try:
            # Try to initialize Inky display,
            # if it fails, fall back to a mock display from the Inky library

            # noinspection PyUnresolvedReferences
            from inky.auto import auto
            self.display = auto(verbose=True)

        except RuntimeError as e:  # Linux
            self.debug = True
            Terminal.warn(
                "Could not initialise display, if you're debugging you can ignore this,\n"
                "Printing exception:\n"
                f"{Terminal.underline}{e}\n"
            )
            from inky.mock import InkyMockPHATSSD1608

            self.display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        except ImportError as e:  # Windows
            self.debug = True
            Terminal.warn(
                "\nMissing dependencies,"
                "If you're on windows you can ignore this,"
                f"printing exception:\n{Terminal.underline}{e}\n"
            )
            from inky.mock import InkyMockPHATSSD1608

            self.display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        # Setup
        self.display.set_border(self.display.BLACK)

        # Setup image and Drawing object
        self.image = Image.new(
            "P", (self.display.width, self.display.height), self.display.WHITE
        )
        self.draw = ImageDraw.Draw(self.image)

        # Setup font, using banana but I'm leaving fredoka here for a bit.
        # TODO: remove fredoka
        self.font = ImageFont.truetype(font_fredoka_one.font, 18)
        with open("assets/banana.otf", "rb") as font:
            self.font = ImageFont.truetype(font, 14)

        # Consistent margins
        self.margin = 10
        self.line_offset = 53

        # Create tokenfile temporarily from config.yml token
        # if not os.path.exists("token.txt"):
        #    with open("token.txt", "wb") as tokenfile:
        #        tokenfile.write(config["Cupra"]["Token"])

        from interface import cupra

        self.cupra = cupra.Cupra()

        # Delete tokenfile but persist token in config.yaml
        pass

        # Only import and setup weather interface if it's actually going to be used.
        if self.options["ShowWeather"]:
            try:
                from interface import weather

                self.weather = weather.Weather(city, country)
            except ModuleNotFoundError:
                Terminal.error(
                    "\nOne or more modules required for the weather interface missing.\n"
                    "Disabling interface module"
                )
                self.options["ShowWeather"] = False
            except RuntimeError:
                Terminal.error("Weather interface failed to init, disabling.")

    def __draw_time(self):
        # TODO: Time function is a bit messy
        time_now = datetime.datetime.now().strftime("%H:%M")
        date = datetime.datetime.now().strftime("%d/%m")

        time_size = self.font.getbbox(time_now)
        # date_size = self.font.getbbox(date)
        self.draw.text((9, (time_size[3] + 5)), date, self.display.RED, self.font)
        # 9 is chosen as the x because
        # line-offset/2 = 26.5px
        # length of date or time = 17.5px
        # 26.5 - 17.5 = 9px putting them in the centre
        self.draw.text((9, 0), time_now, self.display.RED, self.font)

    def generate_image(self):
        # Reset canvas otherwise it flips each time
        self.image = None
        self.image = Image.new(
            "P", (self.display.width, self.display.height), self.display.WHITE
        )
        self.draw = ImageDraw.Draw(self.image)

        battery_status = self.cupra.get_battery_status()
        if battery_status is not None:
            charge = battery_status[0].currentSOC_pct.value
            charge_range = battery_status[0].cruisingRangeElectric_km.value
            unit = "km"
            soc_message = f"Charge: {charge}%"
            range_message = f"Range : {charge_range}{unit}"
            soc_message_bbox = self.font.getbbox(soc_message)

            soc_message_coords = (
                (self.display.width / 2) - (soc_message_bbox[2] / 2),
                (self.display.height / 2) - (soc_message_bbox[3] / 2),
            )
            range_message_coords = (
                soc_message_coords[0],
                soc_message_coords[1] + self.margin
            )
            self.draw.text(soc_message_coords, soc_message, self.display.RED, self.font)
            self.draw.text(range_message_coords, range_message, self.display.RED, self.font)
        else:
            message = "Failed to get SoC"
            message_bbox = self.font.getbbox(message)

            message_coords = (
                (self.display.width / 2) - (message_bbox[2] / 2),
                (self.display.height / 2) - (message_bbox[3] / 2),
            )
            self.draw.text(message_coords, message, self.display.RED, self.font)

        if self.options["ShowTime"]:
            self.__draw_time()

        if self.options["ShowLogo"]:
            logo = Image.open("assets/Cupra-Logo.png")
            logo_pos = (math.ceil((self.display.width / 2) - (logo.width / 2)), 0)
            self.image.paste(logo, logo_pos)

        if self.options["ShowBatteryIcon"]:
            if battery_status is not None:
                icon = battery_status[1]
                bat_pos = (
                    math.ceil((self.display.width / 2) - (icon.width / 2)),
                    (self.display.height - icon.height),
                )
                self.image.paste(icon, bat_pos)
        if self.options["DrawLines"]:
            self.draw.line(
                (self.line_offset, 0, self.line_offset, self.display.height),
                fill=self.display.BLACK,
                width=3,
            )
            self.draw.line(
                (
                    self.display.width - self.line_offset,
                    0,
                    self.display.width - self.line_offset,
                    self.display.height,
                ),
                fill=self.display.BLACK,
                width=3,
            )
        if self.options["ShowWeather"]:
            weather = self.weather.get_weather()
            if weather is None:
                # It's easier to make this the return point if getting weather fails
                # self.options["ShowWeather"] = False
                return self.image

            self.image.paste(
                weather["icon"], (self.display.width - weather["icon"].width, 0)
            )
            icon_box = (weather["icon"].width, weather["icon"].height)
            temperature_pos = (
                # math.floor(
                (self.display.width - icon_box[0]),
                5 + icon_box[1],
            )
            # Terminal.debug(temperature_pos)
            self.draw.text(
                temperature_pos, weather["temperature"], self.display.RED, self.font
            )

        return self.image

    def push_image(self):
        # This allows to have the Pi in either orientation
        if self.options["FlipScreen"]:
            self.image = self.image.transpose(
                method=Image.Transpose.FLIP_LEFT_RIGHT
            ).transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)

        # Push image to buffer and then trigger refresh
        self.display.set_image(self.image)
        self.display.show()


def main():
    display = Inkra()

    while True:
        display.generate_image()
        display.push_image()

        # Updating the actual display is slow, but Tk will hang on windows if the thread is slept
        # TODO: move actual display handling into a thread?
        if not display.debug:
            time.sleep(30)
        else:
            time.sleep(1)


if __name__ == "__main__":
    # Register the clean exit handler and go to main
    signal.signal(signal.SIGINT, interrupt)
    main()
