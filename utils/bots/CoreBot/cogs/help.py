# Copyright (c) 2015-2021 Rapptz
# Copyright (c) 2022-present School Simplified
from __future__ import annotations

import inspect
import itertools
from typing import Any, Coroutine, Dict, List, Optional, Set, TYPE_CHECKING, Union

import discord
from discord import app_commands
from discord.app_commands import command, describe
from discord.ext import commands, menus

from core.common import Others
from core.paginate import RoboPages

if TYPE_CHECKING:
    from main import Timmy

TotalMappingDict = Dict[
    commands.Cog,
    Union[
        Set[Any],
        List[
            Union[
                commands.Command,
                app_commands.Command,
                app_commands.Group,
                app_commands.ContextMenu,
                Any,
            ]
        ],
    ],
]

CommandsListType = Union[
    Set,
    List[
        Union[
            commands.Command,
            commands.Group,
            app_commands.Group,
            app_commands.Command,
            app_commands.ContextMenu,
        ]
    ],
]


class FieldPageSource(menus.ListPageSource):
    """A page source that requires (field_name, field_value) tuple items."""

    def __init__(self, entries, *, per_page=12):
        super().__init__(entries, per_page=per_page)
        self.embed = discord.Embed(colour=discord.Colour.blurple())

    async def format_page(self, menu, entries):
        self.embed.clear_fields()
        self.embed.description = None

        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            text = (
                f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            )
            self.embed.set_footer(text=text)

        return self.embed


class GroupHelpPageSource(menus.ListPageSource):
    def __init__(
        self,
        group: Union[commands.Group, commands.Cog, app_commands.Group],
        commands_: CommandsListType,
        *,
        prefix: str,
    ):
        super().__init__(entries=commands_, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f"{self.group.qualified_name} Commands"
        self.description = self.group.description

    async def format_page(
        self,
        menu,
        commands_: CommandsListType,
    ) -> discord.Embed:

        embed = discord.Embed(
            title=self.title,
            description=self.description,
            colour=discord.Colour.fuchsia(),
        )
        for command_ in commands_:
            if isinstance(command_, commands.Command):
                signature = f"{command_.qualified_name} {command_.signature}"
                embed.add_field(
                    name=signature,
                    value=command_.short_doc or "No help given...",
                    inline=False,
                )
            elif isinstance(command_, app_commands.Command):
                params = self.slash_param_signature(command_)
                signature = (
                    f"{command_.root_parent} {command_.name} {params}"
                    if command_.root_parent
                    else f"{command_.name} {params}"
                )
                embed.add_field(
                    name=signature[:256],
                    value=command_.description[:1024] or "No help given...",
                    inline=False,
                )
            elif isinstance(command_, app_commands.Group):
                description = (
                    f"Use /help `{command_.name}` for subcommands help\n"
                    + command_.description
                    if not command_.description == "…"
                    else f"Use /help `{command_.name}` for subcommands help\n"
                )
                embed.add_field(
                    name=f"{command_.name} [subcommands]",
                    value=description[:1024],
                    inline=False,
                )
            # elif isinstance(command_, app_commands.ContextMenu)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(
                name=f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)"
            )

        embed.set_footer(text=f'Use "/help command" for more info on a command.')
        return embed

    @staticmethod
    def slash_param_signature(
        _command: Union[app_commands.Command, app_commands.Group]
    ) -> str:

        raw_sig = _command.to_dict()
        params: List[Dict[str, Union[int, List, str]]] = raw_sig["options"]

        if isinstance(_command, app_commands.Command):
            param_list: List[str] = []
            for param in params:
                name = param["name"]
                if not param["required"]:
                    param_list.append(f"[{name}]")
                else:
                    param_list.append(f"<{name}>")

            return " ".join(param_list)

        elif isinstance(_command, app_commands.Group):
            param_list = []
            for param in params:
                param_list.append(f"<{param['name']}>")
            return " ".join(param_list)


