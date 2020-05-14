import asyncio
import io
import functools

import skimage.io
from wand.image import Image
import matplotlib.pyplot as plt


loop = asyncio.get_event_loop()


async def run_in_executor(func, *args, **kwargs):
    executor = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, executor)


async def bytes_to_wand(img_bytes: io.BytesIO):
    return Image(blob=img_bytes.getvalue())


async def wand_to_bytes(img: Image):
    ret = io.BytesIO()
    img.save(ret)
    if img.format != "png":
        with Image(blob=ret.getvalue()) as converted:
            converted.format = "png"
            converted.save(ret)
    img.close()
    ret.seek(0)

    return ret


async def bytes_to_np(img_bytes: io.BytesIO):
    ret = skimage.io.imread(img_bytes)
    return ret


async def np_to_bytes(img_bytes: io.BytesIO):
    b = io.BytesIO()
    plt.imsave(b, img_bytes)
    b.seek(0)
    return b


def manipulation_numpy(func):
    async def wrapper(image: io.BytesIO, *args, **kwargs):
        image = await bytes_to_np(image)
        image = await run_in_executor(func, image, *args, **kwargs)
        return await np_to_bytes(image)
    return wrapper


def manipulation_wand(func):
    async def wrapper(image: io.BytesIO, *args, **kwargs):
        image = await bytes_to_wand(image)
        image = await run_in_executor(func, image, *args, **kwargs)
        return await wand_to_bytes(image)
    return wrapper
