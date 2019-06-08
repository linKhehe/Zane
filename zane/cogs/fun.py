import random

from discord.ext import commands

from zane import utils


class Fun(commands.Cog):

    OWO_TRANS = str.maketrans({
        "o": "owo",
        "O": "OwO",
        "r": "w",
        "R": "W",
        "l": "y",
        "L": "Y"
    })

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mock(self, ctx, phrase: str = None):
        """MocK somEONes MessAGE"""
        if phrase is None:
            phrase = (await utils.get_last_message(ctx.channel, ctx.message)).content

        await ctx.send("".join(random.choice([p.upper, p.lower])() for p in phrase))

    @commands.command()
    async def owo(self, ctx, phrase: commands.clean_content = None):
        """OwO ify a message i wove yowou"""
        if phrase is None:
            phrase = (await utils.get_last_message(ctx.channel, ctx.message)).clean_content

        await ctx.send(phrase.translate(self.OWO_TRANS))


def setup(bot):
    bot.add_cog(Fun(bot))
