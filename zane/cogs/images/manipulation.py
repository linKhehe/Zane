import io

import matplotlib.pyplot as plt
import numpy as np
import skimage
import skimage.filters
from sklearn.preprocessing import minmax_scale
from skimage.color.adapt_rgb import adapt_rgb, each_channel
from skimage.exposure import rescale_intensity
from skimage.feature import hog as hog_image
from wand.color import Color
from wand.image import Image

from .decorators import manipulation, executor
from .image_managers import *

__all__ = ("magic", "deepfry", "invert", "concave",
           "convex", "floor", "vaporwave", "emboss",
           "edge", "bend", "posterize", "grayscale",
           "lsd", "swirl", 'polaroid', "arc",
           "sobel", "shuffle", "sort", "hog",
           "cube"
)


@executor
@manipulation(Wand)
def magic(image):
    """Content-aware-scale an image."""
    image.liquid_rescale(
        width=int(image.width * 0.4),
        height=int(image.height * 0.4),
        delta_x=1,
        rigidity=0
    )
    image.liquid_rescale(
        width=int(image.width * 1.7),
        height=int(image.height * 1.7),
        delta_x=2,
        rigidity=0
    )

    return image


@executor
@manipulation(Wand)
def deepfry(img):
    """Compress and saturate in image."""
    img.format = "jpeg"
    img.compression_quality = 1
    img.modulate(saturation=700)

    return img


@executor
@manipulation(Wand)
def invert(img):
    """Invert an image."""
    img.alpha_channel = False
    img.negate()

    return img


@executor
@manipulation(Wand)
def concave(img):
    """View an image through a concave lens."""
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[-.5, 0.0, 0.0, 1])

    return img


@executor
@manipulation(Wand)
def convex(img):
    """View an image through a convex lens."""
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[1, 0, 0, 1])

    return img


@executor
@manipulation(Wand)
def floor(img):
    """Make an image the floor."""
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


@executor
@manipulation(Wand)
def vaporwave(img):
    """Vvaappoorrwwaavvee an image."""
    img.alpha_channel = False
    img.function('sinusoid', [3, -90, 0.2, 0.7])
    img.modulate(saturation=25, brightness=75)

    return img


@executor
@manipulation(Wand)
def emboss(img):
    """Emboss an image."""
    img.transform_colorspace('gray')
    img.emboss(radius=3, sigma=50)

    return img


@executor
@manipulation(Wand)
def edge(img):
    """Make an image edgy."""
    img.alpha_channel = False
    img.transform_colorspace('gray')
    img.edge(2)

    return img


@executor
@manipulation(Wand)
def bend(img):
    """Bend the image like its paper."""
    img.alpha_channel = False
    img.virtual_pixel = "transparent"
    img.distort(method="plane_2_cylinder", arguments=[90])

    return img


@executor
@manipulation(Wand)
def posterize(img):
    """Posterize the image."""
    img.posterize(2)

    return img


@executor
@manipulation(Wand)
def grayscale(img):
    """Put the image in grayscale."""
    img.transform_colorspace('gray')

    return img


@executor
@manipulation(Wand)
def lsd(img):
    """Take a tab then look at the image."""
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


@executor
@manipulation(Wand)
def swirl(img):
    """Swirl an image."""
    img.swirl(200)
    return img


@executor
@manipulation(Wand)
def polaroid(img):
    """Give an image a polaroidesque frame."""
    img.polaroid()
    return img


@executor
@manipulation(Wand)
def arc(img):
    """Arc an image."""
    img.virtual_pixel = "tile"
    img.distort("arc", (360,))
    return img

@executor
@manipulation(Numpy)
def sobel(img):
    """Put a sobel filter on the image."""
    @adapt_rgb(each_channel)
    def _sobel_each(image):
        return skimage.filters.sobel(image)
    return rescale_intensity(255 - _sobel_each(img) * 255)


@executor
@manipulation(Numpy)
def shuffle(img):
    """Shuffle the pixels randomly."""
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    np.random.shuffle(img)

    return img.reshape(shape)


@executor
@manipulation(Numpy)
def sort(img):
    """Sort the pixels in the image."""
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    img = np.sort(img, 0)

    return img.reshape(shape)


@executor
@manipulation(Numpy, cmap=plt.cm.get_cmap("hot"))
def hog(img):
    """Histogram of oriented gradients."""
    _, img = hog_image(img, orientations=8, pixels_per_cell=(8, 8),
                       cells_per_block=(1, 1), visualize=True, multichannel=True)
    return img


# noinspection PyTypeChecker
@executor
@manipulation(Wand)
def cube(image: Image):
    """Make a 3D cube out of the image."""
    def s(x):
        return int(x / 3)

    image.resize(s(1000), s(860))
    image.format = "png"
    image.alpha_channel = 'opaque'

    image1 = image
    image2 = Image(image1)

    out = Image(width=s(3000 - 450), height=s(860 - 100) * 3)
    out.format = "png"

    image1.shear(background=Color("none"), x=-30)
    image1.rotate(-30)
    out.composite(image1, left=s(500 - 250), top=s(0 - 230) + s(118))
    image1.close()

    image2.shear(background="rgba(0,0,0,0)", x=30)
    image2.rotate(-30)
    image3 = Image(image2)
    out.composite(image2, left=s(1000 - 250) - s(72), top=s(860 - 230))
    image2.close()

    image3.flip()
    out.composite(image3, left=s(0 - 250) + s(68), top=s(860 - 230))
    image3.close()

    out.crop(left=80, top=40, right=665, bottom=710)

    return out


ascii_characters = {
    0: " ", 1: ".", 2: "'", 3: "'",
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


def create_ascii_art(array: np.ndarray) -> str:
    art = str()
    for i in range(0, array.shape[0], 2):
        row = array[i]
        art += "\n"
        for col in row:
            r, g, b = col[0:3]
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            art += ascii_characters[int(luminance / 5)]
    return art


@executor
def ascii(image: io.BytesIO):
    array = Numpy.input(image)
    return create_ascii_art(array)


@executor
def discord_ascii(image: io.BytesIO):
    image = Pillow.input(image)
    image = image.resize((62, 62))
    array = np.asarray(image)

    return create_ascii_art(array)


@executor
@manipulation(Wand)
def rotate_right(image: Image):
    image.rotate(90)
    return image


@executor
@manipulation(Wand)
def rotate_left(image: Image):
    image.rotate(-90)
    return image
