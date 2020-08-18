from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
import logging
import typing as t

import discord
from discord.ext.commands import Context
import humanize

from snek.utils import ProxyUser, UserObject

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
    user: UserObject
    actor: UserObject
    guild: discord.Guild
    reason: t.Optional[str] = None
    expires_at: t.Optional[datetime] = None
    active: bool = True,
    hidden: bool = False
    id: t.Optional[int] = None

    def to_dict(self) -> InfractionPayloadDict:
        payload = {
            'id': self.id,
            'type': self.type.name.lower(),
            'reason': self.reason,
            'user': self.user.id,
            'actor': self.actor.id,
            'guild': self.guild.id,
            'active': self.active,
            'hidden': self.hidden
        }

        if self.expires_at is not None:
            payload['expires_at'] = self.expires_at.isoformat()

        return payload

    @classmethod
    async def from_dict(cls, ctx: Context, payload: InfractionPayloadDict) -> InfractionPayload:

        async def get_user(user_id: int) -> UserObject:
            return ctx.guild.get_member(user_id) or await ProxyUser().convert(ctx, user_id)

        self = cls(
            id=payload.get('id'),
            type=Infraction[payload['type'].upper()],
            reason=payload['reason'],
            expires_at=datetime.fromisoformat(payload['expires_at']) if payload['expires_at'] else None,
            user=await get_user(payload['user']),
            actor=await get_user(payload['actor']),
            guild=ctx.bot.get_guild(payload['guild']),
            active=payload['active'],
            hidden=payload['hidden']
        )

        return self


def _construct_generic_infr_embed(payload: InfractionPayload, *, infraction: bool) -> discord.Embed:
    """Constructs a generic embed for infractions and pardons."""
    infr_type = payload.type.name.capitalize()

    embed = discord.Embed(
        title=f'{infr_type} {"Infraction" if infraction else "Pardon"}',
        timestamp=datetime.utcnow(),
        color=discord.Color.red() if infraction else discord.Color.green()
    )

    embed.set_author(name=payload.guild.name, icon_url=str(payload.guild.icon_url))

    embed.add_field(name='Guild', value=payload.guild.name)
    embed.add_field(name='Infraction Type', value=infr_type)

    return embed


async def send_infraction(payload: InfractionPayload) -> bool:
    """
    Sends information about an infraction to a user via DMs and returns
    a boolean showing whether or not the DM was successful.

    True -> Successful
    False -> Unsuccessful
    """
    embed = _construct_generic_infr_embed(payload, infraction=True)

    if (expires_at := payload.expires_at) is not None:
        if expires_at == 'permanent':
            duration = 'N/A'
        else:
            duration = humanize.precisedelta(expires_at, minimum_unit='seconds', format=r'%0.0f')

        embed.add_field(name='Expires At', value=duration)

    if (reason := payload.reason) is not None:
        embed.description = f'**Reason**\n{reason}'

    log.trace(f'Sending an infraction notification to user {payload.user.id} from guild {payload.guild.id}.')
    return await send_private_embed(payload.user, embed)


async def send_pardon(payload: InfractionPayload) -> bool:
    """
    Notifies about an infraction pardon to a user via DMs and returns
    a boolean showing whether or not the DM was successful.

    True -> Successful
    False -> Unsuccessful
    """
    embed = _construct_generic_infr_embed(payload, infraction=False)
    embed.description = f'Your {payload.type.lower()} has been pardoned.'

    log.trace(f'Sending an infraction pardon notification to user {payload.user.id} from guild {payload.guild.id}.')
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
