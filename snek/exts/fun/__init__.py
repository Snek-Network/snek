from snek.bot import Snek
from snek.exts.fun.randomization import Randomization


def setup(bot: Snek) -> None:
    """Load the `Randomization` cog."""
    bot.add_cog(Randomization(bot))
