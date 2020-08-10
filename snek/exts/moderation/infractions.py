import logging
import typing as t

import discord
from discord.ext.commands import Cog, Context, command

from snek.bot import Snek
from snek.utils import FetchedMember, ProxyUser, UserObject

from snek.exts.moderation.utils import Infraction, InfractionPayload, send_infraction

log = logging.getLogger(__name__)


class Infractions(Cog):
    """
    Commands for moderators+ to ban, mute, kick, watch,
    force nick, warn, and note offending members.
    """

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    async def apply_infraction(self, ctx: Context, payload: InfractionPayload) -> None:
        """Applies an infraction to an offending member."""
        infr_type = payload.type.name.lower()
        log.trace(f'Applying {infr_type} to user {payload.user.id} in guild {payload.guild.id}.')

        resp = await ctx.bot.api_client.post('infractions', json=payload.to_dict())

        dm_emoji = ''
        if not payload.hidden:
            notified = await send_infraction(payload)
            dm_emoji = '📬 ' if notified else '📭 '

        msg = f'{dm_emoji}👌 Applied {infr_type} to {payload.user.mention}.'

        infractions = await self.bot.api_client.get(
            'infractions',
            params={'user__id': payload.user.id, 'hidden': 'false'}
        )

        if (infr_amt := len(infractions)) > 0:
            msg += f' ({infr_amt} total)'

        await ctx.send(msg)

        log.debug(
            f'Applied infraction #{resp["id"]} ({infr_type}) to '
            f'user {payload.user.id} in guild {payload.guild.id}.'
        )

    async def pardon_infraction(self, ctx: Context, infr_type: Infraction, user: UserObject):
        """Pardons an infraction from a user."""

    @command(name='ban')
    async def apply_ban(self, ctx: Context, user: FetchedMember, *, reason: t.Optional[str]) -> None:
        """Bans an offending member of a guild."""

    @command(name='mute')
    async def apply_mute(self, ctx: Context, user: discord.Member, *, reason: t.Optional[str]) -> None:
        """Mutes an offending member of a guild."""

    @command(name='kick')
    async def apply_kick(self, ctx: Context, user: discord.Member, *, reason: t.Optional[str]) -> None:
        """Kicks an offending member of a guild."""

    @command(name='forcenick', aliases=('nick',))
    async def apply_nick(self, ctx: Context, user: discord.Member, *, reason: t.Optional[str]) -> None:
        """Forces a nickname on an offending member of a guild."""

    @command(name='warn')
    async def apply_warn(self, ctx: Context, user: discord.Member, *, reason: t.Optional[str]) -> None:
        """Warns an offending member of a guild."""
        await self.apply_infraction(
            ctx,
            InfractionPayload(
                type=Infraction.WARNING,
                reason=reason,
                expires_at=None,
                user=user,
                actor=ctx.author,
                guild=ctx.guild,
                active=False,
                hidden=False
            )
        )

    @command(name='note')
    async def apply_note(self, ctx: Context, user: FetchedMember, *, reason: str) -> None:
        """Keeps a note on an offending member of a guild."""
        await self.apply_infraction(
            ctx,
            InfractionPayload(
                type=Infraction.NOTE,
                reason=reason,
                expires_at=None,
                user=user,
                actor=ctx.author,
                guild=ctx.guild,
                active=False,
                hidden=True
            )
        )

    @command(aliases=('unban',))
    async def pardon_ban(self, ctx: Context, user: ProxyUser, *, reason: t.Optional[str]) -> None:
        """Pardons a ban."""

    @command(aliases=('unmute',))
    async def pardon_mute(self, ctx: Context, user: FetchedMember, *, reason: t.Optional[str]) -> None:
        """Pardons a mute."""

    @command(aliases=('unnick',))
    async def pardon_nick(self, ctx: Context, user: FetchedMember, *, reason: t.Optional[str]) -> None:
        """Pardons a forced nickname."""
