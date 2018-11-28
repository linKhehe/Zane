import discord
from discord.ext import commands


class Zane:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="vote",
    )
    async def _vote_command(self, ctx):
        await ctx.send(f"""Vote for me! It really helps <3.\n**https://discordbots.org/bot/{self.bot.user.id}/vote**""")

    @commands.command(
        name="invite",
        aliases=[
            "inviteme",
            "addme"
        ]
    )
    async def _invite_command(self, ctx):
        await ctx.send(f"""Add me to your server!\n**https://discordapp.com/api/oauth2/authorize\
?client_id={self.bot.user.id}&permissions=8&scope=bot**""")


def setup(bot):
    bot.add_cog(Zane(bot))
