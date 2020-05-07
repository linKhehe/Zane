import asyncio
import functools
from io import BytesIO

from .wandops import bytes_to_wand, wand_to_bytes, _magic, _emboss, _deepfry, _vaporwave, _floor, _concave, _convex, \
    _invert, _sat, _desat, _lsd, _posterize, _grayscale, _bend, _edge, _gay, _sphere
from .numpyops import bytes_to_np, np_to_bytes, _sort, _ascii_art, _sobel, _shuffle

loop = asyncio.get_event_loop()


async def run_in_executor(func, *args, **kwargs):
    executor = functools.partial(func, *args, **kwargs)
    ret = await loop.run_in_executor(None, executor)
    return ret


async def magic(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_magic, img)
    return await wand_to_bytes(img)


async def deepfry(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_deepfry, img)
    return await wand_to_bytes(img)


async def emboss(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_emboss, img)
    return await wand_to_bytes(img)


async def vaporwave(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_vaporwave, img)
    return await wand_to_bytes(img)


async def floor(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_floor, img)
    return await wand_to_bytes(img)


async def concave(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_concave, img)
    return await wand_to_bytes(img)


async def convex(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_convex, img)
    return await wand_to_bytes(img)


async def invert(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_invert, img)
    return await wand_to_bytes(img)


async def desat(img_bytes: BytesIO, threshold: int):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_desat, img, threshold)
    return await wand_to_bytes(img)


async def sat(img_bytes: BytesIO, threshold: int):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_sat, img, threshold)
    return await wand_to_bytes(img)


async def lsd(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_lsd, img)
    return await wand_to_bytes(img)


async def grayscale(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_grayscale, img)
    return await wand_to_bytes(img)


async def posterize(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_posterize, img)
    return await wand_to_bytes(img)


async def bend(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_bend, img)
    return await wand_to_bytes(img)


async def edge(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_edge, img)
    return await wand_to_bytes(img)


async def sphere(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_sphere, img)
    return await wand_to_bytes(img)


async def ascii_art(img_bytes: BytesIO):
    img = await bytes_to_np(img_bytes)
    art = await run_in_executor(_ascii_art, img)
    return art


async def gay(img_bytes: BytesIO):
    img = await bytes_to_wand(img_bytes)
    img = await run_in_executor(_gay, img)
    return await wand_to_bytes(img)


async def sort(img_bytes: BytesIO):
    img = await bytes_to_np(img_bytes)
    img = await run_in_executor(_sort, img)
    return await np_to_bytes(img)


async def sobel(img_bytes: BytesIO):
    img = await bytes_to_np(img_bytes)
    img = await run_in_executor(_sobel, img)
    return await np_to_bytes(img)


async def shuffle(img_bytes: BytesIO):
    img = await bytes_to_np(img_bytes)
    img = await run_in_executor(_shuffle, img)
    return await np_to_bytes(img)
