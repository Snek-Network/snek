from snek.bot import Snek
from snek.exts.moderation.slowmode import Slowmode


def setup(bot: Snek) -> None:
    """Load the `moderation` cogs."""
    bot.add_cog(Slowmode(bot))
