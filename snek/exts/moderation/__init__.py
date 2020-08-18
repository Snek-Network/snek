from snek.bot import Snek
from snek.exts.moderation.infractions import Infractions


def setup(bot: Snek) -> None:
    """Load the `moderation` cogs."""
    bot.add_cog(Infractions(bot))
