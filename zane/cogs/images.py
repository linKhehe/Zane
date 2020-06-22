import aiohttp
import io

import discord
from discord.ext import commands

import zane.imageops as imageops


session = aiohttp.ClientSession()


async def save_image(url: str):
    async with session.get(url) as get:
        return io.BytesIO(await get.read())


def before_invoke(func):
    async def wrapper(ctx, member=None):
        await ctx.trigger_typing()

        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        elif member is not None:
            url = str(member.avatar_url_as(format="png"))
        else:
            url = str(ctx.author.avatar_url_as(format="png"))

        ctx.image = await save_image(url)

        await func(ctx, member)
    return wrapper




class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        command_names = ["magic", "deepfry", "emboss",
                         "vaporwave", "floor", "concave",
                         "convex", "invert", "lsd",
                         "posterize", "grayscale", "bend",
                         "edge", "gay", "sort",
                         "sobel", "shuffle", "swirl",
                         "polaroid", "arc"]

        for name in command_names:
            @commands.command(name=name)
            @before_invoke
            async def callback(ctx, member: discord.Member = None):
                await ctx.send(file=discord.File(await getattr(imageops, ctx.command.name)(ctx.image), "generated.png"))
            self.bot.add_command(callback)


def setup(bot):
    bot.add_cog(Images(bot))
