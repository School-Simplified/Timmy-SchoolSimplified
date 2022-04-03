# Copyright (c) 2015-2021 Rapptz
# Copyright (c) 2022-present School Simplified


import asyncio
import inspect
import itertools
from typing import Any, Coroutine, Dict, List, Optional, Set, Union
from discord import app_commands
import discord
from discord.app_commands import command, describe, guilds
from discord.ext import commands, menus
from core.common import Others, get_guild_ids


class RoboPages(discord.ui.View):
    def __init__(
            self,
            source: menus.PageSource,
            *,
            interaction: discord.Interaction,
            check_embeds: bool = True,
            compact: bool = False,
            bot: commands.Bot,
    ):
        super().__init__()
        self.source: menus.PageSource = source
        self.check_embeds: bool = check_embeds
        self.interaction: discord.Interaction = interaction
        self.message: Optional[discord.Message] = None
        self.bot = bot
        self.current_page: int = 0
        self.compact: bool = compact
        self.input_lock = asyncio.Lock()
        self.clear_items()
        self.fill_items()

    def fill_items(self) -> None:
        if not self.compact:
            self.numbered_page.row = 1
            self.stop_pages.row = 1

        if self.source.is_paginating():
            max_pages = self.source.get_max_pages()
            use_last_and_first = max_pages is not None and max_pages >= 2
            if use_last_and_first:
                self.add_item(self.go_to_first_page)  # type: ignore
            self.add_item(self.go_to_previous_page)  # type: ignore
            if not self.compact:
                self.add_item(self.go_to_current_page)  # type: ignore
            self.add_item(self.go_to_next_page)  # type: ignore
            if use_last_and_first:
                self.add_item(self.go_to_last_page)  # type: ignore
            if not self.compact:
                self.add_item(self.numbered_page)  # type: ignore
            self.add_item(self.stop_pages)  # type: ignore

    async def _get_kwargs_from_page(self, page: int) -> Dict[str, Any]:
        value = await discord.utils.maybe_coroutine(self.source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {'content': value, 'embed': None}
        elif isinstance(value, discord.Embed):
            return {'embed': value, 'content': None}
        else:
            return {}

    async def show_page(self, interaction: discord.Interaction, page_number: int) -> None:
        page = await self.source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(page_number)
        if kwargs:
            if interaction.response.is_done():
                if self.message:
                    await self.message.edit(**kwargs, view=self)
            else:
                await interaction.response.edit_message(**kwargs, view=self)

    def _update_labels(self, page_number: int) -> None:
        self.go_to_first_page.disabled = page_number == 0
        if self.compact:
            max_pages = self.source.get_max_pages()
            self.go_to_last_page.disabled = max_pages is None or (page_number + 1) >= max_pages
            self.go_to_next_page.disabled = max_pages is not None and (page_number + 1) >= max_pages
            self.go_to_previous_page.disabled = page_number == 0
            return

        self.go_to_current_page.label = str(page_number + 1)
        self.go_to_previous_page.label = str(page_number)
        self.go_to_next_page.label = str(page_number + 2)
        self.go_to_next_page.disabled = False
        self.go_to_previous_page.disabled = False
        self.go_to_first_page.disabled = False

        max_pages = self.source.get_max_pages()
        if max_pages is not None:
            self.go_to_last_page.disabled = (page_number + 1) >= max_pages
            if (page_number + 1) >= max_pages:
                self.go_to_next_page.disabled = True
                self.go_to_next_page.label = '…'
            if page_number == 0:
                self.go_to_previous_page.disabled = True
                self.go_to_previous_page.label = '…'

    async def show_checked_page(self, interaction: discord.Interaction, page_number: int) -> None:
        max_pages = self.source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(interaction, page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(interaction, page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in (self.bot.owner_id, interaction.user.id):
            return True
        await interaction.response.send_message('This pagination menu cannot be controlled by you, sorry!',
                                                ephemeral=True)
        return False

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    #     async def on_error(self, error: Exception, item: discord.ui.Item, interaction: discord.Interaction) -> None:
    #         if interaction.response.is_done():
    #             await interaction.followup.send(f'An unknown error occurred, sorry {error}', ephemeral=True)
    #             print(error)
    #         else:
    #             await interaction.response.send_message(f'An unknown error occurred, sorry {error}', ephemeral=True)
    #             print(error)

    async def start(self) -> None:
        if self.check_embeds and not self.interaction.channel.permissions_for(self.interaction.guild.me).embed_links:
            await self.interaction.response.send_message('Bot does not have embed links permission in this channel.')
            return

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        self.message = await self.interaction.response.send_message(**kwargs, view=self)

    @discord.ui.button(label='≪', style=discord.ButtonStyle.grey)
    async def go_to_first_page(self, interaction: discord.Interaction, button: discord.ui.Button, ):
        """go to the first page"""
        await self.show_page(interaction, 0)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.blurple)
    async def go_to_previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """go to the previous page"""
        await self.show_checked_page(interaction, self.current_page - 1)

    @discord.ui.button(label='Current', style=discord.ButtonStyle.grey, disabled=True)
    async def go_to_current_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label='Next', style=discord.ButtonStyle.blurple)
    async def go_to_next_page(self, interaction: discord.Interaction, button: discord.ui.Button, ):
        """go to the next page"""
        await self.show_checked_page(interaction, self.current_page + 1)

    @discord.ui.button(label='≫', style=discord.ButtonStyle.grey)
    async def go_to_last_page(self, interaction: discord.Interaction, button: discord.ui.Button, ):
        """go to the last page"""
        # The call here is safe because it's guarded by skip_if
        await self.show_page(interaction, self.source.get_max_pages() - 1)

    @discord.ui.button(label='Skip to page...', style=discord.ButtonStyle.grey)
    async def numbered_page(self, interaction: discord.Interaction, button: discord.ui.Button, ):
        """lets you type a page number to go to"""
        if self.input_lock.locked():
            await interaction.response.send_message('Already waiting for your response...', ephemeral=True)
            return

        if self.message is None:
            return

        async with self.input_lock:
            channel = self.message.channel
            author_id = interaction.user and interaction.user.id
            await interaction.response.send_message('What page do you want to go to?', ephemeral=True)

            def message_check(m):
                return m.author.id == author_id and channel == m.channel and m.content.isdigit()

            try:
                msg = await self.bot.wait_for('message', check=message_check, timeout=30.0)
            except asyncio.TimeoutError:
                await interaction.followup.send('Took too long.', ephemeral=True)
                await asyncio.sleep(5)
            else:
                page = int(msg.content)
                await msg.delete()
                await self.show_checked_page(interaction, page - 1)

    @discord.ui.button(label='Quit', style=discord.ButtonStyle.red)
    async def stop_pages(self, interaction: discord.Interaction, button: discord.ui.Button, ):
        """stops the pagination session."""
        await interaction.response.defer()
        await interaction.delete_original_message()
        self.stop()


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
            text = f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)'
            self.embed.set_footer(text=text)

        return self.embed


