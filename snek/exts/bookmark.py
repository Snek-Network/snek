import discord
from discord.ext.commands import Cog, Context, command

from snek.bot import Snek


class Bookmark(Cog):
    """Bookmark and save messages."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @command(aliases=('bm',))
    async def bookmark(self, ctx: Context, message: discord.Message, *, title: str = '') -> None:
        """Bookmark a message to your DMs."""
        embed = discord.Embed(
            title=title or "Bookmark",
            color=discord.Color.blurple(),
            description=message.content
        )
        embed.set_author(
            name=message.author,
            icon_url=message.author.avatar_url
        )
        embed.add_field(
            name='Want to visit the original message?',
            value=f'[Jump to original message]({message.jump_url})'
        )

        embed.set_thumbnail(
            url='https://cdn.iconscout.com/icon/free/png-32/bookmark-1754138-1493251.png'
        )

        for a in message.attachments:
            if a.height is None or a.width is None:
                continue

            embed.set_image(url=a.url)
            break

        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send('❌ Please open your DMs!')
        else:
            await ctx.message.add_reaction('✅')


def setup(bot: Snek) -> None:
    """Load the `Bookmark` cog."""
    bot.add_cog(Bookmark(bot))
