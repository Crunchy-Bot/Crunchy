import os
import discord
import typing as t

import aioredis

from discord.ext import commands


if __name__ == '__main__':
    from redis import RedisManager
else:
    from .redis import RedisManager


PRODUCTION = False
CACHE = [
    'votes',
    'guilds',
    'members',
]


class Crunchy(commands.Bot):
    def __new__(cls, *args, **kwargs):
        if PRODUCTION:
            delattr(cls, 'on_ready')
        else:
            delattr(cls, 'on_shard_ready')

        instance = super(Crunchy, cls).__new__(cls, *args, **kwargs)
        return instance

    def __init__(self, **options):
        super().__init__("", **options)

        self._starting = True

        self.redis = RedisManager(CACHE)

    async def on_ready_once(self):
        await self.redis.setup()

    async def logout(self):
        await self.redis.shutdown()
        await super().logout()

    async def on_ready(self):
        print("[ SHARD INFO ][ CONNECT ] Bot Connected to Discord")
        if self._starting:
            await self.on_ready_once()
            self._starting = False

    async def on_shard_ready(self, shard_id: int):
        print("[ SHARD INFO ][ CONNECT ] Shard {} has connected".format(shard_id))
        if self._starting:
            await self.on_ready_once()
            self._starting = False


if __name__ == '__main__':
    crunchy = Crunchy()
    crunchy.run(str(os.getenv("DEBUG_TOKEN") if not PRODUCTION else str(os.getenv("PRODUCTION_TOKEN"))))
