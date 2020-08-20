import contextlib
import json
import typing as t
from pathlib import Path
from random import choice, randint, random

from discord import Embed, Message
from discord.ext.commands import BadArgument, MessageConverter, Cog, Context, command

from snek.bot import Snek


UWU = {
    'fi': 'fwi',
    'l': 'w',
    'r': 'w',
    'some': 'sum',
    'th': 'd',
    'thing': 'fing',
    'tho': 'fo',
    "you're": "yuw'we",
    'your': 'yur',
    'you': 'yuw',
}


with Path('snek/resources/magic8ball.json').open('r', encoding='utf8') as f:
    MAGICBALL = json.load(f)


class Randomization(Cog):
    """Randomizing the contents of messages."""

    def __init__(self, bot: Snek) -> None:
        self.bot = bot

    @command(name='uwu')
    async def uwu_case(self, ctx: Context, *, msg: str) -> None:
        """Uwuifies and adds stutter to strings in a message/embed."""
        def func(string: str, stutter_rate: float = 0.1) -> str:
            def _stutter(word: str) -> str:
                while random() < stutter_rate:
                    word = word[0] + '-' + word

                return word

            # UWU the string
            for before, after in UWU.items():
                string = string.replace(before, after)

            # Add stutter
            return ' '.join(map(_stutter, string.split(' ')))

        msg, embed = await self._get_text_and_embed(ctx, msg)

        # Convert embed if it exists
        if embed is not None:
            embed = self._convert_embed(func, embed)

        converted_text = func(msg)

        # Don't put >>> if only embed present
        if converted_text:
            converted_text = f'>>> {converted_text.lstrip("> ")}'

        await ctx.send(content=converted_text, embed=embed)

    @command(name='randomcase', aliases=('sarcasm',))
    async def random_case(self, ctx: Context, *, msg: str) -> None:
        """Randomizes the casing of each character in a message/embed."""
        def func(string: str) -> str:
            return ''.join(c.upper() if randint(0, 1) else c for c in string.lower())

        msg, embed = await self._get_text_and_embed(ctx, msg)

        # Convert embed if it exists
        if embed is not None:
            embed = self._convert_embed(func, embed)

        converted_text = func(msg)

        # Don't put >>> if only embed present
        if converted_text:
            converted_text = f'>>> {converted_text.lstrip("> ")}'

        await ctx.send(content=converted_text, embed=embed)

    @command(name='diceroll', aliases=('roll', 'dice'))
    async def roll_dice(self, ctx: Context, amount: int = 1) -> None:
        """Rolls a die an amount of times."""
        if amount < 1 or amount > 10:
            return await ctx.send('❌ Input must be between 1 and 10.')

        dice = [randint(1, 6) for _ in range(amount)]
        avg = round(sum(dice) / amount, 2)

        dice_string = ', '.join(f'`{x}`' for x in dice)

        await ctx.send((
            f'Rolled a die `{amount}` time{"s" if amount != 1 else ""}. '
            f'Output: {dice_string}. '
            f'Average: `{avg if amount != 1 else "Obvious"}`.'
        ))

    @command(name='coinflip', aliases=('coin', 'flip', 'cf'))
    async def flip_coin(self, ctx: Context) -> None:
        """Flips a two-sided coin for the user."""
        await ctx.send(f'Tossed a coin to your Witcher. Landed `{choice(["heads", "tails"])}` facing up.')

    @command(name='8ball', aliases=('magic8ball',))
    async def magic_8_ball(self, ctx: Context) -> None:
        """Answers come to the user from the magic 8 ball."""
        key = choice(list(MAGICBALL.keys()))
        await ctx.send(f'`{key}`: {choice(MAGICBALL[key])}')

    @classmethod
    async def _get_text_and_embed(cls, ctx: Context, text: str) -> t.Tuple[str, t.Optional[Embed]]:
        """Gets the text and embed from a possible link to a discord Message object."""
        embed = None
        message = await cls._get_discord_message(ctx, text)

        if isinstance(message, Message):
            text = message.content

            # Take first embed because we can't send multiple embeds
            if message.embeds:
                embed = message.embeds[0]

        return text, embed

    @staticmethod
    async def _get_discord_message(ctx: Context, text: str) -> t.Union[Message, str]:
        """Converts a message ID, link, or message to a message object or a string."""
        with contextlib.suppress(BadArgument):
            text = await MessageConverter().convert(ctx, text)

        return text

    @staticmethod
    def _convert_embed(func: t.Callable, embed: Embed) -> Embed:
        """Converts the title, description, footer, and field text with the given function"""
        embed_dict = embed.to_dict()

        embed_dict['title'] = func(embed_dict.get('title', ''))
        embed_dict['description'] = func(embed_dict.get('description', ''))

        if 'footer' in embed_dict:
            embed_dict['footer']['text'] = func(embed_dict['footer'].get('text', ''))

        if 'fields' in embed_dict:
            for field in embed_dict['fields']:
                field['name'] = func(field.get('name', ''))
                field['value'] = func(field.get('value', ''))

        if 'author' in embed_dict:
            embed_dict['author']['name'] = func(embed_dict['author'].get('name', ))

        return Embed.from_dict(embed_dict)


def setup(bot: Snek) -> None:
    """Load the `Randomization` cog."""
    bot.add_cog(Randomization(bot))
