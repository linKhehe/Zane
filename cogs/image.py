from io import BytesIO
import functools
import time
import math

from wand.image import Image as WandImage
from wand.color import Color as WandColor
from discord.ext import commands
import aiohttp
import discord

from utils.flags import parse_flags


class Color(WandColor):
    """
    A little subclass of wand.color.Color

    Adds functionality for ascii art.
    """

    def __init__(self, *args, **kwargs):
        self.ascii_characters = {
            300: "@",
            275: "#",
            250: ";",
            225: "+",
            200: "=",
            175: ":",
            150: "-",
            125: "\"",
            100: "'",
            75: ",",
            50: ".",
            25: " ",
            0: " "
        }
        super().__init__(*args, **kwargs)

    @property
    def ascii_character(self):
        value = self.red + self.green + self.blue
        value *= 100
        return self.ascii_characters[int(math.ceil(value/ 25.) * 25)]

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
    def _ascii(image: Image, inverted: bool = False, brightness: int = 100, size: int = 62):
        """
        Converts image into an ascii art string.

        :param image: The :class Image: to convert to ascii.
        :param inverted: A :type bool: determining whether or not to invert.
        :param brightness: A :type int: determining the brightness.
        :param size: A :type int: determining the size.
        :return: A :type str: containing the art.
        """
        if inverted:
            image.negate()
        if brightness is not 100:
            image.modulate(brightness=brightness)
        if size > 62:
            size = 62
        if size < 0:
            size = 2
        size = int(math.ceil(size / 2.) * 2)

        image.sample(size, int(size / 2))

        ascii_art = "```"

        for row in image:
            ascii_art += "\n"
            for col in row:
                with Color(str(col)) as c:
                    ascii_art += c.ascii_character

        ascii_art += "```"

        return ascii_art

    @staticmethod
    def _magic(image: Image):
        """
        Content aware scale an image. Made for use with _magic_command.
        :param Image:
        :return discord.File:
        """
        # overly content-aware-scale it
        image.liquid_rescale(
            width=int(image.width * 0.3),
            height=int(image.height * 0.3),
            delta_x=1.75,
            rigidity=0
        )
        image.liquid_rescale(
            width=int(image.width * 1.3),
            height=int(image.height * 1.3),
            delta_x=1.75,
            rigidity=0
        )

        image.resize(256, 256)

        return image.to_discord_file("magik.png")

    @staticmethod
    def _invert(image: Image):
        """
        Invert an image. Made for use with _invert_command.
        :param Image:
        :return discord.File:
        """
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
    async def _magic_command(self, ctx, member: discord.Member = None):
        """
        Content aware scale, also known as magic, a member's profile picture.
        If the member parameter is not fulfilled, the selected member will be you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)
        start = time.perf_counter()

        avatar_url = member.avatar_url_as(format="png", size=512)
        image = await Image.from_link(avatar_url)

        executor = functools.partial(self._magic, image)

        # keep in mind that the output of _magic is ...
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
    @commands.cooldown(
        rate=1,
        per=6,
        type=commands.BucketType.user
    )
    async def _invert_command(self, ctx, member: discord.Member = None):
        """
        Invert a member's profile picture.
        If the member parameter is not fulfilled, the selected member will be you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)
        start = time.perf_counter()

        avatar_url = member.avatar_url_as(format="png", size=256)
        image = await Image.from_link(avatar_url)

        # check whether or not the avatar is a gif
        # assign either _invert_gif or _invert depending on image.animation
        executor = functools.partial(self._invert, image)

        # keep in mind that the output of _magic is ...
        # Image.to_discord_file so we can send them right away.
        file = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(
        name="ascii",
        aliases=[
            "asciify",
            "asciiart"
        ]
    )
    async def _ascii_command(self, ctx, member: discord.Member = None, *flags: commands.clean_content):
        """
        Convert a member's avatar into ascii art.
        If the member parameter is not fulfilled, it will select you.

        Optional Flags:
            -i , --invert Invert the image.
            -b=100, --brightness=100 Change the brightness of the starting image.
            -s=62, --size=62 Change the size of the ascii art. Min is 2 max is 62.

        Example Flag Usage:
            ascii [member] -i --brightness=100 -s=62
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)
        start = time.perf_counter()

        invert = False
        brightness = 100
        size = 62

        flags = parse_flags(flags)

        if flags is not None:
            if "i" in flags.keys():
                invert = flags["i"]
            if "invert" in flags.keys():
                invert = flags["invert"]

            if "b" in flags.keys():
                brightness = flags["b"]
            if "brightness" in flags.keys():
                brightness = flags["brightness"]

            if brightness > 300:
                raise commands.BadArgument("A passed flag was invalid.\nThe maximum value for brightness is 300.")
            elif brightness < 0:
                raise commands.BadArgument("A passed flag was invalid.\nThe minimum value for brightness is 0.")

            if "s" in flags.keys():
                size = flags["s"]
            if "size" in flags.keys():
                size = flags["size"]

            if type(size) is not int:
                raise commands.BadArgument("A passed flag was invalid.\nThe size flag is an whole number.")
            elif size > 62:
                raise commands.BadArgument("A passed flag was invalid.\nThe maximum value for size is 62.")
            elif size < 2:
                raise commands.BadArgument("A passed flag was invalid.\nThe minimum value for size is 2.")

        avatar_url = member.avatar_url_as(format="png", size=256)
        image = await Image.from_link(avatar_url)

        executor = functools.partial(self._ascii, image, invert, brightness, size)
        ascii_art = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        await ctx.send(f"*{duration}ms*\n{ascii_art}")

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)


def setup(bot):
    bot.add_cog(Imaging(bot))
