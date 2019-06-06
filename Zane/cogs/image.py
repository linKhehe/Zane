from io import BytesIO

import aiohttp
import discord
from discord.ext import commands

from zane import imageops


class ImageManip(commands.Cog, name="Image Manipulation",
                 command_attrs=dict(cooldown=commands.Cooldown(1, 3, commands.BucketType.member))):

    LOADING_EMOTE = "a:anim_discord_loading:514917324709429344"

    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def create_session(self):
        self.session = aiohttp.ClientSession()

    async def get_image_bytes(self, image_url: str):
        if self.session is None:
            await self.create_session()

        async with self.session.get(image_url) as response:
            b = BytesIO(await response.read())

        return b

    async def get_avatar_bytes(self, member: discord.Member, *args, **kwargs):
        return await self.get_image_bytes(member.avatar_url_as(*args, **kwargs, size=256, format="png"))

    async def generate_and_send_image(self, author, target, channel, manip_func, *args, **kwargs):
        img = await manip_func(*args, **kwargs)
        embed = discord.Embed(
            title=f"{manip_func.__name__.capitalize()} on {target}",
            color=self.bot.color
        ).set_image(
            url="attachment://image.png"
        ).set_footer(
            text=f"Requested by {author}",
            icon_url=author.avatar_url_as(format="png", size=16)
        )
        await channel.send(embed=embed, file=discord.File(img, "image.png"))

    async def cog_before_invoke(self, ctx):
        try:
            await ctx.message.add_reaction(self.LOADING_EMOTE)
        except discord.Forbidden:
            pass

    async def cog_after_invoke(self, ctx):
        try:
            await ctx.message.remove_reaction(self.LOADING_EMOTE, ctx.guild.me)
        except discord.Forbidden:
            pass

    @commands.command()
    async def bend(self, ctx, *, member: discord.Member = None):
        """Bender Bending Rodríguez."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.bend, await self.get_avatar_bytes(member))

    @commands.command()
    async def concave(self, ctx, *, member: discord.Member = None):
        """View a user's profile picture through a concave lens."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.concave, await self.get_avatar_bytes(member))

    @commands.command()
    async def convex(self, ctx, *, member: discord.Member = None):
        """View a user's profile picture through a convex lens."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.convex, await self.get_avatar_bytes(member))

    @commands.command()
    async def deepfry(self, ctx, *, member: discord.Member = None):
        """Deepfry a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.deepfry, await self.get_avatar_bytes(member))

    @commands.command()
    async def desat(self, ctx, member: discord.Member = None, threshold: int = 1):
        """Desaturate a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.desat, await self.get_avatar_bytes(member), threshold)

    @commands.command()
    async def edge(self, ctx, *, member: discord.Member = None):
        """Make a user's profile picture edgy."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.edge, await self.get_avatar_bytes(member))

    @commands.command()
    async def emboss(self, ctx, *, member: discord.Member = None):
        """Emboss a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.emboss, await self.get_avatar_bytes(member))

    @commands.command()
    async def floor(self, ctx, *, member: discord.Member = None):
        """Make a user's profile picture the floor."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.floor, await self.get_avatar_bytes(member))

    @commands.command()
    async def gay(self, ctx, *, member: discord.Member = None):
        """Make a user gay."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.gay, await self.get_avatar_bytes(member))

    @commands.command()
    async def grayscale(self, ctx, *, member: discord.Member = None):
        """Make a user's profile picture grayscale."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.grayscale, await self.get_avatar_bytes(member))

    @commands.command()
    async def invert(self, ctx, *, member: discord.Member = None):
        """Invert a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.invert, await self.get_avatar_bytes(member))

    @commands.command()
    async def lsd(self, ctx, *, member: discord.Member = None):
        """Take some LSD and view a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.lsd, await self.get_avatar_bytes(member))

    @commands.command()
    async def magic(self, ctx, *, member: discord.Member = None):
        """Heavily content aware scale a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.magic, await self.get_avatar_bytes(member))

    @commands.command()
    async def posterize(self, ctx, *, member: discord.Member = None):
        """Posterize a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.posterize, await self.get_avatar_bytes(member))

    @commands.command()
    async def sat(self, ctx, member: discord.Member = None, threshold: int = 1):
        """Saturate a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.sat, await self.get_avatar_bytes(member), threshold)

    @commands.command()
    async def shuffle(self, ctx, *, member: discord.Member = None):
        """Shuffle the user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.shuffle, await self.get_avatar_bytes(member))

    @commands.command()
    async def sobel(self, ctx, *, member: discord.Member = None):
        """Sobel filter a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.sobel, await self.get_avatar_bytes(member))

    @commands.command()
    async def sort(self, ctx, *, member: discord.Member = None):
        """Sort the pixels in a user's profile picture."""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.sort, await self.get_avatar_bytes(member))

    @commands.command()
    async def vaporwave(self, ctx, *, member: discord.Member = None):
        """vvvaaapppooorrrwwwaaavvveee mmmeee dddaaaddddddyyy!!!"""
        member = member if member is not None else ctx.author
        await self.generate_and_send_image(ctx.author, member, ctx.channel, imageops.vaporwave, await self.get_avatar_bytes(member))
        
    @commands.command()
    async def ascii(self, ctx, *, member: discord.Member = None):
        """Make a user's profile picture ascii-art."""
        member = member if member is not None else ctx.author
        art = await imageops.ascii_art(await self.get_avatar_bytes(member))

        async with self.session.post("https://wastebin.travitia.xyz/documents", data=art) as post:
            key = (await post.json())["key"]

        await ctx.send(f"{ctx.author.mention}, https://wastebin.travitia.xyz/{key}.txt")


def setup(bot):
    bot.add_cog(ImageManip(bot))
