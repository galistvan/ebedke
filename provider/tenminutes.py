import base64
import urllib.request
from io import BytesIO
from math import floor

from PIL import Image


WIDTH = 513
HEIGHT = 284

URL = "http://www.10minutes.hu/"
IMG_PATH = "images/home_1_06.png"

def getMenu(_):
    with urllib.request.urlopen(URL + IMG_PATH) as response:
        r = response.read()
        menu_img = Image.open(BytesIO(r))

        a_menu_box = (234, 54, 234 + WIDTH, 54 + HEIGHT)
        b_menu_box = (234, 452, 234 + WIDTH, 452 + HEIGHT)

        amenu = menu_img.crop(a_menu_box)
        bmenu = menu_img.crop(b_menu_box)

        new_im = Image.new('RGB', (WIDTH * 2, HEIGHT))
        new_im.paste(amenu, (0,0))
        new_im.paste(bmenu, (WIDTH,0))

        new_im = new_im.point(lambda i: i < 100 and 255)
        new_im = new_im.convert('1')
        new_im = new_im.resize((floor(WIDTH*2*0.80), floor(HEIGHT*0.80)), Image.BICUBIC)

        f = BytesIO()
        new_im.save(f, format="png", optimize=True, compress_level=9, bits=4)
        menu = "<img style='width:100%;' src='data:image/png;base64," + base64.b64encode(f.getvalue()).decode('ascii')       + "'/>"
        return {
            'name': '10 minutes',
            'url' : URL,
            'menu': menu
        }

if __name__ == "__main__":
    print(getMenu(None))
