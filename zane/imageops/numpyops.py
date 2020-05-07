from io import BytesIO

import skimage
import skimage.transform
import numpy as np
from skimage.exposure import rescale_intensity
from skimage.color.adapt_rgb import adapt_rgb, each_channel
import skimage.segmentation
import skimage.filters
import matplotlib.pyplot as plt
from skimage import io


async def bytes_to_np(img_bytes: BytesIO):
    """This takes a BytesIO containing an image and converts them to a np.ndarray using
    skimage.io.imread."""
    ret = skimage.io.imread(img_bytes)
    return ret


async def np_to_bytes(img_bytes: BytesIO):
    """This takes a np.ndarray containing an image and converts it to a BytesIO object
    containing an image."""
    b = BytesIO()
    plt.imsave(b, img_bytes)
    b.seek(0)
    return b


def _sort(img: np.ndarray):
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    img.sort(0)

    return img.reshape(shape)


# If you are seeing this and think that you can make
# the selection of characters better, please do.
# this is just some random one I found online and
# made into a dictionary.
_ascii_characters = {
    0: " ", 1: ".", 2: "'", 3: "`",
    4: "^", 5: "\"", 6: ",", 7: ":",
    8: ";", 9: "I", 10: "1", 11: "!",
    12: "i", 13: ">", 14: "<", 15: "~",
    16: "+", 17: "?", 18: "]", 19: "[",
    20: "}", 21: "{", 22: "]", 23: "[",
    24: "|", 25: "/", 26: "\\", 27: "t",
    28: "x", 29: "n", 30: "u", 31: "v",
    32: "z", 33: "X", 34: "Y", 35: "U",
    36: "J", 37: "C", 38: "L", 39: "Q",
    40: "0", 41: "O", 42: "Z", 43: "#",
    44: "M", 45: "W", 46: "&", 47: "8",
    48: "%", 49: "B", 50: "@", 51: "@"
}


def _ascii_art(img: np.ndarray):
    ascii_art = ""

    for i_row in range(0, img.shape[0], 2):
        row = img[i_row]
        ascii_art += "\n"
        for col in row:
            avg = int(col[0]) + int(col[1]) + int(col[2])
            avg = int(avg / 3)
            ascii_art += _ascii_characters[int(avg / 5)]

    return ascii_art


def _sobel(img: np.ndarray):
    @adapt_rgb(each_channel)
    def _sobel_each(image):
        return skimage.filters.sobel(image)
    return rescale_intensity(255 - _sobel_each(img) * 255)


def _shuffle(img: np.ndarray):
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    np.random.shuffle(img)

    return img.reshape(shape)
