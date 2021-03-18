import asyncio
import re

from .events import RabbitConfig, EventHandler
from .dpy_compat.http import HTTPClient
from .models import Author, Message, Context


class Bot:
    def __init__(
        self,
        token: str,
        config: RabbitConfig,
        command_prefix: str,
    ):
        self.loop = asyncio.get_event_loop()
        self.default_prefix = re.compile(
            f"^{command_prefix}",
            flags=re.IGNORECASE,
        )

        self._token = token
        self._client = HTTPClient()
        self._events = EventHandler(
            config,
            self.on_message,
            self.on_message_update,
            self.on_reaction_add,
            self.on_reaction_remove,
            self.on_reaction_clear,
            self.on_reaction_clear_emoji,
        )

    def run(self):
        self.loop.run_until_complete(self.start())

    async def start(self):
        await self._client.static_login(self._token, bot=True)
        await self._events.start()
        await self._events.wait()

    async def get_prefix(self):
        return self.default_prefix

    async def on_message(self, data):
        author = data['author']
        if author.get("bot", False):
            return

        author = Author(
            id=author['id'],
            avatar=author['avatar'],
            discriminator=author['discriminator'],
            username=author['username'],
        )

        message = Message(
            id=data['id'],
            guild_id=data['guild_id'],
            channel_id=data['channel_id'],
            mention_everyone=data['mention_everyone'],
            mention_roles=data['mention_roles'],
            mentions=data['mentions'],
            nonce=data['nonce'],
            author=author
        )

        ctx = Context(self, message)

        if message.author.id == "290923752475066368":
            await ctx.send("hello world :tada:")

    async def on_message_update(self, data):
        print("update")

    async def on_reaction_add(self, data):
        print("reaction add")

    async def on_reaction_remove(self, data):
        print("reation remove")

    async def on_reaction_clear(self, data):
        print("reaction clear")

    async def on_reaction_clear_emoji(self, data):
        print("reaction emoji clear")

    @property
    def http(self):
        return self._client
