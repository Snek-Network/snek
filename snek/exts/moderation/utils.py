from datetime import datetime
import typing as t

from discord.ext.commands import Context

from snek.utils import UserObject


async def post_infraction(
    ctx: Context,
    user: UserObject,
    infr_type: str,
    reason: str,
    expires_at: datetime = None,
    hidden: bool = False,
    active: bool = True
) -> t.Optional[t.Dict[str, t.Any]]:
    """Posts an infraction to the Snek API."""
    payload = {
        'user': user.id,
        'actor': ctx.author.id,
        'reason': reason,
        'hidden': hidden,
        'active': active
    }

    if expires_at is not None:
        payload['expires_at'] = expires_at.isoformat()

    return await ctx.bot.api_client.post('infractions', json=payload)
