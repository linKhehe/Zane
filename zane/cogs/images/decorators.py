from collections import namedtuple
import io

import matplotlib.pyplot as plt
from wand.image import Image
import skimage.io

from .enums import Library


ImageIO = namedtuple(
    "ImageIO",
    [
        "input",
        "output"
    ]
)


def _wand_in(image_bytes):
    image = Image(blob=image_bytes.getvalue())
    image_bytes.close()
    return image


def _wand_out(in_image: Image, **kwargs):
    image_bytes = io.BytesIO()
    in_image.save(image_bytes)
    with Image(blob=image_bytes.getvalue()) as out_image:
        image_bytes.close()
        out_image.format = in_image.format
        in_image.close()

        image_bytes = io.BytesIO()
        out_image.save(image_bytes)
        image_bytes.seek(0)
    return image_bytes


def _numpy_in(image_bytes):
    image_bytes.seek(0)
    return skimage.io.imread(image_bytes, plugin='matplotlib')


def _numpy_out(arr, cmap=None):
    image_bytes = io.BytesIO()
    plt.imsave(image_bytes, arr, cmap=cmap)
    image_bytes.seek(0)
    return image_bytes


image_ios = {
    "wand": ImageIO(input=_wand_in, output=_wand_out),
    "numpy": ImageIO(input=_numpy_in, output=_numpy_out)
}


def manipulation(library: Library, cmap=None):
    def decorator(function):
        def wrapper(images, *args, **kwargs):
            image_io = image_ios.get(library.value)

            if isinstance(images, list):
                images = [image_io.input(image_bytes) for image_bytes in images]
                images = function(images, *args, **kwargs)
                return [image_io.output(image, cmap=cmap) for image in images]
            else:
                image = images
                image = image_io.input(image)
                image = function(image, *args, **kwargs)
                return image_io.output(image, cmap=cmap)
        return wrapper
    return decorator


def executor(function):
    def decorator(*args, loop=None, **kwargs):
        return loop.run_in_executor(None, function, *args, **kwargs)
    return decorator
