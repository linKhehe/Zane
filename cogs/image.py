from io import BytesIO

from wand.image import Image as WandImage
import aiohttp
import discord
from discord.ext import commands


class Image(WandImage):
    """A custom image object. Added functionality includes from_link...

    :param image: makes an exact copy of the ``image``
    :type image: :class:`Image`
    :param blob: opens an image of the ``blob`` byte array
    :type blob: :class:`bytes`
    :param file: opens an image of the ``file`` object
    :type file: file object
    :param filename: opens an image of the ``filename`` string
    :type filename: :class:`basestring`
    :param format: forces filename to  buffer. ``format`` to help
                   imagemagick detect the file format. Used only in
                   ``blob`` or ``file`` cases
    :type format: :class:`basestring`
    :param width: the width of new blank image or an image loaded from raw
                  data.
    :type width: :class:`numbers.Integral`
    :param height: the height of new blank imgage or an image loaded from
                   raw data.
    :type height: :class:`numbers.Integral`
    :param depth: the depth used when loading raw data.
    :type depth: :class:`numbers.Integral`
    :param background: an optional background color.
                       default is transparent
    :type background: :class:`wand.color.Color`
    :param resolution: set a resolution value (dpi),
                       useful for vectorial formats (like pdf)
    :type resolution: :class:`collections.Sequence`,
                      :Class:`numbers.Integral`
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
        self.save(file=bytes_io)
        bytes_io.seek(0)
        return bytes_io


class Imaging:

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Imaging(bot))
