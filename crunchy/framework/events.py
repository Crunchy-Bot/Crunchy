from orjson import loads

from .rabbit import RabbitSession, RabbitConfig, Message
from .dpy_compat.http import HTTPClient


class EventHandler:
    def __init__(self, config: RabbitConfig):
        self._connector = RabbitSession(config, self._on_rabbit_message)


    def _on_rabbit_message(self, msg: Message):
        ...