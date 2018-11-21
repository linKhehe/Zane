from io import BytesIO
import functools
import time

# the weird import is so i can subclass it without
# having a weird name for my image class.
from wand.image import Image as WandImage
from wand.api import library
from wand.compat import binary
import aiohttp
import discord
from discord.ext import commands


class Image(WandImage):
    """
    A little custom version of wand.image.Image.

    Adds functionality such as...

        from_link(link)
            - For creating an image from a link using aiohttp.

        to_bytes_io()
            - For saving an image to a BytesIO object.

        to_discord_file()
            - For saving an image to a discord.File object.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    async def from_link(cls, link: str = None):
        if link is None:
            return cls().blank(width=0, height=0)

        link.strip("<>")

        # Start a client session and get the link. Read the link to response variable.
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                response = await response.read()

        # Convert the response the a byte object
        byte_response = BytesIO(response)
        byte_response.seek(0)

        # Start an image object with the bytes.
        image = cls(file=byte_response)

        return image

    def to_bytes_io(self):
        bytes_io = BytesIO()

        # save self to the bytes io and seek to the beginning
        self.save(file=bytes_io)
        bytes_io.seek(0)
        return bytes_io

    def to_discord_file(self, filename: str):
        bytes_io = self.to_bytes_io()
        file = discord.File(bytes_io, filename=filename)
        return file


class Imaging:
    """
    This cog adds image manipulation functionality for both GIFs and static images.
    """

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _magic_gif(image: Image, multiplier: float = 1.75):
        # iterate through each frame in the input image
        # apply content aware scale and append it to the
        # end of the output image
        with Image() as output:
            with image:
                for frame in image.sequence:
                    frame.liquid_rescale(
                        width=int(image.width * 0.4),
                        height=int(image.height * 0.4),
                        delta_x=multiplier,
                        rigidity=0
                    )
                    frame.liquid_rescale(
                        width=int(image.width * 1.2),
                        height=int(image.height * 1.2),
                        delta_x=multiplier,
                        rigidity=0
                    )
                    output.sequence.append(frame)
                return output.to_discord_file("magic.gif")

    @staticmethod
    def _magic(image: Image, multiplier: float = 1.75):
        # overly content-aware-scale it
        image.liquid_rescale(
            width=int(image.width * 0.4),
            height=int(image.height * 0.4),
            delta_x=multiplier,
            rigidity=0
        )
        image.liquid_rescale(
            width=int(image.width * 1.2),
            height=int(image.height * 1.2),
            delta_x=multiplier,
            rigidity=0
        )

        image.sample(256, 256)

        return image.to_discord_file("magik.png")

    @staticmethod
    def _invert_gif(image: Image):
        # Negate every frame and append it to out
        with Image() as out:
            for frame in image.sequence:
                frame.negate()
                out.sequence.append(frame)

            return out.to_discord_file(filename="inverted.gif")

    @staticmethod
    def _invert(image: Image):
        image.negate()

        return image.to_discord_file(filename="inverted.png")

    # Everything from here on is a command.
    # Commands are named with _name_command

    @commands.command(
        name="magic",
        aliases=[
            'magick',
            'magik'
        ]
    )
    @commands.cooldown(
        rate=1,
        per=20,
        type=commands.BucketType.user
    )
    async def _magic_command(self, ctx, member: discord.Member = None, multiplier: float = 1.75):
        if multiplier > 15 or multiplier < 0:
            # TODO: Raise custom error
            return True

        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)
        start = time.perf_counter()

        avatar_url = member.avatar_url_as(static_format="png", size=256)
        image = await Image.from_link(avatar_url)

        # check whether or not the avatar is a gif
        # assign either _magic_gif or _magic depending on image.animation
        if image.animation:
            executor = functools.partial(self._magic_gif, image)
        else:
            executor = functools.partial(self._magic, image)

        # keep in mind that the output of both _magic and _magic_gif are ...
        # Image.to_discord_file so we can send them right away.
        file = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(
        name="invert",
        aliases=[
            'negate'
        ]
    )
    async def _invert_command(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        loading_reaction = await ctx.message.add_reaction(self.bot.loading_emoji)
        start = time.perf_counter()

        avatar_url = member.avatar_url_as(static_format="png", size=256)
        image = await Image.from_link(avatar_url)

        # check whether or not the avatar is a gif
        # assign either _invert_gif or _invert depending on image.animation
        if image.animation:
            executor = functools.partial(self._invert_gif, image)
        else:
            executor = functools.partial(self._invert, image)

        # keep in mind that the output of both _magic and _magic_gif are
        # Image.to_discord_file so we can send them right away.
        file = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)


def setup(bot):
    bot.add_cog(Imaging(bot))
