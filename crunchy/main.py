import asyncio
import os
from framework.bot import Bot, RabbitConfig


async def main():
    conf = RabbitConfig(
        username="guest",
        password="guest",
    )

    handler = Bot(os.getenv("TOKEN"), conf, "!")
    await handler.start()
    await handler.wait()

asyncio.run(main())