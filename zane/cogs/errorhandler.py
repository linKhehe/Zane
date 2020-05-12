import datetime

import discord
from discord.ext import commands
import humanize


def humanize_command_cooldown(cooldown):
    return humanize.naturaltime(datetime.datetime.now() + datetime.timedelta(seconds=cooldown.retry_after))


class UnknownError:
    pass


class CommandError:

    def __init__(self, exception, ctx):
        self.exception = exception
        self.ctx = ctx

        if isinstance(exception, commands.CommandOnCooldown):
            exception.formatted_cooldown = humanize_command_cooldown(exception)

        self.messages = {
            commands.MissingRequiredArgument: {"title": "Missing Argument",
                                               "description": "You are missing the required argument {0.param.name}. "
                                                              "Please enter that parameter and try again.",
                                               "reset": True},
            commands.BadArgument: {"title": "Bad Argument",
                                   "description": "You passed a bad argument. If you are having trouble, refer to the "
                                                  "help documentation for the command.",
                                   "reset": True},
            commands.BadUnionArgument: {"title": "Bad Or Missing Argument",
                                        "description": "You passed a bad argument or forgot an argument. If you are "
                                                       "having trouble, refer to the help documentation for the "
                                                       "command.",
                                        "reset": True},
            commands.TooManyArguments: {"title": "Too Many Arguments",
                                        "description": "You passed too many arguments. If you are having trouble, "
                                                       "refer to the help documentation for the command.",
                                        "reset": True},
            commands.UserInputError: {"title": "Input Error",
                                      "description": "Your input was invalid. If you are having trouble, refer to the "
                                                     "help documentation for the command.",
                                      "reset": True},
            commands.CommandOnCooldown: {"title": "Command On Cooldown",
                                         "description": "That command is currently on a cooldown, **you can try again "
                                                        "in {0.formatted_cooldown}**.",
                                         "reset": False},
            commands.MissingPermissions: {"title": "Missing Permissions",
                                          "description": "You are missing {0.missing_perms} which is/are required for "
                                                         "this command.",
                                          "reset": True},
            discord.Forbidden: {"title": "I'm Missing Permissions",
                                "description": "I am missing {0.missing_perms} which is/are required for this command.",
                                "reset": True},
            commands.CommandInvokeError: {"title": "Error",
                                          "description": "An error occurred, that is all I know",
                                          "reset": True}
        }

    @property
    def message(self):
        return self.messages[type(self.exception)]

    @property
    def embed(self):
        return discord.Embed(title=self.message["title"], color=discord.Color.red(),
                             description=self.message["description"].format(self.exception))

    async def send_to(self, channel: discord.abc.Messageable):
        await channel.send(embed=self.embed)

    async def reset_cooldown(self):
        try:
            if self.messages[type(self.exception)]["reset"]:
                self.ctx.command.reset_cooldown(self.ctx)
                return True
        except KeyError:
            return False


class ErrorHandler(commands.Cog, name="Error Handler", command_attrs=dict(hidden=True, checks=[commands.is_owner])):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        error = CommandError(exception, ctx)

        await error.reset_cooldown()
        try:
            await error.send_to(ctx)
        except discord.Forbidden:
            await error.send_to(ctx.author)

        if isinstance(exception, commands.CommandInvokeError):
            raise exception.original
        commands.NotOwner


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
