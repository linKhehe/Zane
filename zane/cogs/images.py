import aiohttp
import io
from time import perf_counter

import discord
from discord.ext import commands

import zane
import zane.imageops as imageops


class Images(commands.Cog):

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

    NUMBERS = {
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
        "0": "0️⃣",
        "m": "🇲",
        "s": "🇸",
        ".": "⏺️"
    }

    def __init__(self, bot):
        self.bot = bot

        self.session = None
        self.bot.loop.create_task(self.create_session())

        zane.logger.info("Images cog initiated")

        for name, kwargs in self.COMMANDS.items():
            zane.logger.debug(f"Registering command {name}")

            @commands.command(name=name, **kwargs)
            @commands.cooldown(1, 1, type=commands.BucketType.user)
            @commands.cooldown(5, 5, type=commands.BucketType.guild)
            @self.reacts_with_time
            @self.requires_image
            async def callback(ctx, member: discord.Member = None):
                image = await getattr(imageops, ctx.command.name)(ctx.image)
                file = discord.File(
                    fp=image,
                    filename="generated.png"
                )
                return await ctx.send(file=file)

            self.bot.add_command(callback)

        zane.logger.info("All image commands registered.")

    async def create_session(self, *args, **kwargs):
        self.session = aiohttp.ClientSession(*args, **kwargs)
        zane.logger.info("Image cog session created.")

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

    def reacts_with_time(self, func):
        async def wrapper(ctx, *args, **kwargs):
            start = perf_counter()
            await func(ctx, *args, **kwargs)
            end = perf_counter()

            reactions = [self.NUMBERS[e] for e in f"{round(end - start, 1)}s"]

            for reaction in reactions:
                await ctx.message.add_reaction(reaction)

        return wrapper

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())
        zane.logger.info("Image cog session closed.")


def setup(bot):
    bot.add_cog(Images(bot))