class HelpSelectMenu(discord.ui.Select["HelpMenu"]):
    def __init__(
        self,
        _commands: TotalMappingDict,
        bot: Timmy,
    ):
        super().__init__(
            placeholder="Select a category...",
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands = _commands
        self.bot = bot
        self.__fill_options()

    def __fill_options(self) -> None:
        self.add_option(
            label="Index",
            emoji="\N{WAVING HAND SIGN}",
            value="__index",
            description="The help page showing how to use the bot.",
        )
        for cog, __commands in self.commands.items():
            if not __commands:
                continue
            description = cog.description.split("\n", 1)[0] or None
            emoji = getattr(cog, "display_emoji", None)
            self.add_option(
                label=cog.qualified_name,
                value=cog.qualified_name,
                description=description,
                emoji=emoji,
            )

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        if value == "__index":
            await self.view.rebind(FrontPageSource(), interaction)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message(
                    "Somehow this category does not exist?", ephemeral=True
                )
                return

            __commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message(
                    "This category has no commands for you", ephemeral=True
                )
                return

            source = GroupHelpPageSource(cog, __commands, prefix="/")
            await self.view.rebind(source, interaction)


class HelpMenu(RoboPages):
    def __init__(
        self,
        source: menus.PageSource,
        interaction: discord.Interaction,
        bot: Timmy,
    ):
        super().__init__(source, interaction=interaction, compact=True, bot=bot)

    def add_categories(
        self, _commands: Dict[commands.Cog, List[commands.Command]]
    ) -> None:
        self.clear_items()
        self.add_item(HelpSelectMenu(_commands, self.bot))
        self.fill_items()

    async def rebind(
        self, source: menus.PageSource, interaction: discord.Interaction
    ) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)


class FrontPageSource(menus.PageSource):
    def is_paginating(self) -> bool:
        # This forces the buttons to appear even in the front page
        return True

    def get_max_pages(self) -> Optional[int]:
        # There's only one actual page in the front page
        # However we need at least 2 to show all the buttons
        return 2

    async def get_page(self, page_number: int) -> Any:
        # The front page is a dummy
        self.index = page_number
        return self

    def format_page(self, menu: HelpMenu, page):
        embed = discord.Embed(title="Bot Help", colour=discord.Colour.blurple())
        embed.description = inspect.cleandoc(
            f"""
            Hello! Welcome to the help page.
            Use "/help command" for more info on a command.
            Use "/help category" for more info on a category.
            Use the dropdown menu below to select a category.
        """
        )
        embed.set_footer(text=f"Contact IT Dept. for any questions or concerns!")
        embed.set_thumbnail(url=Others.timmy_book_png)

        if self.index == 0:
            embed.add_field(
                name="Documentation Page",
                value="https://timmy.schoolsimplified.org",
                inline=False,
            )
        elif self.index == 1:
            entries = (
                ("<argument>", "This means the argument is __**required**__."),
                ("[argument]", "This means the argument is __**optional**__."),
                ("[A|B]", "This means that it can be __**either A or B**__."),
                (
                    "[argument...]",
                    "This means you can have multiple arguments.\n"
                    "Now that you know the basics, it should be noted that...\n"
                    "__**You do not type in the brackets!**__",
                ),
            )

            embed.add_field(
                name="How do I use this bot?",
                value="Reading the bot signature is pretty simple.",
            )

            for name, value in entries:
                embed.add_field(name=name, value=value, inline=False)

        return embed


