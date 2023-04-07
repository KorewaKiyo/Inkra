from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import datetime
import time
import math



class Inkra:
    def __init__(self):
        inky_real = True
        try:
            # noinspection PyUnresolvedReferences
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
        inky_display.set_border(inky_display.BLACK)

        self.width = inky_display.width
        self.height = inky_display.height
        self.display = inky_display
        self.display_simulated = inky_real
        self.image = Image.new("P", (self.width, self.height), self.display.WHITE)
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype(FredokaOne, 18)

    def battery_icon(self, charge: int):
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
        return icon


display = Inkra()
display.font

battery = 12
message = f"battery is {battery}%"
w, h = display.font.getsize(message)
x = (display.width / 2) - (w / 2)
y = (display.height / 2) - (h / 2)
display.draw.text((x, y), message, display.display.RED, display.font)
newtime = datetime.datetime.now().strftime('%H:%M')
display.draw.text((5, 0), newtime, display.display.RED, display.font)
timelength = display.font.getlength(newtime)
 
timewidth = math.ceil(timelength) + 10
display.draw.line((timewidth, 0, timewidth, display.height), fill=display.display.BLACK, width=3)
display.draw.line((display.width - timewidth, 0, display.width - timewidth, display.height), fill=display.display.BLACK,
                  width=3)
print(f"right line is {display.width - timewidth}")
print(f"left line is {timewidth}")
# (display.width - timewidth) = 199
# 199 - timewidth = 148
# 148 - 48 = 100
batterypos = ((display.width - timewidth) - timewidth - 48, 122 - 24)
print(timewidth)
display.image.paste(display.battery_icon(battery), batterypos)
display.image.paste(Image.open("assets/Cupra-Logo.png"), ((display.width - timewidth) - timewidth - 48, 0))
im = display.image.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)

while not display.display_simulated:
    display.display.set_image(im)
    display.display.show()
    time.sleep(1)
display.display.set_image(im)
display.display.show()
time.sleep(1)
print(f"Finished displaying {newtime}")
