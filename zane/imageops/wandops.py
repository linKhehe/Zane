import os
from io import BytesIO

from wand.image import Image
from wand.color import Color


async def bytes_to_wand(img_bytes: BytesIO):
    return Image(blob=img_bytes.getvalue())


async def wand_to_bytes(img: Image):
    ret = BytesIO()
    img.save(ret)
    if img.format != "png":
        with Image(blob=ret.getvalue()) as converted:
            converted.format = "png"
            converted.save(ret)
    img.close()
    ret.seek(0)

    return ret


def _magic(img: Image):
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
    img.modulate(saturation=100 - (threshold * 50))

    return img


def _sat(img: Image, threshold: int = 1):
    img.modulate(saturation=100 + (threshold * 50))

    return img


def _noise(img: Image):
    img = img.fx("""iso=32; rone=rand(); rtwo=rand(); \
myn=sqrt(-2*ln(rone))*cos(2*Pi*rtwo); myntwo=sqrt(-2*ln(rtwo))* \
cos(2*Pi*rone); pnoise=sqrt(p)*myn*sqrt(iso)* \
channel(4.28,3.86,6.68,0)/255; max(0,p+pnoise)""")

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


# noinspection PyInterpreter,PyInterpreter
def _sphere(img: Image):
    if os.name == 'nt':
        slash = "\\"
    else:
        slash = "/"

    x = max([img.width, img.height])
    img.resize(x, x)

    path = f"{os.path.dirname(os.path.realpath(__file__))}{slash}image_assets{slash}"

    img.save(filename=path + "sphere-in.png")

    sphere = Image(filename=path + "spherical_unified_master.png")
    sphere.resize(img.width, img.height)
    sphere.save(filename=path + "spherical_unified.png")

    img.close()
    sphere.close()

    quote = "\""

    os.system(
        f"magick convert {quote}{path}sphere-in.png{quote} {quote}{path}spherical_unified.png{quote}  "
        "( -clone 0,1 -alpha set -compose Distort -composite ) "
        "( -clone 1   -channel B -separate +channel ) "
        "( -clone 2,3 -compose HardLight -composite ) "
        f"( -clone 4,1 -compose DstIn -composite ) -delete 0--2  {quote}{path}sphere-out.png{quote}")

    return Image(filename=path + "sphere-out.png")


def _swirl(img: Image):
    img.swirl(200)
    return img


def _polaroid(img: Image):
    img.polaroid()
    return img


def _arc(img: Image):
    # img.artifacts["distort:viewport"] = "100x100-50-50"
    img.virtual_pixel = "tile"
    img.distort("arc", (360,))
    return img
