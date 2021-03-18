from orjson import loads
from logging import getLogger

from .rabbit import RabbitSession, RabbitConfig, Message


logger = getLogger("event-handler")


class EventHandler:
    def __init__(
        self,
        config: RabbitConfig,
        on_message,
        on_message_update,
        on_reaction_add,
        on_reaction_remove,
        on_reaction_clear,
        on_reaction_clear_emoji,
    ):
        self._connector = RabbitSession(config, self._on_rabbit_message)
        self._events = dict(
            CHANNEL_CREATE=None,
            CHANNEL_UPDATE=None,
            CHANNEL_DELETE=None,
            CHANNEL_PINS_UPDATE=None,

            GUILD_CREATE=None,
            GUILD_UPDATE=None,
            GUILD_DELETE=None,
            GUILD_BAN_ADD=None,
            GUILD_BAN_REMOVE=None,
            GUILD_EMOJI_UPDATE=None,
            GUILD_INTEGRATIONS_UPDATE=None,
            GUILD_ROLE_CREATE=None,
            GUILD_ROLE_UPDATE=None,
            GUILD_ROLE_DELETE=None,

            INTERACTION_CREATE=None,

            MESSAGE_CREATE=on_message,
            MESSAGE_UPDATE=on_message_update,
            MESSAGE_REACTION_ADD=on_reaction_add,
            MESSAGE_REACTION_REMOVE=on_reaction_remove,
            MESSAGE_REACTION_REMOVE_ALL=on_reaction_clear,
            MESSAGE_REACTION_REMOVE_EMOJI=on_reaction_clear_emoji,
        )

    async def start(self):
        await self._connector.connect()
        self._connector.serve_events()

    async def wait(self):
        await self._connector.wait()

    async def shutdown(self):
        await self._connector.shutdown()

    async def _on_rabbit_message(self, msg: Message):
        async with msg.process():
            content = loads(msg.body)
            event: str = content['t']

            handler = self._events.get(event, -1)
            if handler is None or handler == -1:
                logger.warning(f"ignoring event {event!r}")

            await handler(content['d'])
