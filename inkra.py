from PIL import Image, ImageFont, ImageDraw

import font_fredoka_one
import datetime
import time
import math


class Inkra:
    def __init__(self, flip: bool = True):
        inky_real = True
        try:
            # noinspection PyUnresolvedReferences
            from inky.auto import auto
            inky_display = auto(verbose=True)

        except RuntimeError as e:  # Linux
            print(f"Could not initialise display, if you're debugging you can ignore this, printing exception:\n{e}")
            from inky.mock import InkyMockPHATSSD1608
            inky_real = False
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        except ImportError as e:  # Windows
            print("Missing dependencies," \
                  "If you're on windows you can ignore this," \
                  f"printing exception:\n{e}\n")
            from inky.mock import InkyMockPHATSSD1608
            inky_real = False
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        inky_display.set_border(inky_display.BLACK)
        self.width = inky_display.width
        self.height = inky_display.height
        self.display = inky_display
        self.display_real = inky_real
        self.image = Image.new("P", (self.width, self.height), self.display.WHITE)
        self.flip = flip
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(font_fredoka_one.font, 18)
        with open("assets/SourceCodePro-Bold.otf", "rb") as font:
            self.font = ImageFont.truetype(font, 15)
        with open("assets/banana.otf", "rb") as font:
            self.font = ImageFont.truetype(font, 14)

        self.margin = 10
        self.lineoffset = 53

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
        now = datetime.datetime.now().strftime('%H:%M')
        timelength = display.font.getbbox(datetime.datetime.now().strftime('%H:%M'))[2]
        if show_time:
            self.draw.text((5, 0), now, self.display.RED, self.font)
            timewidth = math.ceil(timelength) + 10

        if show_logo:
            logo = Image.open("assets/Cupra-Logo.png")
            logo_pos = (
                (self.width - (timelength + self.margin)) - (timelength + self.margin) - logo.width,
                0
            )
            self.image.paste(logo, logo_pos)
        if show_bat_icon:
            print(charge)
            self.__battery_icon(charge)
            bat_width = self.icon.width
            bat_height = self.icon.height
            bat_pos = ((self.width - (timelength + 10)) - (timelength + 10) - bat_width, self.height - bat_height)
            bat_pos2 = (self.width - 2 * (timelength + self.margin) - bat_width, self.height - bat_height)
            bat_pos = (
                int((self.width / 2) - (bat_width / 2)),
                self.height - bat_height
            )

            print(bat_pos, bat_pos2)
            self.image.paste(self.icon, bat_pos2)
        if draw_lines:
            self.draw.line((self.lineoffset, 0, self.lineoffset, self.height), fill=self.display.BLACK, width=3)
            self.draw.line((self.width - self.lineoffset, 0, self.width - self.lineoffset, self.height),
                           fill=display.display.BLACK,
                           width=3)
            print(f"right line is {display.width - timewidth}")
            print(f"left line is {timewidth}")
            # (display.width - timewidth) = 199
            # 199 - timewidth = 148
            # 148 - 48 = 100,
        return self.image

    def push_image(self):
        if self.flip:
            self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
        self.display.set_image(self.image)
        self.display.show()


display = Inkra(flip=True)

battery = 45

while True:
    # battery -= 1
    if battery == -1:
        time.sleep(30)
        exit(0)

    display.generate_image(show_logo=True, show_bat_icon=True, show_time=True, charge=battery, draw_lines=True)

    # display.image = display.image.transpose(Image.FLIP_LEFT_RIGHT)
    display.push_image()
    if display.display_real:
        time.sleep(30)
    else:
        time.sleep(1)
