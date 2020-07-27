import abc
import io
import numpy as np

import matplotlib.pyplot as plt
import PIL.Image
from wand.image import Image


__all__ = ('Wand', 'Numpy', 'Pillow', 'ImageManager', 'AsciiArt')


class ImageManager(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def input(image_bytes):
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def output(image_object):
        raise NotImplementedError


class Wand(ImageManager):

    @staticmethod
    def input(image_bytes) -> Image:
        image = Image(blob=image_bytes.getvalue())
        image_bytes.close()
        return image

    @staticmethod
    def output(image_object) -> io.BytesIO:
        image_bytes = io.BytesIO()
        image_object.save(image_bytes)
        image_bytes.seek(0)
        return image_bytes


class Pillow(ImageManager):

    @staticmethod
    def input(image_bytes) -> PIL.Image:
        image = PIL.Image.open(image_bytes)
        return image

    @staticmethod
    def output(image_object) -> io.BytesIO:
        image_bytes = io.BytesIO()
        image_object.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        return image_bytes


class Numpy(ImageManager):

    @staticmethod
    def input(image_bytes) -> np.ndarray:
        image = PIL.Image.open(image_bytes)
        return np.asarray(image)

    @staticmethod
    def output(arr) -> io.BytesIO:
        image_bytes = io.BytesIO()
        plt.imsave(image_bytes, arr)
        image_bytes.seek(0)
        return image_bytes


class AsciiArt(Numpy):

    @staticmethod
    def output(art: str) -> str:
        return art
