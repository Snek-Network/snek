from contextlib import suppress
import logging
import typing as t

import discord
from discord.ext.commands import BadArgument, Context, Converter, UserConverter

from snek.api import ResponseCodeError

log = logging.getLogger(__name__)

UserObject = t.Union[discord.Member, discord.User, discord.Object]


class ProxyUser(Converter):
    """
    Converts a user ID to a proxy user object.

    This first tries to query the Snek API for the user, but
    if that fails, it will just fill in the information it can.
    """

    async def convert(self, ctx: Context, user_id: int) -> discord.Object:
        """Creates a proxy user object from the given ID."""
        log.trace(f'Attempting to create proxy user for {user_id}')

        user = discord.Object(user_id)
        user.mention = f'<@{user.id}>'
        user.bot = False

        try:
            user_info = await ctx.bot.api_client.get(f'users/{user_id}')
        except ResponseCodeError as err:
            if err.status != 404:
                raise

            user.display_name = user.mention
            user.avatar_url = None

        else:
            user.display_name = user_info['name']
            user.discriminator = user_info['discriminator']
            user.avatar_url = user_info['avatar_url']

        return user


class FetchedUser(UserConverter):
    """
    Converts to a `discord.User` object, or a `discord.Object` if it fails.

    Attempts to fetch the user via a Discord API call when the user is not found
    in the cache. If this fails,
    """

    async def convert(self, ctx: Context, arg: str) -> t.Union[discord.User, discord.Object]:
        """Converts `arg` into a `discord.User` or `discord.Object`."""
        with suppress(BadArgument):
            return await super().convert(ctx, arg)

        try:
            user_id = int(arg)

            log.trace(f'Fetching user {user_id}')
            return await ctx.bot.fetch_user(user_id)

        except ValueError:
            log.debug(f'Failed to fetch user {user_id}: could not convert to int.')
            raise BadArgument('The provided argument could not be converted to an integer.')

        except discord.HTTPException as err:
            # If the error is not "Unknown user"
            if err.code != 10013:
                log.debug(f'Failed to fetch user {user_id}; returning proxy user instead. Status: {err.status}')

                proxy_converter = ProxyUser()
                return await proxy_converter.convert(ctx, user_id)

        log.debug(f'Failed to fetch user {user_id}; user does not exist.')
        raise BadArgument('User does not exist.')


FetchedMember = t.Union[discord.Member, FetchedUser]
