from discord import Embed
from dataclasses import dataclass


DISCORD_CDN = "https://cdn.discordapp.com/"


@dataclass(frozen=True)
class Author:
    id: str
    avatar: str
    discriminator: str
    username: str

    @property
    def avatar_url(self):
        if self.avatar[0] == "a":
            return f"{DISCORD_CDN}/avatars/{self.id}/{self.avatar}.gif"
        return f"{DISCORD_CDN}/avatars/{self.id}/{self.avatar}.webp"


@dataclass(frozen=True)
class Message:
    id: str
    guild_id: str
    channel_id: str
    mention_everyone: bool
    mention_roles: list
    mentions: list
    nonce: str
    author: Author


class Context:
    def __init__(
        self,
        bot,
        message: Message
    ):
        self.bot = bot
        self.message = message

    async def send(self, content: str = None, *, embed: Embed = None):
        if embed is not None:
            embed = embed.to_dict()

        await self.bot.http.send_message(
            channel_id=self.message.channel_id,
            content=content,
            embed=embed,
        )
