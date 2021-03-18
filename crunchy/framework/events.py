from orjson import loads

from .rabbit import RabbitSession, RabbitConfig, Message
from .http import HTTPClient


class EventHandler:
    def __init__(self, config: RabbitConfig):
        self._connector = RabbitSession(config, self._on_rabbit_message)
        self.client = HTTPClient()
        self.client.send_message()

    def _on_rabbit_message(self, msg: Message):
        ...