class Help(commands.Cog):
    """
    Help command
    """

    def __init__(self, bot: Timmy):
        self.bot = bot

    async def _filter_commands(
        self,
        _commands: CommandsListType,
        interaction: discord.Interaction,
        *,
        sort=False,
        key=None,
    ) -> List[Union[app_commands.Command, commands.Command, Any]]:
        """|coro|
        Returns a filtered list of commands and optionally sorts them.
        This takes into account the :attr:`verify_checks` and :attr:`show_hidden`
        attributes.
        Parameters
        ------------
        _commands: Iterable[:class:`Command`]
            An iterable of commands that are getting filtered.
        sort: :class:`bool`
            Whether to sort the result.
        key: Optional[Callable[:class:`Command`, Any]]
            An optional key function to pass to :func:`py:sorted` that
            takes a :class:`Command` as its sole parameter. If ``sort`` is
            passed as ``True`` then this will default as the command name.
        Returns
        ---------
        List[:class:`Command`]
            A list of commands that passed the filter.
        """

        if sort and key is None:
            key = (
                lambda c: c.qualified_name
                if isinstance(c, commands.Command)
                else c.name
            )
        #
        iterator = _commands
        return sorted(iterator, key=key) if sort else list(iterator)

    @staticmethod
    def get_command_signature(_command: Union[app_commands.Command, commands.Command]):
        if isinstance(_command, commands.Command):
            parent = _command.full_parent_name
            if len(_command.aliases) > 0:
                aliases = " | ".join(_command.aliases)
                fmt = f"[{_command.name}|{aliases}]"
                if parent:
                    fmt = f"{parent} {fmt}"
                alias = fmt
            else:
                alias = _command.name if not parent else f"{parent} {_command.name}"
            return f"{alias} {_command.signature}"
        elif isinstance(_command, app_commands.Command):
            return f"{_command.parent.name} {_command.name}"

    async def _send_bot_help(self, interaction: discord.Interaction) -> None:
        def key(_command: Union[app_commands.Command, commands.Command]) -> str:
            if isinstance(_command, app_commands.Command):
                _cog: commands.Cog = (
                    _command.binding
                    if isinstance(_command.binding, commands.Cog)
                    else None
                )
            else:
                _cog: commands.Cog = _command.cog
            return _cog.qualified_name if _cog else "\U0010ffff"

        _tuple_of_iter = (
            self.bot.tree.get_commands(guild=discord.Object(interaction.guild.id)),
            self.bot.tree.get_commands(),
            self.bot.commands,
        )

        # sort guild and global slash commands, regular commands
        entries: Union[
            Set[Any], List[Union[commands.Command, app_commands.Command]]
        ] = await self._filter_commands(
            _commands=set(itertools.chain.from_iterable(_tuple_of_iter)),
            interaction=interaction,
            sort=True,
            key=key,
        )

        all_commands: TotalMappingDict = {}
        for cog_name, children in itertools.groupby(entries, key=key):
            if cog_name == "\U0010ffff":
                continue

            cog = self.bot.get_cog(cog_name)
            all_commands[cog] = sorted(
                children,
                key=lambda c: c.qualified_name
                if isinstance(c, commands.Command)
                else c.name,
            )

        menu = HelpMenu(FrontPageSource(), interaction=interaction, bot=self.bot)
        menu.add_categories(all_commands)
        await menu.start()

    async def _send_cog_help(self, interaction: discord.Interaction, cog: commands.Cog):
        __commands_iter = (cog.get_commands(), cog.__cog_app_commands__)
        __commands = set(itertools.chain.from_iterable(__commands_iter))
        entries = await self._filter_commands(__commands, interaction=interaction, sort=True)
        menu = HelpMenu(
            GroupHelpPageSource(cog, entries, prefix="/"),
            interaction=interaction,
            bot=self.bot,
        )
        await menu.start()

    def reg_common_command_formatting(
        self, embed_like: discord.Embed, _command: commands.Command
    ):
        embed_like.title = self.get_command_signature(_command)
        if _command.description:
            embed_like.description = f"{_command.description}\n\n{_command.help}"
        else:
            embed_like.description = _command.help or "No help found..."

    async def _send_command_help(
        self,
        interaction: discord.Interaction,
        _command: Union[commands.Command, app_commands.Command, Any],
    ):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.fuchsia())

        if isinstance(_command, commands.Command):
            self.reg_common_command_formatting(embed, _command)

        elif isinstance(_command, app_commands.Command):
            self._common_command_formatting(embed, _command)

        await interaction.response.send_message(embed=embed)

    async def _send_group_help(
        self,
        interaction: discord.Interaction,
        group: Union[List[Any], Set[Any], app_commands.Group, commands.Group],
    ):
        if isinstance(group, app_commands.Group):
            subcommands = group.commands
            if len(subcommands) == 0:
                return await self._send_command_help(interaction, group)
            entries = await self._filter_commands(subcommands, interaction=interaction, sort=True)
            if len(entries) == 0:
                return await self._send_command_help(interaction, group)

        elif isinstance(group, commands.Group):
            subcommands = group.commands
            if len(subcommands) == 0:
                return await self._send_command_help(interaction, group)

            entries = await self._filter_commands(subcommands, interaction=interaction,sort=True)
            if len(entries) == 0:
                return await self._send_command_help(interaction, group)

    def _common_command_formatting(
        self, embed_like: discord.Embed, _command: app_commands.Command
    ):
        embed_like.title = self.get_command_signature(_command)
        if _command.description:
            embed_like.description = f"{_command.description}"
        else:
            embed_like.description = "No help found..."

    async def _command_callback(
        self, interaction: discord.Interaction, *, _command=None
    ):
        """|coro|
        The actual implementation of the help command.

        - :meth:`_send_bot_help`
        - :meth:`_send_cog_help`
        - :meth:`_send_group_help`
        - :meth:`_send_command_help`
        """
        await self.prepare_help_command(interaction, _command)
        bot = self.bot

        #  If no command, send help for the whole bot
        if not _command:
            return await self._send_bot_help(interaction=interaction)

        # Check if it's a cog
        cog = bot.get_cog(_command)
        if cog:
            return await self._send_cog_help(interaction=interaction, cog=cog)

        # If it's not a cog then it's a command.
        # Since we want to have detailed errors when someone
        # passes an invalid subcommand, we need to walk through
        # the command group chain ourselves.

        slash = (
            self.bot.tree.get_command(
                _command,
                guild=interaction.guild,
            ),
            self.bot.tree.get_command(
                _command, guild=None
            ),
        )[0]

        regular_command = self.bot.get_command(_command)
        cog = self.bot.get_cog(_command)

        if isinstance(slash, app_commands.Command):
            return await self._send_command_help(interaction, slash)
        elif isinstance(slash, app_commands.Group):
            return await self._send_group_help(interaction, slash)
        if isinstance(regular_command, commands.Group):
            return await self._send_group_help(interaction, regular_command)
        elif isinstance(regular_command, commands.Command):
            return await self._send_command_help(interaction, regular_command)
        if cog:
            return await self._send_cog_help(interaction, cog)
        if not slash and not regular_command and not cog:
            return await interaction.response.send_message(
                "Couldn't find command or cog"
            )

    async def prepare_help_command(
        self, interaction: discord.Interaction, _command=None
    ) -> Union[
        None, Coroutine, List[Union[commands.Command, Any, app_commands.Command]]
    ]:
        """|coro|
        A low level method that can be used to prepare the help command
        before it does anything. For example, if you need to prepare
        some state in your subclass before the command does its processing
        then this would be the place to do it.
        The default implementation does nothing.
        .. note::
            This is called *inside* the help command callback body. So all
            the usual rules that happen inside apply here as well.
        Parameters
        -----------
        interaction: :class:`Interaction`
            The invocation context.
        _command: Optional[:class:`str`]
            The argument passed to the help command.
        """
        pass

    @property
    def display_emoji(self) -> str:
        return "❔"

    @command()
    @describe(object="Name of command, cog or command group")
    async def help(
        self, interaction: discord.Interaction, object: Optional[str] = None
    ):

        await self._command_callback(interaction, _command=object)
        # Maybe add autocomplete for commands in the future


async def setup(bot: Timmy):
    await bot.add_cog(Help(bot))
