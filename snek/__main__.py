import logging
import os

import discord
from discord.ext.commands import when_mentioned_or

from snek.bot import Snek

log = logging.getLogger(__name__)


snek = Snek(
    command_prefix=when_mentioned_or('!'),
    activity=discord.Game(name='Commands: !help'),
    case_insensitive=True,
    max_messages=10_000
)

# Load extensions
snek.load_extension('snek.cogs.ping')
snek.load_extension('snek.cogs.syncer')

log.info('Snek starting..')
snek.run(os.environ.get('BOT_TOKEN'))
