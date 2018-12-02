import os

import dbl
import asyncio


class DiscordBotsOrgAPI:

    def __init__(self, bot):
        self.bot = bot
        self.token = os.environ['DBL_TOKEN']
        self.dbl_py = dbl.Client(self.bot, self.token)
        self.bot.loop.create_task(self._update_stats())

    async def _update_stats(self):
        while True:
            try:
                await self.dbl_py.post_server_count(shard_count=len(self.bot.shards))
            except Exception:
                pass
            await asyncio.sleep(1800)


def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
