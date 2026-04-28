import os
import sys
import traceback
import discord
from discord.ext import commands, tasks
from utils import config, db, EmbedBuilder
from utils.tasks import TaskLoop
from commands import ComandosAviso, ComandosEvento, ComandosGerais, ComandosMention, ComandosFicha, ComandosEnquete


class BotDiscord(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=config.prefix,
            intents=config.intents,
            owner_ids=config.owner_ids
        )
        self.task_loop = None

    async def setup_hook(self):
        await self.add_cog(ComandosAviso(self))
        await self.add_cog(ComandosEvento(self))
        await self.add_cog(ComandosGerais(self))
        await self.add_cog(ComandosMention(self))
        await self.add_cog(ComandosFicha(self))
        await self.add_cog(ComandosEnquete(self))

        self.task_loop = TaskLoop(self)
        await self.task_loop.start()

    async def on_ready(self):
        print(f"🤖 Bot iniciado como {self.user}")
        print(f"📡 Conectado em {len(self.guilds)} servidor(es)")


def main():
    if not config.token:
        print("❌ TOKEN não configurado no .env")
        sys.exit(1)

    bot = BotDiscord()

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = EmbedBuilder.error(
                "Argumento Faltante",
                f"Uso correto: `{ctx.command.usage}`" if ctx.command.usage else "Argumento necessário não fornecido."
            )
            await ctx.send(embed=embed)
            return

        traceback.print_exception(type(error), error, error.__traceback__)
        
        embed = EmbedBuilder.error(
            "Erro no Comando",
            str(error)
        )
        await ctx.send(embed=embed)

    bot.run(config.token, log_handler=None)


if __name__ == "__main__":
    main()