class GroupHelpPageSource(menus.ListPageSource):
    def __init__(
            self,
            group: Union[commands.Group, commands.Cog, app_commands.Group],
            commands: List[Union[commands.Command, app_commands.Command, app_commands.ContextMenu]],
            *,
            prefix: str
    ):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f'{self.group.qualified_name} Commands'
        self.description = self.group.description

    async def format_page(
            self,
            menu,
            _commands: List[Union[commands.Command, app_commands.Command, app_commands.Group]]
    ) -> discord.Embed:

        embed = discord.Embed(title=self.title, description=self.description, colour=discord.Colour.fuchsia())
        for _command in _commands:
            if isinstance(_command, commands.Command):
                signature = f'{_command.qualified_name} {_command.signature}'
                embed.add_field(name=signature, value=_command.short_doc or 'No help given...', inline=False)
            elif isinstance(_command, app_commands.Command):
                params = self.slash_param_signature(_command)
                signature = (f'{_command.root_parent} {_command.name} {params}' if _command.root_parent
                             else f'{_command.name} {params}')
                embed.add_field(
                    name=signature[:256], value=_command.description[:1024] or 'No help given...', inline=False
                )
            elif isinstance(_command, app_commands.Group):
                subcommands = self.slash_param_signature(_command)
                signature = f'{_command.name} {subcommands}'
                embed.add_field(
                    name=signature[:256], value=_command.description[:1024] or 'No help given...', inline=False
                )

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "/help command" for more info on a command.')
        return embed

    @staticmethod
    def slash_param_signature(_command: Union[app_commands.Command, app_commands.Group]) -> str:

        raw_sig = _command.to_dict()
        params: List[Dict[str, Union[int, List, str]]] = raw_sig["options"]

        if isinstance(_command, app_commands.Command):
            param_list: List[str] = []

            for name, param in params:
                if param["choices"]:
                    name = '|'.join(f'"{v}"' if isinstance(v, str) else str(v) for v in param["choices"])
                else:
                    name = name
                if not param["required"] or param["default"]:
                    param_list.append(f"[{name}]")
                else:
                    param_list.append(f"<{name}>")
            return " ".join(param_list)
        elif isinstance(_command, app_commands.Group):
            param_list = []
            for name, param in params:
                param_list.append(f"<{name}>")
                
            return " ".join(param_list)


