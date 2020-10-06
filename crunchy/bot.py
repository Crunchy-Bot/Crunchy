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
        """
        We use __new__ to modify our class before we initialise it as discord.py
        changes everything when it's init subclass is ran.
        """
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
        """
        Anything which needs initialising at the start can be ran here, it will only ever be
        ran once regardless of shard connects.
        """
        await self.redis.setup()

    async def logout(self):
        """ We override the existing logout coroutine to let us safely shutdown everything first """
        await self.redis.shutdown()
        await super().logout()

    async def on_ready(self):
        """
        Used for when the bot is in debug mode running on a test bot, on_shard_ready wont trigger
        if this event is not removed so this is a dynamic event.
        """

        print("[ SHARD INFO ][ CONNECT ] Bot Connected to Discord")
        if self._starting:
            await self.on_ready_once()
            self._starting = False

    async def on_shard_ready(self, shard_id: int):
        """
        Used in production, all shards are logged to keep track of any issues.

            - When in PRODUCTION=False Mode the bot will remove this event.
        """
        print("[ SHARD INFO ][ CONNECT ] Shard {} has connected".format(shard_id))
        if self._starting:
            await self.on_ready_once()
            self._starting = False


if __name__ == '__main__':
    crunchy = Crunchy()
    crunchy.run(str(os.getenv("DEBUG_TOKEN") if not PRODUCTION else str(os.getenv("PRODUCTION_TOKEN"))))
