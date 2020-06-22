import aiohttp
import io

import discord
from discord.ext import commands

import zane
import zane.imageops as imageops


class Images(commands.Cog):

    # All the commands that need to be created, these must also be names
    # of attributes of the imageops library
    COMMANDS = {
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
        "arc": {"help": "Arc an image."}
    }

    def __init__(self, bot):
        self.bot = bot

        self.session = None
        self.bot.loop.create_task(self.create_session())

        zane.logger.info("Images cog initiated")

        for name, kwargs in self.COMMANDS.items():
            zane.logger.debug(f"Registering command {name}")

            @commands.command(name=name, **kwargs)
            @self.requires_image
            async def callback(ctx, member: discord.Member = None):
                image = await getattr(imageops, ctx.command.name)(ctx.image)
                file = discord.File(
                    fp=image,
                    filename="generated.png"
                )
                await ctx.send(file=file)

            self.bot.add_command(callback)

        zane.logger.info("All image commands registered.")

    async def create_session(self, *args, **kwargs):
        self.session = aiohttp.ClientSession(*args, **kwargs)

    async def read_image(self, url: str):
        async with self.session.get(url) as get:
            return io.BytesIO(await get.read())

    def requires_image(self, func):
        async def wrapper(ctx, member=None):
            await ctx.trigger_typing()

            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            elif member is not None:
                url = str(member.avatar_url_as(format="png"))
            else:
                url = str(ctx.author.avatar_url_as(format="png"))

            ctx.image = await self.read_image(url)

            await func(ctx, member)

        return wrapper

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())


def setup(bot):
    bot.add_cog(Images(bot))
