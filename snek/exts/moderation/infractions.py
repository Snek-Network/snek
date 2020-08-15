import logging
import typing as t

import discord
from discord.ext.commands import Cog, Context, command

from snek.bot import Snek
from snek.utils import FetchedMember, ProxyUser, UserObject

from snek.exts.moderation.utils import Infraction, InfractionPayload, send_infraction, send_pardon

log = logging.getLogger(__name__)


class Infractions(Cog):
    """
    Commands for moderators+ to ban, mute, kick, watch,
    force nick, warn, and note offending members.
    """

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    async def apply_infraction(
        self,
        ctx: Context,
        payload: InfractionPayload,
        *,
        action: t.Optional[t.Coroutine] = None
    ) -> None:
        """Applies an infraction to an offending member."""
        infr_type = payload.type.name.lower()
        log.trace(f'Applying {infr_type} to user {payload.user.id} in guild {payload.guild.id}.')

        log.trace('Posting infraction to Snek API..')
        resp = await ctx.bot.api_client.post('infractions', json=payload.to_dict())

        dm_emoji = ''
        if not payload.hidden:
            notified = await send_infraction(payload)
            dm_emoji = '📬 ' if notified else '📭 '

        if action is not None:
            try:
                log.trace('Attempting to await infraction action..')
                await action
            except Exception as err:
                log.error(
                    f'Failed to apply infraction #{resp["id"]} ({infr_type}) '
                    f'to user {payload.user.id} in guild {payload.guild.id}.',
                    exc_info=err
                )
                await ctx.bot.api_client.delete(f'infractions/{resp["id"]}')

                await ctx.send('❌ Failed to apply infraction.')
                return

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

    async def pardon_infraction(
        self,
        ctx: Context,
        infr_type: Infraction,
        user: UserObject,
        reason: t.Optional[str],
        *,
        action: t.Coroutine
    ) -> None:
        """Pardons an infraction from a user."""
        infr_type = infr_type.name.lower()
        log.trace(f'Pardoning {infr_type} for user {user.id} in guild {ctx.guild.id}.')

        log.trace(
            f'Getting active {infr_type}s for user {user.id} in guild {ctx.guild.id} from Snek API..'
        )
        infractions = await self.bot.api_client.get(
            'infractions',
            params={
                'active': 'true',
                'type': infr_type,
                'user__id': user.id,
                'guild__id': ctx.guild.id
            }
        )

        if not infractions:
            log.debug(f'No active {infr_type}s found for user {user.id} in guild {ctx.guild.id}.')
            await ctx.send(f'❌ There are no active infraction for {user.mention}.')
            return

        payload = await InfractionPayload.from_dict(ctx, infractions[0])

        try:
            log.trace('Attempting to await infraction pardon action..')
            await action
        except Exception as err:
            log.error(
                f'Failed to pardon infraction #{payload.id} ({infr_type}) '
                f'to user {user.id} in guild {ctx.guild.id}.',
                exc_info=err
            )

            await ctx.send('❌ Failed to pardon infraction.')
            return

        await self.bot.api_client.patch(
            f'infractions/{payload.id}',
            json={'active': False}
        )

        dm_emoji = ''
        if payload.type != Infraction.BAN:
            notified = await send_pardon(payload)
            dm_emoji = '📬 ' if notified else '📭 '

        await ctx.send(f'{dm_emoji}👌 Pardoned {infr_type} for {payload.user.mention}.')

        log.debug(
            f'Pardoned infraction #{payload.id} ({infr_type}) for '
            f'user {payload.user.id} in guild {payload.guild.id}.'
        )

    @command(name='ban')
    async def apply_ban(self, ctx: Context, user: FetchedMember, *, reason: t.Optional[str]) -> None:
        """Bans an offending member of a guild."""
        await self.apply_infraction(
            ctx,
            InfractionPayload(
                type=Infraction.BAN,
                reason=reason,
                expires_at=None,
                user=user,
                actor=ctx.author,
                guild=ctx.guild,
                active=True,
                hidden=False
            ),
            action=user.ban(reason=reason)
        )

    @command(name='mute')
    async def apply_mute(self, ctx: Context, user: discord.Member, *, reason: t.Optional[str]) -> None:
        """Mutes an offending member of a guild."""

    @command(name='kick')
    async def apply_kick(self, ctx: Context, user: discord.Member, *, reason: t.Optional[str]) -> None:
        """Kicks an offending member of a guild."""
        await self.apply_infraction(
            ctx,
            InfractionPayload(
                type=Infraction.KICK,
                reason=reason,
                expires_at=None,
                user=user,
                actor=ctx.author,
                guild=ctx.guild,
                active=False,
                hidden=False
            ),
            action=user.kick(reason=reason)
        )

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

    @command(name='unban')
    async def pardon_ban(self, ctx: Context, user: ProxyUser, *, reason: t.Optional[str]) -> None:
        """Pardons a ban."""

    @command(name='unmute')
    async def pardon_mute(self, ctx: Context, user: FetchedMember, *, reason: t.Optional[str]) -> None:
        """Pardons a mute."""

    @command(name='unnick')
    async def pardon_nick(self, ctx: Context, user: FetchedMember, *, reason: t.Optional[str]) -> None:
        """Pardons a forced nickname."""

    def cog_check(self, ctx: Context) -> bool:
        return discord.utils.get(ctx.author.roles, id=self.bot.configs[ctx.guild.id]['mod_role'])
