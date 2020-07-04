from discord.ext import commands
import jishaku


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """See my ping to Discord."""
        await ctx.send(f"pinggggggieeeeee {round(self.bot.latency * 1000, 2)}")

    @commands.command()
    async def source(self, ctx):
        """View my source code."""
        await ctx.send("<https://github.com/ir-3/Zane")


def setup(bot):
    bot.add_cog(Info(bot))
