import io
import time
import typing

import aiohttp
import discord
from discord.ext import commands
from wand.exceptions import MissingDelegateError, BlobError, BlobFatalError

from . import manipulation


class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = None

        def callback_builder(name: str):
            async def function(_, ctx, *, member_or_emoji: typing.Union[discord.Member, discord.PartialEmoji] = None):
                async with ctx.typing():
                    raw_image = await self.get_image_contextually(ctx, member_or_emoji)

                    if raw_image.__sizeof__() > 40_000_000:
                        return await ctx.send("File is too large.")

                    try:
                        process_time, image = await self.timer(getattr(manipulation, function.__name__)(raw_image))
                    except (MissingDelegateError, ValueError, BlobError, BlobFatalError):
                        return await ctx.send("Invalid file format.")

                    raw_image.close()

                    embed = discord.Embed(
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

            function.__name__ = name
            function.__doc__ = getattr(manipulation, name).__doc__
            return function

        for manipulation_function in manipulation.__all__:
            callback = callback_builder(manipulation_function)
            command = commands.Command(callback)
            command.cog = self
            self.bot.add_command(command)

    @commands.command()
    async def ascii(self, ctx, *, member_or_emoji: typing.Union[discord.Member, discord.PartialEmoji] = None):
        """Make ascii art out of an image."""
        async with ctx.typing():
            raw_image = await self.get_image_contextually(ctx, member_or_emoji)

            if raw_image.__sizeof__() > 40_000_000:
                return await ctx.send("File is too large.")

            try:
                process_time, art = await self.timer(manipulation.ascii(raw_image))
            except (MissingDelegateError, ValueError, BlobError, BlobFatalError):
                return await ctx.send("Invalid file format.")

            try:
                async with self.session.post("https://mystb.in/documents", data=art) as post:
                    key = (await post.json())["key"]
                await ctx.send(f"{ctx.author.mention} https://mystb.in/{key}.txt in {round(process_time * 1000, 3)}ms")
            except KeyError:
                await ctx.send("Sorry. I was able to caclulate that image but it was too large for my text-host.")
                return
            except aiohttp.ContentTypeError:
                await ctx.send("Sorry. I was able to caclulate that image but it was too large for my text-host.")
                return

    @commands.command()
    async def discord_ascii(self, ctx, *, member_or_emoji: typing.Union[discord.Member, discord.PartialEmoji] = None):
        """Make ascii art that fits in a discord message."""
        async with ctx.typing():
            raw_image = await self.get_image_contextually(ctx, member_or_emoji)

            if raw_image.__sizeof__() > 40_000_000:
                return await ctx.send("File is too large.")

            try:
                process_time, art = await self.timer(manipulation.discord_ascii(raw_image))
            except (MissingDelegateError, ValueError, BlobError, BlobFatalError):
                return await ctx.send("Invalid file format.")

            await ctx.send(f">>> ```{art}```")

    @property
    def upload_channel(self):
        return self.bot.get_guild(663063922085068810).get_channel(729966231716626505)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.BadUnionArgument):
            return await ctx.send(f"{ctx.command.name.capitalize()} only takes members and guild-emoji as arguments.")
        raise error

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

    async def get_image_contextually(self, ctx, member_or_emoji):
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        else:
            if isinstance(member_or_emoji, discord.Member):
                url = str(member_or_emoji.avatar_url_as(format="png"))
            elif isinstance(member_or_emoji, discord.PartialEmoji):
                url = str(member_or_emoji.url)
            else:
                url = str(ctx.author.avatar_url_as(format="png"))

        return await self.read_image(url)
