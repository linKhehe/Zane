import os

import numpy as np
import skimage
import skimage.filters
from skimage.exposure import rescale_intensity
from skimage.color.adapt_rgb import adapt_rgb, each_channel
from wand.image import Image
from wand.color import Color

from .decorators import manipulation_numpy, manipulation_wand


@manipulation_wand
def magic(img):
    img.liquid_rescale(
        width=int(img.width * 0.5),
        height=int(img.height * 0.5),
        delta_x=1,
        rigidity=0
    )
    img.liquid_rescale(
        width=int(img.width * 1.6),
        height=int(img.height * 1.6),
        delta_x=2,
        rigidity=0
    )

    return img


@manipulation_wand
def deepfry(img):
    img.format = "jpeg"
    img.compression_quality = 1
    img.modulate(saturation=700)

    return img


@manipulation_wand
def invert(img):
    img.alpha_channel = False
    img.negate()

    return img


@manipulation_wand
def desat(img, threshold: int = 1):
    img.modulate(saturation=100 - (threshold * 50))

    return img


@manipulation_wand
def sat(img, threshold: int = 1):
    img.modulate(saturation=100 + (threshold * 50))

    return img


@manipulation_wand
def noise(img):
    img = img.fx("""iso=32; rone=rand(); rtwo=rand(); \
myn=sqrt(-2*ln(rone))*cos(2*Pi*rtwo); myntwo=sqrt(-2*ln(rtwo))* \
cos(2*Pi*rone); pnoise=sqrt(p)*myn*sqrt(iso)* \
channel(4.28,3.86,6.68,0)/255; max(0,p+pnoise)""")

    return img


@manipulation_wand
def concave(img):
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[-.5, 0.0, 0.0, 1])

    return img


@manipulation_wand
def convex(img):
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[1, 0, 0, 1])

    return img


@manipulation_wand
def floor(img):
    x, y = img.size

    img.alpha_channel = False
    img.background_color = Color("#81cfe0")
    img.virtual_pixel = "tile"

    img.resize(255, 255)

    img.distort(
        method="perspective",
        arguments=(0, 0, 77, 153,
                   img.height, 0, 179, 153,
                   0, img.width, 51, 255,
                   img.height, img.width, 204, 255)
    )

    img.resize(x, y)

    return img


@manipulation_wand
def blur(img):
    img.blur(0, 5)

    return img


@manipulation_wand
def vaporwave(img):
    img.alpha_channel = False
    img.function('sinusoid', [3, -90, 0.2, 0.7])
    img.modulate(saturation=25, brightness=75)

    return img


@manipulation_wand
def emboss(img):
    img.transform_colorspace('gray')
    img.emboss(radius=3, sigma=50)

    return img


@manipulation_wand
def edge(img):
    img.alpha_channel = False
    img.transform_colorspace('gray')
    img.edge(2)

    return img


@manipulation_wand
def bend(img):
    img.alpha_channel = False
    img.virtual_pixel = "transparent"
    img.distort(method="plane_2_cylinder", arguments=[90])

    return img


@manipulation_wand
def posterize(img):
    img.posterize(2)

    return img


@manipulation_wand
def grayscale(img):
    img.transform_colorspace('gray')

    return img


@manipulation_wand
def lsd(img):
    img.liquid_rescale(
        width=int(img.width * 0.5),
        height=int(img.height * 0.5),
        delta_x=1,
        rigidity=0
    )
    img.liquid_rescale(
        width=int(img.width * 1.6),
        height=int(img.height * 1.6),
        delta_x=2,
        rigidity=0
    )

    img.alpha_channel = False
    img.function('sinusoid', [3, -90, 0.2, 0.7])
    img.modulate(saturation=200, brightness=75)

    return img


@manipulation_wand
def gay(img):
    if os.name == 'nt':
        slash = "\\"
    else:
        slash = "/"
    with Image(filename=f"{os.path.dirname(os.path.realpath(__file__))}{slash}image_assets{slash}gay.jpg") as gay:
        img.transform_colorspace("gray")
        img.transform_colorspace("rgb")
        gay.transparentize(.50)
        gay.sample(img.width, img.height)
        img.composite(gay, 0, 0)
    return img


@manipulation_wand
def swirl(img):
    img.swirl(200)
    return img


@manipulation_wand
def polaroid(img):
    img.polaroid()
    return img


@manipulation_wand
def arc(img):
    img.virtual_pixel = "tile"
    img.distort("arc", (360,))
    return img


@manipulation_numpy
def ascii_art(img: np.ndarray):
    ascii_characters = {
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

    ascii_art = ""

    for i_row in range(0, img.shape[0], 2):
        row = img[i_row]
        ascii_art += "\n"
        for col in row:
            avg = int(col[0]) + int(col[1]) + int(col[2])
            avg = int(avg / 3)
            ascii_art += ascii_characters[int(avg / 5)]

    return ascii_art


@manipulation_numpy
def sobel(img):
    @adapt_rgb(each_channel)
    def _sobel_each(image):
        return skimage.filters.sobel(image)
    return rescale_intensity(255 - _sobel_each(img) * 255)


@manipulation_numpy
def shuffle(img):
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    np.random.shuffle(img)

    return img.reshape(shape)


@manipulation_numpy
def sort(img):
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    img.sort(0)

    return img.reshape(shape)
