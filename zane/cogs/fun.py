import random

from discord.ext import commands


class Fun(commands.Cog):

    OWO_MAP = {
        "r": "w",
        "l": "y",
        "R": "Ww",
        "L": "Y"
    }

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def get_last_content(before, channel):
        phrase = ""
        limit = 0
        while phrase == "":
            if limit > 5:
                return None
            limit += 1
            messages = await channel.history(limit=limit, before=before).flatten()
            message = messages[len(messages) - 1]
            phrase = message.clean_content
        return phrase

    @commands.command(hidden=True, name="z.")
    async def zdot(self, ctx):
        await ctx.send("z.z.")


def setup(bot):
    bot.add_cog(Fun(bot))
