import io

import aiohttp
import discord
from discord.ext import commands

from . import manipulation


class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = None

        image_commands = {
            "magic": {"help": "Content-aware-scale an image."},
            "deepfry": {"help": "Deepfry an image."},
            "emboss": {"help": "Emboss an image."},
            "vaporwave": {"help": "Vvaappoorrwwaavvee an image."},
            "floor": {"help": "Make an image the floor."},
            "concave": {"help": "View an image through a concave lens."},
            "convex": {"help": "View an image through a convex lens."},
            "invert": {"help": "Invert the colors of an image."},
            "lsd": {"help": "View an image through an LSD trip."},
            "posterize": {"help": "Posterize an image."},
            "grayscale": {"help": "Greyscale an image."},
            "bend": {"help": "Bend an image."},
            "edge": {"help": "Amplify the edges within an image."},
            "gay": {"help": "Make an image rainbow."},
            "sort": {"help": "Sort the colors in an image."},
            "sobel": {"help": "View an image through a sobel color filter."},
            "shuffle": {"help": "Shuffle the pixels of an image."},
            "swirl": {"help": "Give an image a swirley."},
            "polaroid": {"help": "Polaroid picture printer go brrrr."},
            "arc": {"help": "Arc an image."},
            "hog": {"help": "this does something true"},
        }

        for k, v in image_commands.items():
            @commands.command(name=k, **v)
            async def callback(ctx, *, member: discord.Member = None):
                member = member or ctx.author
                function = getattr(manipulation, ctx.command.name)
                avatar = await self.read_image(member.avatar_url_as(format="png").__str__())
                image = await function(avatar, loop=self.bot.loop)
                await ctx.send(file=discord.File(image, f"{ctx.command.name}.png"))
            self.bot.add_command(callback)

    async def read_image(self, url: str):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        async with self.session.get(url) as response:
            image = io.BytesIO(await response.read())
            image.seek(0)
        return image
