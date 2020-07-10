import io
import time
import typing

import aiohttp
import discord
from discord.ext import commands
from wand.exceptions import MissingDelegateError

from . import manipulation
from . editor import Editor


class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.session = None

        for f in [getattr(manipulation, f) for f in manipulation.__all__]:
            @commands.command(name=f.__name__, help=f.__doc__)
            async def callback(_, ctx, *, member_or_emoji: typing.Union[discord.Member, discord.PartialEmoji] = None):
                async with ctx.typing():
                    function = getattr(manipulation, ctx.command.name)

                    if isinstance(member_or_emoji, discord.PartialEmoji):
                        embed = discord.Embed(
                            title=f"Emoji {member_or_emoji.name}",
                            url=member_or_emoji.url.__str__(),
                            color=self.bot.color
                        )
                        image_url = member_or_emoji.url.__str__()
                    else:
                        if ctx.message.attachments:
                            embed = discord.Embed(
                                title=f"Message Attachment",
                                url=ctx.message.jump_url,
                                color=self.bot.color
                            )
                            image_url = ctx.message.attachments[0].url
                        else:
                            embed = discord.Embed(
                                title=str(member_or_emoji or ctx.author),
                                color=self.bot.color
                            )
                            image_url = (member_or_emoji or ctx.author).avatar_url_as(format="png").__str__()

                    raw_image = await self.read_image(image_url)

                    if raw_image.__sizeof__() > 40_000_000:
                        return await ctx.send("File is too large.")

                    try:
                        process_time, image = await self.timer(function(raw_image, loop=self.bot.loop))
                    except (MissingDelegateError, ValueError):
                        return await ctx.send("Invalid file format.")

                    raw_image.close()

                    embed.set_image(
                        url=f"attachment://{ctx.command.name}.png"
                    ).set_footer(
                        text=f"Requested by {ctx.author} | Processed in {round(process_time * 1000, 3)}ms",
                        icon_url=ctx.author.avatar_url_as(format="png", size=64).__str__()
                    )

                    await ctx.send(
                        embed=embed,
                        file=discord.File(image, filename=f"{ctx.command.name}.png")
                    )

            callback.cog = self
            self.bot.add_command(callback)

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

    @commands.command()
    async def edit(self, ctx, *,
                   member_or_emoji: typing.Union[discord.Member, discord.PartialEmoji] = None):
        image = await self.get_image_contextually(ctx, member_or_emoji)
        menu = Editor(self.upload_channel, image, self.bot.loop)
        await menu.start(ctx)

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
