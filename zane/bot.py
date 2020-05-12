import traceback

from discord.ext import commands


class Zane(commands.Bot):

    def __init__(self, config):
        prefixes = getattr(config, "command_prefix", None)
        if type(prefixes) is not list:
            prefixes = [prefixes]

        super().__init__(
            command_prefix=commands.when_mentioned_or(*prefixes),
            description=getattr(config, "description", None),
            owner_id=getattr(config, "owner_id", None),
            owner_ids=getattr(config, "owner_ids", None)
        )

        self.config = config
        self.color = getattr(config, "color", 0x0000FF)
        self.db = None

    def run(self):
        cogs = ["zane.cogs." + cog for cog in getattr(self.config, "cogs", [])]
        if getattr(self.config, "load_jishaku", True):
            cogs.append("jishaku")

        for cog in cogs:
            try:
                self.load_extension(cog)
            except:
                print(f"Error loading {cog}, traceback below.")
                traceback.print_exc()

        super().run(getattr(self.config, "token", None))
