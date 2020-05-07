import io

import aiohttp
import discord
from discord.ext import commands

from zane import imageops


class Images(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.color = self.bot.color
        self.session = None

        self.bot.loop.create_task(self.create_session())

    async def create_session(self, *args, **kwargs):
        self.session = aiohttp.ClientSession(*args, **kwargs)

    async def save_image(self, url: str):
        async with self.session.get(url) as get:
            return io.BytesIO(await get.read())

    async def cog_before_invoke(self, ctx):
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
        elif ctx.args[2] is not None:
            url = str(ctx.args[2].avatar_url)
        else:
            url = str(ctx.author.avatar_url)

        ctx.image = await self.save_image(url)

    @commands.command()
    async def magic(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.magic(ctx.image), "generated.png"))

    @commands.command()
    async def deepfry(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.deepfry(ctx.image), "generated.png"))

    @commands.command()
    async def emboss(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.emboss(ctx.image), "generated.png"))

    @commands.command()
    async def vaporwave(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.vaporwave(ctx.image), "generated.png"))

    @commands.command()
    async def floor(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.floor(ctx.image), "generated.png"))

    @commands.command()
    async def concave(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.concave(ctx.image), "generated.png"))

    @commands.command()
    async def convex(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.convex(ctx.image), "generated.png"))

    @commands.command()
    async def invert(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.invert(ctx.image), "generated.png"))

    @commands.command()
    async def lsd(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.lsd(ctx.image), "generated.png"))

    @commands.command()
    async def posterize(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.posterize(ctx.image), "generated.png"))

    @commands.command()
    async def grayscale(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.grayscale(ctx.image), "generated.png"))

    @commands.command()
    async def bend(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.bend(ctx.image), "generated.png"))

    @commands.command()
    async def edge(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.edge(ctx.image), "generated.png"))

    @commands.command()
    async def gay(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.gay(ctx.image), "generated.png"))

    @commands.command()
    async def sort(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.sort(ctx.image), "generated.png"))

    @commands.command()
    async def sobel(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.sobel(ctx.image), "generated.png"))

    @commands.command()
    async def shuffle(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.shuffle(ctx.image), "generated.png"))

    @commands.command()
    async def sphere(self, ctx, member: discord.Member = None):
        await ctx.send(file=discord.File(await imageops.sphere(ctx.image), "generated.png"))

    @commands.command()
    async def ascii(self, ctx, member: discord.Member = None):
        async with ctx.typing():
            art = await imageops.ascii_art(ctx.image)
            async with self.session.post("https://mystb.in/documents", data=art) as post:
                key = (await post.json())["key"]
            await ctx.send(f"https://mystb.in/{key}.txt")


def setup(bot):
    bot.add_cog(Images(bot))
