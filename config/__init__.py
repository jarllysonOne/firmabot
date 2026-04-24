import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    token: str = field(default_factory=lambda: os.getenv("DISCORD_TOKEN", ""))
    prefix: str = field(default_factory=lambda: os.getenv("BOT_PREFIX", "!"))
    channel_id: int = field(default_factory=lambda: int(os.getenv("CHANNEL_ID", 0)))
    everyone_role: Optional[int] = field(default_factory=lambda: int(os.getenv("EVERYONE_ROLE_ID", 0)) if os.getenv("EVERYONE_ROLE_ID") else None)
    owner_ids: list = field(default_factory=lambda: [int(uid) for uid in os.getenv("OWNER_IDS", "").split(",") if uid])
    log_channel_id: Optional[int] = field(default_factory=lambda: int(os.getenv("LOG_CHANNEL_ID", 0)) if os.getenv("LOG_CHANNEL_ID") else None)

    @property
    def intents(self) -> "discord.Intents":
        import discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        return intents


config = BotConfig()