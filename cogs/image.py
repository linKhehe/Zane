from io import BytesIO
import functools

from wand.image import Image as WandImage
import aiohttp
import discord
from discord.ext import commands


class Image(WandImage):

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

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _magic_gif(image: Image, multiplier: float = 1.75):
        with Image() as output:
            image.sample(200, 200)
            for frame in image.sequence:
                frame.sample(200, 200)
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
        image.sample(400, 400)
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
        return image.to_discord_file("magik.png")

    @commands.command(
        name="magic",
        aliases=[
            'magic',
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

        avatar_url = member.avatar_url_as(static_format="png")
        image = await Image.from_link(avatar_url)

        if image.animation:
            executor = functools.partial(self._magic_gif, image)
        else:
            executor = functools.partial(self._magic, image)

        file = await self.bot.loop.run_in_executor(None, executor)

        await ctx.send(file=file)

def setup(bot):
    bot.add_cog(Imaging(bot))
