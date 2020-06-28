from .cog import Images


def setup(bot):
    bot.add_cog(Images(bot))