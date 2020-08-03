import typing as t

import discord
from discord.ext.commands import Cog, Context, command

from snek.bot import Snek
from snek.utils import FetchedMember, ProxyUser, UserObject

from snek.exts.moderation.utils import Infraction, InfractionPayload


class Infractions(Cog):
    """
    Commands for moderators+ to ban, mute, kick, watch,
    force nick, warn, and note offending members.
    """

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    def apply_infraction(self, ctx: Context, payload: InfractionPayload) -> None:
        """Applies an infraction to an offending member."""

    def pardon_infraction(self, ctx: Context, infr_type: Infraction, user: UserObject):
        """Pardons an infraction from a user."""

    @command(name='ban')
    def apply_ban(self, ctx: Context, user: FetchedMember, reason: t.Optional[str]) -> None:
        """Bans an offending member of a guild."""

    @command(name='mute')
    def apply_mute(self, ctx: Context, user: discord.Member, reason: t.Optional[str]) -> None:
        """Mutes an offending member of a guild."""

    @command(name='kick')
    def apply_kick(self, ctx: Context, user: discord.Member, reason: t.Optional[str]) -> None:
        """Kicks an offending member of a guild."""

    @command(name='forcenick', aliases=('nick',))
    def apply_nick(self, ctx: Context, user: discord.Member, reason: t.Optional[str]) -> None:
        """Forces a nickanme on an offending member of a guild."""

    @command(name='warn')
    def apply_warn(self, ctx: Context, user: discord.Member, reason: t.Optional[str]) -> None:
        """Warns an offending member of a guild."""

    @command(name='note')
    def apply_note(self, ctx: Context, user: FetchedMember, reason: str) -> None:
        """Keeps a note on an offending member of a guild."""

    @command(aliases=('unban',))
    def pardon_ban(self, ctx: Context, user: ProxyUser, reason: t.Optional[str]) -> None:
        """Pardons a ban."""

    @command(aliases=('unmute',))
    def pardon_mute(self, ctx: Context, user: FetchedMember, reason: t.Optional[str]) -> None:
        """Pardons a mute."""

    @command(aliases=('unnick',))
    def pardon_nick(self, ctx: Context, user: FetchedMember, reason: t.Optional[str]) -> None:
        """Pardons a forced nickname."""
