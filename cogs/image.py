from io import BytesIO

from wand.image import Image
import aiohttp
import discord
from discord.ext import commands


class Imaging:

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def link_to_image(link: str):
        """
        Returns a wand.image.Image and a bool stating whether or not it is a gif.
        """
        link = link.strip("<>")

        if "gif" in link:
            gif = True
        else:
            link = link.replace("webp", "png")
            gif = False

        async with aiohttp.ClientSession() as cs:
            async with cs.get(link) as r:
                r = await r.read()
        b = BytesIO(r)
        img = Image(filename=b)

        return img, gif


def setup(bot):
    bot.add_cog(Imaging(bot))
