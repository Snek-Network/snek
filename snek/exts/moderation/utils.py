from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
import typing as t

import discord

from snek.utils import UserObject


class Infraction(Enum):
    BAN = auto()
    KICK = auto()
    MUTE = auto()
    WATCH = auto()
    FORCE_NICK = auto()
    WARNING = auto()
    NOTE = auto()


InfractionPayloadDict = t.Dict[str, t.Union[str, None, datetime, discord.Guild, UserObject, Infraction]]


@dataclass
class InfractionPayload:
    type: Infraction
    reason: t.Optional[str]
    expires_at: t.Optional[datetime]
    user: UserObject
    actor: UserObject
    guild: discord.Guild

    def to_dict(self) -> InfractionPayloadDict:
        return {
            'type': self.type.name,
            'reason': self.reason,
            'expires_at': self.expires_at.isoformat(),
            'user': self.user.id,
            'actor': self.actor.id,
            'guild': self.guild.id
        }
