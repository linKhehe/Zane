# -*- coding: utf-8 -*-

"""
blissops.wandops
================

Somewhat async image manipulation library
created for use within the bliss Discord bot.
Makes use of numpy and wand and takes BytesIO
as an input and as an output.

:copyright: (c) 2019 Liam (ir-3) H.
:license: MIT, see LICENSE for more details.
"""

import os
from io import BytesIO

from wand.image import Image
from wand.color import Color


async def bytes_to_wand(img_bytes: BytesIO):
    return Image(blob=img_bytes.getvalue())


async def wand_to_bytes(img: Image):
    ret = BytesIO()
    img.save(ret)
    if img.format is not "png":
        with Image(blob=ret.getvalue()) as converted:
            converted.format = "png"
            converted.save(ret)
    img.close()
    ret.seek(0)

    return ret


def _magic(img: Image):
    img.liquid_rescale(
        width=int(img.width * 0.4),
        height=int(img.height * 0.4),
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


def _deepfry(img: Image):
    img.format = "jpeg"
    img.compression_quality = 1
    img.modulate(saturation=700)

    return img


def _invert(img: Image):
    img.alpha_channel = False
    img.negate()

    return img


def _desat(img: Image, threshold: int = 1):
    img.modulate(saturation=100-(threshold*50))

    return img


def _sat(img: Image, threshold: int = 1):
    img.modulate(saturation=100+(threshold*50))

    return img


def _noise(img: Image):
    img = img.fx("""iso=32; rone=rand(); rtwo=rand(); \
myn=sqrt(-2*ln(rone))*cos(2*Pi*rtwo); myntwo=sqrt(-2*ln(rtwo))* \
cos(2*Pi*rone); pnoise=sqrt(p)*myn*sqrt(iso)* \
channel(4.28,3.86,6.68,0)/255; max(0,p+pnoise)""")

    return img


def _arc(img: Image):
    img.virtual_pixel = "transparent"
    img.distort(method='arc', arguments=[360])

    return img


def _concave(img: Image):
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[-.5, 0.0, 0.0, 1])

    return img


def _convex(img: Image):
    img.virtual_pixel = "transparent"
    img.background_color = Color("white")
    img.distort(method="barrel", arguments=[1, 0, 0, 1])

    return img


def _floor(img: Image):
    x, y = img.size

    img.alpha_channel = False
    img.background_color = Color("#81cfe0")
    img.virtual_pixel = "tile"

    img.distort(
        method="perspective",
        arguments=[
            0,
            0,
            20,
            61,

            90,
            0,
            70,
            63,

            0,
            90,
            0,
            83,

            90,
            90,
            85,
            88
        ]
    )

    img.resize(x*2, y*2)

    return img


def _blur(img: Image):
    img.blur(0, 5)

    return img


def _vaporwave(img: Image):
    img.alpha_channel = False
    img.function('sinusoid', [3, -90, 0.2, 0.7])
    img.modulate(saturation=25, brightness=75)

    return img


def _emboss(img: Image):
    img.transform_colorspace('gray')
    img.emboss(radius=3, sigma=50)

    return img


def _edge(img: Image):
    img.alpha_channel = False
    img.transform_colorspace('gray')
    img.edge(2)

    return img


def _bend(img: Image):
    img.alpha_channel = False
    img.virtual_pixel = "transparent"
    img.distort(method="plane_2_cylinder", arguments=[90])

    return img


def _posterize(img: Image):
    img.posterize(2)

    return img


def _grayscale(img: Image):
    img.transform_colorspace('gray')

    return img


def _lsd(img: Image):
    _magic(img)
    img.alpha_channel = False
    img.function('sinusoid', [3, -90, 0.2, 0.7])
    img.modulate(saturation=200, brightness=75)

    return img


def _gay(img: Image):
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
