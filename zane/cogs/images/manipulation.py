import matplotlib.pyplot as plt
import numpy as np
import skimage
import skimage.filters
from skimage.feature import hog as hog_image
from skimage.exposure import rescale_intensity
from skimage.color.adapt_rgb import adapt_rgb, each_channel
from wand.color import Color

from .enums import Library
from .decorators import manipulation, executor


@executor
@manipulation(Library.Wand)
def magic(image):
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
@manipulation(Library.Wand)
def deepfry(img):
    img.format = "jpeg"
    img.compression_quality = 1
    img.modulate(saturation=700)

    return img


@executor
@manipulation(Library.Wand)
def invert(img):
    img.alpha_channel = False
    img.negate()

    return img


@executor
@manipulation(Library.Wand)
def desat(img, threshold: int = 1):
    img.modulate(saturation=100 - (threshold * 50))

    return img


@executor
@manipulation(Library.Wand)
def sat(img, threshold: int = 1):
    img.modulate(saturation=100 + (threshold * 50))

    return img


@executor
@manipulation(Library.Wand)
def noise(img):
    img = img.fx("""iso=32; rone=rand(); rtwo=rand(); \
myn=sqrt(-2*ln(rone))*cos(2*Pi*rtwo); myntwo=sqrt(-2*ln(rtwo))* \
cos(2*Pi*rone); pnoise=sqrt(p)*myn*sqrt(iso)* \
channel(4.28,3.86,6.68,0)/255; max(0,p+pnoise)""")

    return img


@executor
@manipulation(Library.Wand)
def concave(img):
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[-.5, 0.0, 0.0, 1])

    return img


@executor
@manipulation(Library.Wand)
def convex(img):
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[1, 0, 0, 1])

    return img


@executor
@manipulation(Library.Wand)
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


@executor
@manipulation(Library.Wand)
def blur(img):
    img.blur(0, 5)

    return img


@executor
@manipulation(Library.Wand)
def vaporwave(img):
    img.alpha_channel = False
    img.function('sinusoid', [3, -90, 0.2, 0.7])
    img.modulate(saturation=25, brightness=75)

    return img


@executor
@manipulation(Library.Wand)
def emboss(img):
    img.transform_colorspace('gray')
    img.emboss(radius=3, sigma=50)

    return img


@executor
@manipulation(Library.Wand)
def edge(img):
    img.alpha_channel = False
    img.transform_colorspace('gray')
    img.edge(2)

    return img


@executor
@manipulation(Library.Wand)
def bend(img):
    img.alpha_channel = False
    img.virtual_pixel = "transparent"
    img.distort(method="plane_2_cylinder", arguments=[90])

    return img


@executor
@manipulation(Library.Wand)
def posterize(img):
    img.posterize(2)

    return img


@executor
@manipulation(Library.Wand)
def grayscale(img):
    img.transform_colorspace('gray')

    return img


@executor
@manipulation(Library.Wand)
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


@executor
@manipulation(Library.Wand)
def swirl(img):
    img.swirl(200)
    return img


@executor
@manipulation(Library.Wand)
def polaroid(img):
    img.polaroid()
    return img


@executor
@manipulation(Library.Wand)
def arc(img):
    img.virtual_pixel = "tile"
    img.distort("arc", (360,))
    return img

@executor
@manipulation(Library.Numpy)
def sobel(img):
    @adapt_rgb(each_channel)
    def _sobel_each(image):
        return skimage.filters.sobel(image)
    return rescale_intensity(255 - _sobel_each(img) * 255)


@executor
@manipulation(Library.Numpy)
def shuffle(img):
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    np.random.shuffle(img)

    return img.reshape(shape)


@executor
@manipulation(Library.Numpy)
def sort(img):
    shape = img.shape
    img = img.reshape((img.shape[0] * img.shape[1], img.shape[2]))

    img.sort(0)

    return img.reshape(shape)


@executor
@manipulation(Library.Numpy, cmap=plt.cm.get_cmap("hot"))
def hog(img):
    _, img = hog_image(img, orientations=8, pixels_per_cell=(8, 8),
                       cells_per_block=(1, 1), visualize=True, multichannel=True)
    return img
