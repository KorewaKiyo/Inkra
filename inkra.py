from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import datetime
import time

inkyReal = False
try:
    # noinspection PyUnresolvedReferences
    from inky.auto import auto

    inky_display = auto(verbose=True)
    inkyReal = True

except RuntimeError as e:  # Linux
    print("Could not initialise display, if you're debugging you can ignore this, printing exception:")
    print(e)
    from inky.mock import InkyMockPHATSSD1608

    inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

except ImportError as e:  # Windows
    print("Missing dependencies,")
    print("If you're on windows you can ignore this,")
    print(f"printing exception:\n{e}\n")
    from inky.mock import InkyMockPHATSSD1608

    inky_display = InkyMockPHATSSD1608("red", h_flip=True, v_flip=True)

inky_display.set_border(inky_display.BLACK)
displayWidth = inky_display.width
displayHeight = inky_display.height
RED = inky_display.RED
BLACK = inky_display.BLACK
WHITE = inky_display.WHITE
im = Image.new("P", (displayWidth, displayHeight), WHITE)
print(displayHeight)

draw = ImageDraw.Draw(im)
font = ImageFont.truetype(FredokaOne, 18)


def battery_icon(charge: int):
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



battery = 12
message = f"battery is {battery}%"
w, h = font.getsize(message)
x = (displayWidth / 2) - (w / 2)
y = (displayHeight / 2) - (h / 2)
draw.text((x, y), message, RED, font)
newtime = datetime.datetime.now().strftime('%H:%M')
draw.text((5, 0), newtime, RED, font)
timewidth, timeheight = font.getsize(newtime)
timewidth = timewidth + 10
draw.line((timewidth, 0, timewidth, displayHeight), fill=BLACK, width=3)
draw.line((displayWidth - timewidth, 0, displayWidth - timewidth, displayHeight), fill=BLACK, width=3)
print(f"right line is {displayWidth - timewidth}")
print(f"left line is {timewidth}")
# (displayWidth - timewidth) = 199
# 199 - timewidth = 148
# 148 - 48 = 100
batterypos = ((displayWidth - timewidth) - timewidth - 48, 122 - 24)
print(timewidth)
im.paste(battery_icon(battery), batterypos)
im.paste(Image.open("assets/Cupra-Logo.png"), ((displayWidth - timewidth) - timewidth - 48, 0))
im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)

while not inkyReal:
    inky_display.set_image(im)
    inky_display.show()
    time.sleep(1)
inky_display.set_image(im)
inky_display.show()
time.sleep(1)
print(f"Finished displaying {newtime}")
