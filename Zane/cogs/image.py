from io import BytesIO
import functools
import time
import math

from discord.ext import commands
import aiohttp
import discord

from utils.flags import parse_flags
from utils.image import Image as WandImage
from utils.image import Color as WandColor


class Imaging:
    """
    This cog adds image manipulation functionality for both GIFs and static images.
    """

    def __init__(self, bot):
        self.bot = bot

    async def _image_function_on_link(self, link: str, image_function, *args):
        start = time.perf_counter()

        image = await WandImage.from_link(link)

        executor = functools.partial(image_function, image)
        if args:
            executor = functools.partial(image_function, image, *args)

        file = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        return file, duration
    
    async def _image_function(self, image: WandImage, image_function, *args):
        start = time.perf_counter()

        executor = functools.partial(image_function, image)
        if args:
            executor = functools.partial(image_function, image, *args)

        file = await self.bot.loop.run_in_executor(None, executor)

        end = time.perf_counter()
        duration = round((end - start) * 1000, 2)

        return file, duration

    @staticmethod
    def _deepfry(image: WandImage):
        """
        Deepfry an image.

        :param image:
        :return:
        """
        with image:
            image.compression_quality = 2
            image.modulate(saturation=700)
            ret = image.to_discord_file("deep-fry.png")

        return ret

    @staticmethod
    def _thonk(image: WandImage):
        """
        Add the thonk hand image on top of the provided image.

        :param image:
        :return:
        """
        with WandImage(filename="assets/thonk_hand.png") as thonk:
            with image:
                thonk.resize(image.width, image.height)
                image.composite(thonk, 0, 0)
                ret = image.to_discord_file("thonk.png")

        return ret

    @staticmethod
    def _wasted(image: WandImage):
        """
        Add the wasted image on top of the provided image.

        :param image:
        :return:
        """
        with WandImage(filename="assets/wasted.png") as wasted:
            with image:
                wasted.resize(image.width, image.height)
                image.composite(wasted, 0, 0)
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
        :param image:
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
        :param image:
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
            member.avatar_url_as(format="png", size=64), self._ascii, invert, brightness, size
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

    @commands.command(
        name="wasted",
        aliases=[
            'gta',
            'gtawasted'
        ]
    )
    @commands.cooldown(
        rate=1,
        per=20,
        type=commands.BucketType.user
    )
    async def _wasted_command(self, ctx, member: discord.Member = None):
        """
        Add a gta wasted picture to a member's profile picture.
        If the member parameter is not fulfilled, the selected member will be you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)

        file, duration = await self._image_function_on_link(member.avatar_url_as(format="png", size=512), self._wasted)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(
        name="thonk",
        aliases=[
            'thonkify',
            'thonking',
            'think',
            'thinkify',
            'thinking'
        ]
    )
    @commands.cooldown(
        rate=1,
        per=20,
        type=commands.BucketType.user
    )
    async def _thonk_command(self, ctx, member: discord.Member = None):
        """
        Add a thonk hand to a member's profile picture.
        If the member parameter is not fulfilled, the selected member will be you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)

        file, duration = await self._image_function_on_link(member.avatar_url_as(format="png", size=512), self._thonk)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(
        name="deepfry",
        aliases=[
            "deep-fry",
            "deepfryer"
        ]
    )
    @commands.cooldown(
        rate=1,
        per=20,
        type=commands.BucketType.user
    )
    async def _deep_fry_command(self, ctx, member: discord.Member = None):
        """
        Deepfry a member's profile picture.
        If the member parameter is not fulfilled, the selected member will be you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)

        file, duration = await self._image_function_on_link(member.avatar_url_as(format="jpeg", size=512), self._deepfry)

        await ctx.send(f"*{duration}ms*", file=file)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(
        name="effects",
        aliases=[
            "effect",
            "edit",
            "stack"
        ]
    async def _effect_stack_command(self, ctx, member: discord.Member, *effect_names):
        """
        This command allows you to stack multiple image effects, all the effects found in the other commands, on to one image.
        The list of args can be found by replacing the member argument with "list" or "all". If the member you are trying to select uses one of those reserved terms, just tag them or use their user id.
        """
        await ctx.message.add_reaction(self.bot.loading_emoji)
        
        effects = []
        
        for effect_name in effect_names:
            effect_name = effect_name.lower()
            
            if effect_name in ["magic", "magik", "magick"]:
                effects.append(self._magic)
            elif effect_name in ["invert", "negate"]:
                effects.append(self._invert)
            elif effect_name in ["invert", "negate"]:
                effects.append(self._invert)
            elif effect_name in ["expand", "expand_dong"]:
                effects.append(self._expand)
            elif effect_name in ["wasted", "gta", "gtawasted"]:
                effects.append(self._wasted)
            elif effect_name in ["think", "thinking", "thonk", "thonking", "thinkify", "thonkify"]:
                effects.append(self._thonk)
            elif effect_name in ["deepfry", "deep-fry"]:
                effects.append(self._deepfry)
            else:
                raise commands.BadArgument(f"I couldn't find an effect by the name \"{effect_name}\". Use effect list for a list of effects")
        
        effects = list(set(effects))
        total_ms = 0
        
        for i, effect in enumerate(effects):
            if i == 0:
                image = await Image.from_link(ctx.author.avatar_url_as(format="png", size=256))
            b_io, ms = await self._image_function(image, effect)
            image = WandImage.from_bytes_io(b_io)
            total_ms += ms
        
        file = image.to_discord_file("stacked_effects.png")
        
        await ctx.send(f"*{total_ms}*", file=file)
        
        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)
            
                
        
def setup(bot):
    bot.add_cog(Imaging(bot))
