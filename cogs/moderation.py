import asyncio
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
        """
        Kick a member from the server.
        """
        await member.kick(reason=reason)

        e = discord.Embed(
            title=f"Kicked: {member.name}",
            description=f"{member.name} was kicked from the server."
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)

    @commands.command(
        name="ban"
    )
    @commands.has_permissions(
        ban_members=True
    )
    async def _ban_command(self, ctx, member: discord.Member, time: int = False, reason: str = None):
        """
        Ban a member from the server. You can use the time argument to specify then the member should be unbanned.
        """
        if time <= 0:
            raise commands.BadArgument("An invalid argument was passed. The time argument can't be negative or 0.")

        await member.ban(reason=reason)

        e = discord.Embed(
            title=f"Banned: {member.name}",
            description=f"{member.name} was banned from the server.",
            color=self.bot.color
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)

        if time:
            await asyncio.sleep(time)
            await member.unban(reason="Ban timer elapsed.")
            try:
                e = discord.Embed(
                    title=f"Unbanned: {member.name}",
                    description=f"You have been unbanned in {ctx.guild.name}.",
                    color=self.bot.color
                )
                e.set_thumbnail(
                    url=ctx.guild.icon_url
                )
                await member.send(embed=e)
            except discord.Forbidden:
                pass

def setup(bot):
    bot.add_cog(Moderation(bot))
