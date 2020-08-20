import logging
import os

import discord
from discord.ext.commands import when_mentioned_or

from snek.bot import Snek
from snek.exts import EXTENSIONS

log = logging.getLogger(__name__)


snek = Snek(
    command_prefix=when_mentioned_or('!'),
    activity=discord.Activity(name='over everyone.', type=discord.ActivityType.watching),
    case_insensitive=True,
    max_messages=10_000,
    allowed_mentions=discord.AllowedMentions(everyone=False)
)

# Ignore bots
snek.check(lambda ctx: not ctx.author.bot)

# Load extensions
for extension in sorted(EXTENSIONS):
    snek.load_extension(extension)

log.info('Snek starting..')
snek.run(os.environ.get('SNEK_BOT_TOKEN'))
