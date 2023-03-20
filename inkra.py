from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import datetime

from inky.auto import auto

inky_display = auto(verbose=True)
inky_display.set_border(inky_display.WHITE)

displayWidth = inky_display.width
displayHeight = inky_display.height
im = Image.new("P", (displayWidth, displayHeight))
draw = ImageDraw.Draw(im)
font = ImageFont.truetype(FredokaOne, 18)


def battery_icon(im, charge: int, pos: int):
    if charge <= 15:
        im.paste(Image.open('assets/battery15.png'), (pos, 0))
    elif charge < 30:
        im.paste(Image.open('assets/battery30.png'), (pos, 0))
    elif charge < 50:
        im.paste(Image.open('assets/battery50.png'), (pos, 0))
    elif charge < 70:
        im.paste(Image.open('assets/battery70.png'), (pos, 0))
    else:
        im.paste(Image.open('assets/battery100.png'), (pos, 0))


battery = 85
message = f"battery is {battery}%"
w, h = font.getsize(message)
x = (displayWidth / 2) - (w / 2)
y = (displayHeight / 2) - (h / 2)
print(x, y)
draw.text((x, y), message, inky_display.RED, font)
newtime = datetime.datetime.now().strftime('%H:%M')
draw.text((5, 0), newtime, inky_display.RED, font)
timewidth, timeheight = font.getsize(newtime)
timewidth = timewidth + 10
draw.line((timewidth, 0, timewidth, displayHeight), fill=inky_display.BLACK, width=2)
draw.line((displayWidth - timewidth, 0, displayWidth - timewidth, displayHeight), fill=inky_display.BLACK, width=2)
print(f"right line is {displayWidth - timewidth}")
print(f"left line is {timewidth}")

batterypos = (displayWidth - timewidth) - timewidth - 48
battery_icon(im,battery,batterypos)
im = im.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)

inky_display.set_image(im)
inky_display.show(busy_wait=True)
print(f"Finished displaying {newtime}")
