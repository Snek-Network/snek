from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
import typing as t

from discord.ext.commands import Context

from snek.utils import UserObject


class Infraction(Enum):
    BAN = auto()
    KICK = auto()
    MUTE = auto()
    WATCH = auto()
    FORCE_NICK = auto()
    WARNING = auto()
    NOTE = auto()


InfractionPayloadDict = t.Dict[str, t.Union[str, None, datetime, UserObject, Infraction]]


@dataclass
class InfractionPayload:
    type: Infraction
    reason: t.Optional[str]
    expires_at: t.Optional[datetime]
    user: UserObject
    actor: UserObject

    def to_dict(self) -> InfractionPayloadDict:
        return {
            'type': self.type.name,
            'reason': self.reason,
            'expires_at': self.expires_at.isoformat(),
            'user': self.user.id,
            'actor': self.actor.id
        }


async def post_infraction(ctx: Context, payload: InfractionPayload) -> t.Optional[t.Dict[str, t.Any]]:
    """Posts an infraction to the Snek API."""
    return await ctx.bot.api_client.post('infractions', json=payload.to_dict())
