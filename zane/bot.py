import random
from traceback import print_exc

from discord.ext import commands

import zane


class Zane(commands.AutoShardedBot):

    def __init__(self, *args, **kwargs):
        zane.logger.info("Zane initialization started.")

        self.token = kwargs.pop("token")
        self.runtime_cogs = kwargs.pop("cogs")

        self.redis_url = kwargs.pop("redis_url")
        self.redis_pass = kwargs.pop("redis_pass")

        super().__init__(*args, **kwargs)

        zane.logger.info("Zane initialized.")

    @property
    def color(self):
        return random.randint(0, 16_777_215)

    def run(self, *args, **kwargs):
        zane.logger.info("The blocking run is starting")
        for cog in self.runtime_cogs:
            try:
                self.load_extension(cog)
                zane.logger.info(f"Loaded {cog}")
            except:
                zane.logger.critical(f"There was a critical error loading extension {cog}; traceback printed below.")
                print_exc()
        zane.logger.info("Cog loading done. Connecting to Discord.")
        super().run(self.token, *args, **kwargs)

    async def on_connection(self):
        zane.logger.info("Connected to Discord.")

    async def on_disconnect(self):
        zane.logger.info("Disconnected from Discord.")

    async def on_ready(self):
        zane.logger.info("The bot is now ready.")

    async def on_guild_join(self, guild):
        zane.logger.info(f"Joined a new guild, (Name: {guild.name}, Members: {len(guild.members)})")

    async def on_guild_remove(self, guild):
        zane.logger.info(f"Left a guild, (Name: {guild.name}, Members: {len(guild.members)})")

    async def on_command(self, ctx):
        zane.logger.debug(f"Command invoked with {ctx.message.content} {repr(ctx.message)}")

    async def on_message(self, message):
        if message.author.id == 246938839720001536:
            return
        await self.process_commands(message)

    @classmethod
    def from_config(cls, config):
        kwargs = {}
        for attr in dir(config):
            if attr.isupper():
                kwargs.update({attr.lower(): getattr(config, attr)})
        return cls(**kwargs)
