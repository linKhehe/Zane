import discord
from discord.ext import commands


class Moderation:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="kick"
    )
    @commands.has_permissions(
        kick_members=True
    )
    async def _kick_command(self, ctx, member: discord.Member, reason: str = None):
        await member.kick(reason=reason)

        e = discord.Embed(
            title=f"Kicked: {member.name}",
            description=f"{member.name} was kicked from the server."
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Moderation(bot))
