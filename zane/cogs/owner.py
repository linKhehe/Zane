import traceback

from discord.ext import commands


class Owner(commands.Cog, command_attrs=dict(hidden=True)):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(aliases=["rl"])
    async def reload(self, ctx, cog: str):
        try:
            self.bot.reload_extension(f"zane.cogs.{cog}")
            await ctx.send(f"Reloaded `zane.cogs.{cog}`")
        except:
            trace = traceback.format_exc()
            await ctx.send("```py\n" + trace + "```")

    @commands.command(aliases=["l"])
    async def load(self, ctx, cog: str):
        try:
            self.bot.load_extension(f"zane.cogs.{cog}")
            await ctx.send(f"Loaded `zane.cogs.{cog}`")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send("Extension already loaded")
        except:
            trace = traceback.format_exc()
            await ctx.send("```py\n" + trace + "```")

    @commands.command(aliases=["ul"])
    async def unload(self, ctx, cog: str):
        try:
            self.bot.unload_extension(f"zane.cogs.{cog}")
            await ctx.send(f"Unloaded `zane.cogs.{cog}`")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"Extension not loaded")

    @commands.command()
    async def nick(self, ctx, *, nick: str = None):
        await ctx.me.edit(nick=nick)
        await ctx.send("Nick updated.")

    @commands.command(aliases=["stop", "logout", "exit"])
    async def quit(self, ctx):
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))