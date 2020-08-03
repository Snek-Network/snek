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
    active: bool = True,
    hidden: bool = False

    def to_dict(self) -> InfractionPayloadDict:
        payload = {
            'type': self.type.name.lower(),
            'reason': self.reason,
            'user': self.user.id,
            'actor': self.actor.id,
            'guild': self.guild.id,
            'active': int(self.active),
            'hidden': int(self.hidden)
        }

        if self.expires_at is not None:
            payload['expires_at'] = self.expires_at.isoformat()

        return payload
