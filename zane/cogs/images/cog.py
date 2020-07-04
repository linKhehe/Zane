import io
import time
import typing

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
            "cube": {"help": "command in testing"}
        }

        for k, v in image_commands.items():
            @commands.command(name=k, **v)
            # @self.typing
            async def callback(ctx, *, member: typing.Union[discord.Member, discord.PartialEmoji] = None):
                function = getattr(manipulation, ctx.command.name)

                attachment = bool(ctx.message.attachments)
                if isinstance(member, discord.PartialEmoji):
                    title = f"Emoji {member.name}"
                    url = member.url.__str__()
                    image_url = member.url.__str__()
                else:
                    if attachment:
                        title = f"Message Attachment"
                        url = ctx.message.jump_url
                        image_url = ctx.message.attachments[0].url
                    else:
                        title = str(member or ctx.author)
                        url = None
                        image_url = (member or ctx.author).avatar_url_as(format="png").__str__()

                raw_image = await self.read_image(image_url)

                process_time, image = await self.timer(function(raw_image, loop=self.bot.loop))

                embed = discord.Embed(
                    title=title,
                    url=url,
                    color=self.bot.color
                ).set_image(
                    url=f"attachment://{ctx.command.name}.png"
                ).set_footer(
                    text=f"Requested by {ctx.author} | Processed in {round(process_time * 1000, 3)}ms",
                    icon_url=ctx.author.avatar_url_as(format="png", size=64).__str__()
                )

                await ctx.send(
                    embed=embed,
                    file=discord.File(image, filename=f"{ctx.command.name}.png")
                )

            self.bot.add_command(callback)

    @staticmethod
    def typing(function):
        async def decorator(ctx, *args, **kwargs):
            async with ctx.typing():
                return await function(ctx, *args, **kwargs)
        return decorator

    @staticmethod
    async def timer(function):
        start = time.perf_counter()
        result = await function
        end = time.perf_counter()
        return end - start, result

    async def read_image(self, url: str):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        async with self.session.get(url) as response:
            image = io.BytesIO(await response.read())
            image.seek(0)
        return image
