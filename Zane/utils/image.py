from io import BytesIO
import math

from wand.image import Image as WandImageBase
from wand.color import Color as WandColor
import aiohttp
import discord


class Color(WandColor):
    """
    A little subclass of wand.color.Color

    Adds functionality for ascii art.
    """

    def __init__(self, *args, **kwargs):
        self.ascii_characters = {
            300: "@",
            275: "#",
            250: ";",
            225: "+",
            200: "=",
            175: ":",
            150: "-",
            125: "\"",
            100: ",",
            75: "'",
            50: ".",
            25: " ",
            0: " "
        }
        super().__init__(*args, **kwargs)

    @property
    def ascii_character(self):
        value = self.red + self.green + self.blue
        value *= 100
        return self.ascii_characters[int(math.ceil(value / 25.) * 25)]


class Image(WandImageBase):
    """
    A little custom version of wand.image.WandImage.

    Adds functionality such as...

        from_link(link)
            - For creating an image from a link using aiohttp.
            
        from_bytes_io(BytesIO)
            - For creating an image from a bytes io object. Not very useful but saves some lines of code.

        to_bytes_io()
            - For saving an image to a BytesIO object.

        to_discord_file()
            - For saving an image to a discord.File object.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    async def from_link(cls, link: str = None):
        if link is None:
            return cls().blank(width=0, height=0)

        link.strip("<>")

        # Start a client session and get the link. Read the link to response variable.
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                response = await response.read()

        # Convert the response the a byte object
        byte_response = BytesIO(response)
        byte_response.seek(0)

        # Start an image object with the bytes.
        image = cls(file=byte_response)

        return image

    @classmethod
    async def from_bytes_io(self, bytes_io : BytesIO):
        # Convert the response the a byte object
        bytes_io.seek(0)

        # Start an image object with the bytes.
        image = cls(file=bytes_io)

        return image
    
    def to_bytes_io(self):
        bytes_io = BytesIO()

        # save self to the bytes io and seek to the beginning
        self.save(file=bytes_io)
        bytes_io.seek(0)
        return bytes_io

    def to_discord_file(self, filename: str):
        bytes_io = self.to_bytes_io()
        file = discord.File(bytes_io, filename=filename)
        return file
