import discord
from discord.ext import commands
import humanize
import psutil


class Zane(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """View my ping."""
        await ctx.send(f"My ping is currently {round(self.bot.latency*1000, 2)}ms.")

    @commands.command()
    async def stats(self, ctx):
        """Sends a list of my statistics."""
        mem = psutil.virtual_memory()

        embed = discord.Embed(
            title="zane's Statistics",
            color=self.bot.color
        ).add_field(
            name="CPU Usage",
            value=f"{psutil.cpu_percent(interval=0.1)}%"
        ).add_field(
            name="RAM Usage",
            value=f"{humanize.naturalsize(mem.used)}/{humanize.naturalsize(mem.total)}"
        ).add_field(
            name="Guilds",
            value=f"{len(self.bot.guilds)}"
        ).add_field(
            name="Unique Users",
            value=f"{len(set(self.bot.get_all_members()))}"
        ).set_thumbnail(
            url=self.bot.user.avatar_url_as(format="png", size=64)
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def za(self, ctx):
        """Za Za"""
        if ctx.author.id in [217462890364403712, 246938839720001536]:
            await ctx.send(ctx.author.mention)


def setup(bot):
    bot.add_cog(Zane(bot))
