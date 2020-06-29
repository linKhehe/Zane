from discord.ext import commands


class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """See my ping to Discord."""
        await ctx.send(f"Who has ever cared about ping. Not once. Alas, mine is {round(self.bot.latency * 1000, 2)}ms.")

    @commands.command()
    async def source(self, ctx):
        """View my source code."""
        await ctx.send("<https://github.com/ir-3/Zane>")

    @commands.command(name="z.", hidden=True)
    async def zdot(self, ctx):
        await ctx.send("zaza")


def setup(bot):
    bot.add_cog(Info(bot))
