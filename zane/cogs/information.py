import discord
from discord.ext import commands
import humanize


class Information(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def create_info_block(info_mappings: dict) -> str:
        newline = "\n"
        return f"```{newline.join(f'{k}: {v}' for k, v in info_mappings.items())}```"

    @staticmethod
    def get_member_created_position(member: discord.Member) -> int:
        return sorted(member.guild.members, key=lambda m: m.created_at).index(member) + 1

    @staticmethod
    def get_member_join_position(member: discord.Member) -> int:
        return sorted(member.guild.members, key=lambda m: m.joined_at).index(member) + 1

    @commands.command(aliases=["ui", "memberinfo", "mi"])
    async def userinfo(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author

        embed = discord.Embed(
            title=str(member),
            color=self.bot.color
        ).add_field(
            name="Basic Info",
            value=self.create_info_block({
                "Username": member.name,
                "Nickname": member.nick or "None",
                "ID": member.id,
                "Discriminator": f"#{member.discriminator}",
                "Bot": str(member.bot).capitalize()
            }),
            inline=False
        ).add_field(
            name="Timing",
            value=self.create_info_block({
                "Joined Guild": humanize.naturaldate(member.joined_at),
                "Joined Discord": humanize.naturaldate(member.created_at),
                "Join Position": self.get_member_join_position(member)
            }),
            inline=False
        ).add_field(
            name="Permissions",
            value=self.create_info_block({
                "Top Role": member.top_role.name,
                "Administrator": str(member.guild_permissions.administrator).capitalize(),
                "Can Kick": str(member.guild_permissions.kick_members).capitalize(),
                "Can Ban": str(member.guild_permissions.ban_members).capitalize()
            }),
            inline=False
        ).set_thumbnail(
            url=str(member.avatar_url_as(format="png", size=64))
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def position(self, ctx, *, member: discord.Member = None):
        member = member or ctx.author

        await ctx.send(
            f"```Joined Guild Position: {self.get_member_join_position(member)}\n"
            f"Joined Discord Position: {self.get_member_created_position(member)}```"
        )


def setup(bot):
    bot.add_cog(Information(bot))
