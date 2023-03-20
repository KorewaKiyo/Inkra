from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
import datetime

from inky.auto import auto

inky_display = auto()
inky_display.set_border(inky_display.WHITE)
battery_image = Image.open('batterylow.png')
battery = 100
while True:
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    W = 250
    H = 122
    im = Image.new("P", (W, H))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(FredokaOne, 16)
    battery -= 15
    message = f"battery is {battery}%"
    if battery <= 30:
        im.paste(battery_image, (int(W / 2) - 16, 0))
    w, h = font.getsize(message)
    x = (W / 2) - (w / 2)
    y = (H / 2) - (h / 2)
    print(x, y)
    draw.text((x, y), message, RED, font)
    newtime = datetime.datetime.now().strftime('%H:%M')
    draw.text((5, 0), newtime, RED, font)
    timewidth, timeheight = font.getsize(newtime)
    timewidth = timewidth + 10
    draw.line((timewidth, 0, timewidth, H), fill=BLACK, width=2)
    draw.line((W - timewidth, 0, W - timewidth, H), fill=BLACK, width=2)

    #im.show()

    inky_display.set_image(im)
    print(f"Displaying {newtime}")
    inky_display.show(busy_wait=True)
    print(f"Finished displaying {newtime}")
