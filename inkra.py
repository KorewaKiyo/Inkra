from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import datetime
import time
import math


class Inkra:
    def __init__(self, flip=True):
        inky_real = True
        try:
            from inky.auto import auto
            inky_display = auto(verbose=True)

        except RuntimeError as e:  # Linux
            print("Could not initialise display, if you're debugging you can ignore this, printing exception:")
            print(e)
            from inky.mock import InkyMockPHATSSD1608
            inky_real = False
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

        except ImportError as e:  # Windows
            print("Missing dependencies,")
            print("If you're on windows you can ignore this,")
            print(f"printing exception:\n{e}\n")
            from inky.mock import InkyMockPHATSSD1608
            inky_real = False
            inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)
        except:
            raise Exception("Unknown error!")
        inky_display.set_border(inky_display.BLACK)

        self.width = inky_display.width
        self.height = inky_display.height
        self.display = inky_display
        self.display_simulated = inky_real
        self.image = Image.new("P", (self.width, self.height), self.display.WHITE)
        self.flip = flip
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(FredokaOne, 18)

    def battery_icon(self, charge: int):

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
            display.image.paste(Image.open("assets/Cupra-Logo.png"), ((display.width - timewidth) - timewidth - 48, 0))
        if show_bat_icon:
            print(charge)
            self.battery_icon(charge)
            bat_width = self.icon.width
            bat_height = self.icon.height
            bat_pos = ((display.width - timewidth) - timewidth - bat_width, display.height - bat_height)
            display.image.paste(self.icon, bat_pos)
        if draw_lines:
            display.draw.line((timewidth, 0, timewidth, display.height), fill=display.display.BLACK, width=3)
            display.draw.line((display.width - timewidth, 0, display.width - timewidth, display.height),
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


display = Inkra()

battery = 12

while not display.display_simulated:
    battery -= 1
    display.generate_image(show_logo=True, show_bat_icon=True, show_time=True, charge=battery, draw_lines=True)
    display.push_image()
    time.sleep(1)
# display.display.set_image(im)
# display.display.show()
# time.sleep(1)
# print(f"Finished displaying {newtime}")
