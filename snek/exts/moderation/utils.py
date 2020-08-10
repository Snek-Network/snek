from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
import logging
import typing as t

import discord
import humanize

from snek.utils import UserObject

log = logging.getLogger(__name__)


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


async def send_infraction(payload: InfractionPayload) -> bool:
    """
    Sends informaiton about an infraction to a user via DMs and returns
    a boolean showing whether or not the DM was successful.

    True -> Successful
    False -> Unsuccessful
    """
    infr_type = payload.type.name.capitalize()

    embed = discord.Embed(
        title=f'{infr_type} Infraction',
        timestamp=datetime.utcnow(),
        color=discord.Color.red()
    )

    embed.set_author(name=payload.guild.name, icon_url=str(payload.guild.icon_url))

    embed.add_field(name='Guild', value=payload.guild.name)
    embed.add_field(name='Infraction Type', value=infr_type)

    if (expires_at := payload.expires_at) is not None:
        if expires_at == 'permanent':
            duration = 'N/A'
        else:
            duration = humanize.precisedelta(expires_at, minimum_unit='seconds', format=r'%0.0f')

        embed.add_field(name='Expires At', value=duration)

    if (reason := payload.reason) is not None:
        embed.add_field(name='Reason', value=reason, inline=False)

    log.trace(f'Sending an infraction notification to user {payload.user.id} from guild {payload.guild.id}.')
    return await send_private_embed(payload.user, embed)


async def send_private_embed(user: UserObject, embed: discord.Embed) -> bool:
    """
    Sends an embed to a user via DMs and returns a boolean showing
    whether or not the DM was successful.

    True -> Successful
    False -> Unsuccessful
    """
    try:
        await user.send(embed=embed)
    except (discord.HTTPException, discord.Forbidden, discord.NotFound):
        log.debug(
            f'Failed to DM user {user.id} an embed. '
            'Most likely because they do not have DMs enabled or the user could not be found.'
        )
        return False

    return True
