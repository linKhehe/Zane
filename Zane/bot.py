import traceback

from discord.ext import commands


class Bot(commands.AutoShardedBot):

    def __init__(self):
        self.prefixes = ["za ", "za."]
        self.color = 0x00ff00
        self.owners = [217462890364403712]

        self.initial_cogs = [
            "jishaku",
            "zane.cogs.fun",
            "zane.cogs.utility",
            "zane.cogs.zane",
            "zane.cogs.image"
        ]

        super().__init__(command_prefix=commands.when_mentioned_or(*self.prefixes))

    async def on_ready(self):
        print("Initiated.")

    def run(self, *args, **kwargs):
        for cog in self.initial_cogs:
            try:
                self.load_extension(cog)
            except Exception:
                print(f"Error loading {cog}...")
                traceback.print_exc()
        super().run(*args, **kwargs)
