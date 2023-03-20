from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import datetime

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


def battery_icon(img, charge: int, pos: int):
    print(charge, pos)
    if charge <= 15:
        img.paste(Image.open('assets/battery15.png'), (pos, 0))
    elif charge < 30:
        img.paste(Image.open('assets/battery30.png'), (pos, 0))
    elif charge < 50:
        img.paste(Image.open('assets/battery50.png'), (pos, 0))
    elif charge < 70:
        img.paste(Image.open('assets/battery70.png'), (pos, 0))
    else:
        print("Batteries full")
        img.paste(Image.open('assets/battery100.png'), (pos, 0))


battery = 85
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

batterypos = (displayWidth - timewidth) - timewidth - 48
battery_icon(im, battery, batterypos)

im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
inky_display.set_image(im)
while not inkyReal:
    inky_display.show()
print(f"Finished displaying {newtime}")
