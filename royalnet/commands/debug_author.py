from ..utils import Command, CommandArgs, Call
from ..database.tables import Royal, Telegram


class DebugAuthorCommand(Command):

    command_name = "debug_author"
    command_title = "Ottieni informazioni sull'autore di questa chiamata."
    command_syntax = ""

    require_alchemy_tables = {Royal, Telegram}

    async def common(self, call: Call, args: CommandArgs):
        author = await call.get_author()
        if author is None:
            await call.reply(f"☁️ L'autore di questa chiamata è sconosciuto.")
        await call.reply(f"🌞 [c]{str(author)}[/c] è l'autore di questa chiamata.")
