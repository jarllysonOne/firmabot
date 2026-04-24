import discord
from discord.ext import tasks
from datetime import datetime
from utils import db, config


class TaskLoop:
    def __init__(self, bot):
        self.bot = bot
        self._verificar_avisos_task = None

    async def start(self):
        self._verificar_avisos_task = self.verificar_avisos.start()

    def stop(self):
        if self._verificar_avisos_task:
            self._verificar_avisos_task.cancel()

    @tasks.loop(minutes=1)
    async def verificar_avisos(self):
        if not config.channel_id:
            return

        canal = self.bot.get_channel(config.channel_id)
        if not canal:
            return

        agora = datetime.now().strftime("%H:%M")

        for nome, evento in db.get_eventos_ativos().items():
            if evento.hora == agora:
                from utils import EmbedBuilder
                
                embed = EmbedBuilder.create(
                    titulo=f"⏰ Aviso Agendado: {nome}",
                    descricao=evento.mensagem,
                    cor=discord.Color.red(),
                    footer_text=f"Horário: {agora}",
                    fields=[
                        {"name": "📛 Nome", "value": f"**{nome}**", "inline": True},
                        {"name": "💬 Mensagem", "value": evento.mensagem, "inline": True}
                    ]
                )
                
                await canal.send(embed=embed)
                db.update_evento(nome, ativo=False)

    @verificar_avisos.before_loop
    async def before_verificar(self):
        await self.bot.wait_until_ready()