class HelpSelectMenu(discord.ui.Select['HelpMenu']):
    def __init__(
            self,
            _commands: Dict[commands.Cog, List[Union[commands.Command, app_commands.Command]]],
            bot: commands.Bot
    ):
        super().__init__(
            placeholder='Select a category...',
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands = _commands
        self.bot = bot
        self.__fill_options()

    def __fill_options(self) -> None:
        self.add_option(
            label='Index',
            emoji='\N{WAVING HAND SIGN}',
            value='__index',
            description='The help page showing how to use the bot.',
        )
        for cog, __commands in self.commands.items():
            if not __commands:
                continue
            description = cog.description.split('\n', 1)[0] or None
            emoji = getattr(cog, 'display_emoji', None)
            self.add_option(label=cog.qualified_name, value=cog.qualified_name, description=description, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        if value == '__index':
            await self.view.rebind(FrontPageSource(), interaction)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message('Somehow this category does not exist?', ephemeral=True)
                return

            __commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message('This category has no commands for you', ephemeral=True)
                return

            source = GroupHelpPageSource(cog, __commands, prefix="/")
            await self.view.rebind(source, interaction)


class HelpMenu(RoboPages):
    def __init__(self, source: menus.PageSource, interaction: discord.Interaction, bot: commands.Bot):
        super().__init__(source, interaction=interaction, compact=True, bot=bot)

    def add_categories(self, _commands: Dict[commands.Cog, List[commands.Command]]) -> None:
        self.clear_items()
        self.add_item(HelpSelectMenu(_commands, self.bot))
        self.fill_items()

    async def rebind(self, source: menus.PageSource, interaction: discord.Interaction) -> None:
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
        embed = discord.Embed(title='Bot Help', colour=discord.Colour.blurple())
        embed.description = inspect.cleandoc(
            f"""
            Hello! Welcome to the help page.
            Use "/help command" for more info on a command.
            Use "/help category" for more info on a category.
            Use the dropdown menu below to select a category.
        """
        )
        embed.set_footer(text=f"Contact IT Dept. for any questions or concerns!")
        embed.set_thumbnail(url=Others.timmyBook_png)

        if self.index == 0:
            embed.add_field(
                name='Documentation Page',
                value=(
                    "https://timmy.schoolsimplified.org"
                ),
                inline=False,
            )
        elif self.index == 1:
            entries = (
                ('<argument>', 'This means the argument is __**required**__.'),
                ('[argument]', 'This means the argument is __**optional**__.'),
                ('[A|B]', 'This means that it can be __**either A or B**__.'),
                (
                    '[argument...]',
                    'This means you can have multiple arguments.\n'
                    'Now that you know the basics, it should be noted that...\n'
                    '__**You do not type in the brackets!**__',
                ),
            )

            embed.add_field(name='How do I use this bot?', value='Reading the bot signature is pretty simple.')

            for name, value in entries:
                embed.add_field(name=name, value=value, inline=False)

        return embed


class Help(commands.Cog):
    """
    Help command
    """

    ALL_GUILD_IDS = ... # type: tuple

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        ALL_GUILD_IDS = get_guild_ids(self.bot)

    @staticmethod
    async def _filter_commands(
            _commands: Union[Set[Any], List[Union[app_commands.Command, commands.Command, Any]]],
            *,
            sort=False,
            key=None
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
            key = lambda c: c.qualified_name if isinstance(c, commands.Command) else c.name
        #
        iterator = _commands
        # iterator = commands if show_hidden else filter(lambda c: not c.hidden, commands)
        #
        # async def predicate(
        #         cmd: Union[app_commands.Command[Any], commands.Command[Any, Any, Any]]
        # ) -> bool:
        #     try:
        #         return await cmd.can_run()
        #     except commands.CommandError:
        #         return False
        #
        # ret = []
        # for cmd in iterator:
        #     valid = await predicate(cmd)
        #     if valid:
        #         ret.append(cmd)
        #
        # if sort:
        #     ret.sort(key=key)
        # return ret
        # TODO IMPLEMENT CHECKS

        return sorted(iterator, key=key) if sort else list(iterator)

    @staticmethod
    def get_command_signature(
            _command: Union[app_commands.Command, commands.Command]
    ):
        if isinstance(_command, commands.Command):
            parent = _command.full_parent_name
            if len(_command.aliases) > 0:
                aliases = ' | '.join(_command.aliases)
                fmt = f'[{_command.name}|{aliases}]'
                if parent:
                    fmt = f'{parent} {fmt}'
                alias = fmt
            else:
                alias = _command.name if not parent else f'{parent} {_command.name}'
            return f'{alias} {_command.signature}'
        elif isinstance(_command, app_commands.Command):
            return f'{_command.parent.name} {_command.name}'

    async def _send_bot_help(self, interaction: discord.Interaction) -> None:

        def key(_command: Union[app_commands.Command, commands.Command]) -> str:
            if isinstance(_command, app_commands.Command):
                _cog: commands.Cog = _command.binding if isinstance(_command.binding, commands.Cog) else None
            else:
                _cog: commands.Cog = _command.cog
            return _cog.qualified_name if _cog else '\U0010ffff'

        # sort guild and global slash commands, regular commands
        entries: Union[Set[Any], List[Union[commands.Command, app_commands.Command]]] = await self._filter_commands(
            [
                x for x in (
                *self.bot.tree.walk_commands(guild=discord.Object(interaction.guild.id)),
                *self.bot.tree.walk_commands(),
                *self.bot.commands
            )
                if isinstance(x, (app_commands.Command, commands.Command))
            ],
            sort=True,
            key=key
        )

        all_commands: Dict[commands.Cog, Union[Set[Any], List[Union[commands.Command, app_commands.Command, Any]]]] = {}
        for name, children in itertools.groupby(entries, key=key):
            if name == '\U0010ffff':
                continue

            cog = self.bot.get_cog(name)
            all_commands[cog] = sorted(
                children, key=lambda c: c.qualified_name if isinstance(c, commands.Command) else c.name
            )

        menu = HelpMenu(FrontPageSource(), interaction=interaction, bot=self.bot)
        menu.add_categories(all_commands)
        await menu.start()

    async def _send_cog_help(self, interaction: discord.Interaction, cog: commands.Cog):
        __commands = [*cog.get_commands(), *cog.__cog_app_commands__]
        entries = await self._filter_commands(__commands, sort=True)
        menu = HelpMenu(GroupHelpPageSource(cog, entries, prefix="/"), interaction=interaction, bot=self.bot)
        await menu.start()

    def reg_common_command_formatting(self, embed_like: discord.Embed, _command: commands.Command):
        embed_like.title = self.get_command_signature(_command)
        if _command.description:
            embed_like.description = f'{_command.description}\n\n{_command.help}'
        else:
            embed_like.description = _command.help or 'No help found...'

    async def _send_command_help(
            self,
            interaction: discord.Interaction,
            _command: Union[commands.Command, app_commands.Command, Any]
    ):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=discord.Colour.fuchsia())

        if isinstance(_command, commands.Command):
            self.reg_common_command_formatting(embed, _command)

        if isinstance(_command, app_commands.Command):
            self._common_command_formatting(embed, _command)

        await interaction.response.send_message(embed=embed)

    async def _send_group_help(
            self,
            interaction: discord.Interaction,
            group: Union[List[Any], Set[Any], app_commands.Group, commands.Group]
    ):
        if isinstance(group, app_commands.Group):
            subcommands = group.commands
            if len(subcommands) == 0:
                return await self._send_command_help(interaction, group)
            entries = await self._filter_commands(subcommands, sort=True)
            if len(entries) == 0:
                return await self._send_command_help(interaction, group)

        elif isinstance(group, commands.Group):
            subcommands = group.commands
            if len(subcommands) == 0:
                return await self._send_command_help(interaction, group)

            entries = await self._filter_commands(subcommands, sort=True)
            if len(entries) == 0:
                return await self._send_command_help(interaction, group)

    def _common_command_formatting(self, embed_like: discord.Embed, _command: app_commands.Command):
        embed_like.title = self.get_command_signature(_command)
        if _command.description:
            embed_like.description = f'{_command.description}'
        else:
            embed_like.description = 'No help found...'

    async def _command_callback(self, interaction: discord.Interaction, *, _command=None):
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
                type=discord.AppCommandType.chat_input
            ), self.bot.tree.get_command(
                _command,
                guild=None,
                type=discord.AppCommandType.chat_input
            )
        )[0]

        regular_command = self.bot.get_command(_command)
        cog = self.bot.get_cog(_command)

        if isinstance(slash, app_commands.Command):
            return await self._send_command_help(interaction, slash)
        if isinstance(slash, app_commands.Group):
            return await self._send_group_help(interaction, slash)
        if isinstance(regular_command, commands.Group):
            return await self._send_group_help(interaction, regular_command)
        if isinstance(regular_command, commands.Command):
            return await self._send_command_help(interaction, regular_command)
        if cog:
            return await self._send_cog_help(interaction, cog)
        if not slash and not regular_command and not cog:
            return await interaction.response.send_message("Couldn't find command or cog")

    async def prepare_help_command(
            self,
            interaction: discord.Interaction,
            _command=None
    ) -> Union[None, Coroutine, List[Union[commands.Command, Any, app_commands.Command]]]:
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
    @guilds(*ALL_GUILD_IDS)
    async def help(self, interaction: discord.Interaction, object: Optional[str] = None):

        await self._command_callback(interaction, _command=object)
        # Maybe add autocomplete for commands in the future


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
