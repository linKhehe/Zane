import asyncio
import collections
import io

import discord
import typing
from discord.ext import menus
from discord.ext import commands

from . import manipulation


class Action:

    def __init__(self, image: io.BytesIO, image_url: str):
        self._image_bytes = image.getvalue()
        self.image_url = image_url

    @property
    def image(self) -> io.BytesIO:
        return io.BytesIO(self._image_bytes)


class Editor(menus.Menu):

    BUTTON_MAP = {
        "\N{REGIONAL INDICATOR SYMBOL LETTER M}": manipulation.magic,
        "\N{RIGHTWARDS ARROW WITH HOOK}": manipulation.rotate_right,
        "\N{LEFTWARDS ARROW WITH HOOK}": manipulation.rotate_left
    }

    def __init__(self, upload_channel: discord.TextChannel, initial_image: io.BytesIO, loop: asyncio.BaseEventLoop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.actions = collections.deque()
        self._image = None

        self.upload_channel = upload_channel
        self.image = initial_image
        self.loop = loop

        def callback_builder(name):
            async def callback(self: Editor, payload):
                manipulation_function = getattr(manipulation, callback.__name__)

                image = await manipulation_function(self.image, loop=loop)
                image_url = await self.upload(image)
                self.image = image

                self.actions.append(Action(image, image_url))

                await self.message.edit(embed=self.create_embed(image_url))

            callback.__name__ = name
            return callback

        for button, manipulation_function in self.BUTTON_MAP.items():
            self.add_button(menus.Button(
                button,
                callback_builder(manipulation_function.__name__)
            ))

    async def send_initial_message(self, ctx: commands.Context, channel) -> discord.Message:
        image_url = await self.upload(self.image)
        self.add_action(self.image, image_url)
        return await ctx.send(embed=self.create_embed(image_url))

    @menus.button("\N{CROSS MARK}")
    async def exit(self, payload):
        self.image.close()
        self.stop()

    @menus.button("\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}")
    async def undo(self, payload):
        if len(self.actions) < 2:
            return await self.alert("Can't Undo - Already at start")

        self.actions.pop()

        action = self.actions[-1]
        self.image = action.image
        await self.message.edit(embed=self.create_embed(action.image_url))

    async def alert(self, alert_message: str, delay: float = 5.0):
        await self.message.edit(content=alert_message)
        await asyncio.sleep(delay)
        await self.message.edit(content="")

    def add_action(self, image: io.BytesIO, image_url: str) -> None:
        self.actions.append(Action(image, image_url))

    @staticmethod
    def create_embed(image_url: str) -> discord.Embed:
        return discord.Embed().set_image(url=image_url)

    async def upload(self, image: io.BytesIO) -> str:
        file = discord.File(image, "edit.png")
        message = await self.upload_channel.send(file=file)
        return message.attachments[0].url.__str__()
