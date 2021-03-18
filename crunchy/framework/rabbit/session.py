import asyncio
import orjson
import aio_pika

from dataclasses import dataclass
from typing import Optional, Callable
from pprint import pprint


@dataclass(frozen=True, init=True)
class RabbitConfig:
    username: str
    password: str
    host: str = "127.0.0.1"
    port: int = 5672
    key: str = "/"

    @property
    def connection_url(self) -> str:
        return (
            f"amqp://"
            f"{self.username}:{self.password}"
            f"@{self.host}:{self.port}{self.key}"
        )


class RabbitSession:
    QUEUE_NAME = "gateway.recv"

    def __init__(
            self,
            config: RabbitConfig,
            on_event: Callable[[aio_pika.IncomingMessage], None],
    ):
        self.config = config
        self._stop_serving = False
        self._on_event = on_event

        self._connection: Optional[aio_pika.RobustConnection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._queue: Optional[aio_pika.Queue] = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(
            self.config.connection_url
        )

        self._channel = await self._connection.channel()

        self._queue = await self._channel.declare_queue(
            self.QUEUE_NAME,
            auto_delete=False,
            passive=False,
            durable=True,
        )

    async def shutdown(self):
        if self._channel is not None:
            await self._channel.close()

        if self._connection is not None:
            await self._connection.close()

        self._channel = None
        self._connection = None

    async def serve_events(self):
        if self._queue is None:
            raise TypeError(
                "queue connection is None, "
                "have you connected to RabbitMQ first?"
            )

        async with self._queue.iterator() as queue_iter:
            while not self._stop_serving:
                message = await queue_iter.__anext__()
                self._on_event(message)

        self._queue = None


def on_event_receive(msg: aio_pika.Message):
    pprint(orjson.loads(msg.body))


async def main():
    config = RabbitConfig(
        username="guest",
        password="guest",
    )

    sess = RabbitSession(
        config,
        on_event_receive,
    )

    await sess.connect()
    await sess.serve_events()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
