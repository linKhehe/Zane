from io import BytesIO
import functools
import time
import math

from wand.image import Image as WandImageBase
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
        return self.ascii_characters[int(math.ceil(value / 25.) * 25)]


class WandImage(WandImageBase):
    """
    A little custom version of wand.image.WandImage.

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

    async def _image_function_on_link(self, link: str, image_function):
        start = time.perf_counter()

        image = await WandImage.from_link(link)

        executor = functools.partial(image_function, image)

        file = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        return file, duration

    @staticmethod
    def _wasted(image: WandImage):
        """
        Add the wasted image on top of the provided image.

        :param image:
        :return:
        """
        with WandImage(filename="assets/wasted.png") as wasted:
            with image:
                image.composite(wasted, int(wasted.width / 2), -200)
                ret = image.to_discord_file("wasted.png")

        return ret

    @staticmethod
    def _ascii(image: WandImage, inverted: bool = False, brightness: int = 100, size: int = 62):
        """
        Converts image into an ascii art string.

        :param image: The :class WandImage: to convert to ascii.
        :param inverted: A :type bool: determining whether or not to invert.
        :param brightness: A :type int: determining the brightness.
        :param size: A :type int: determining the size.
        :return: A :type str: containing the art.
        """
        with image:
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
    def _magic(image: WandImage):
        """
        Content aware scale an image. Made for use with _magic_command.
        :param WandImage:
        :return discord.File:
        """
        # overly content-aware-scale it
        with image:
            image.liquid_rescale(
                width=int(image.width * 0.5),
                height=int(image.height * 0.5),
                delta_x=1,
                rigidity=0
            )
            image.liquid_rescale(
                width=int(image.width * 1.5),
                height=int(image.height * 1.5),
                delta_x=2,
                rigidity=0
            )

            image.resize(256, 256)

            ret = image.to_discord_file("magik.png")

        return ret

    @staticmethod
    def _invert(image: WandImage):
        """
        Invert an image. Made for use with _invert_command.
        :param WandImage:
        :return discord.File:
        """
        with image:
            image.negate()
            ret = image.to_discord_file(filename="inverted.png")

        return ret

    # Everything from here on is a command.
    # Commands are named with _name_command

    @staticmethod
    def _expand(image: WandImage):
        """
        Expand an image using a bit of seam-carving.
        :param image:
        :return discord.File:
        """
        with image:
            image.liquid_rescale(int(image.width * 0.5), image.height)
            image.liquid_rescale(int(image.width * 3.5), image.height, delta_x=1)
            ret = image.to_discord_file("expand_dong.png")

        return ret


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

        file, duration = await self._image_function_on_link(member.avatar_url_as(format="png", size=512), self._magic)

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

        file, duration = await self._image_function_on_link(member.avatar_url_as(format="png", size=512), self._invert)

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

        ascii_art, duration = await self._image_function_on_link(
            member.avatar_url_as(format="png", size=64), self._ascii
        )

        await ctx.send(f"*{duration}ms*\n{ascii_art}")

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(
        name="expand",
        aliases=[
            'expnd',
            'expanddong'
        ]
    )
    @commands.cooldown(
        rate=1,
        per=20,
        type=commands.BucketType.user
    )
    async def _expand_command(self, ctx, member: discord.Member = None):
        """
        Expand a member's profile picture.
        If the member parameter is not fulfilled, the selected member will be you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)

        file, duration = await self._image_function_on_link(member.avatar_url_as(format="png", size=256), self._expand)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)


def setup(bot):
    bot.add_cog(Imaging(bot))
