import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from utils import db, config


class TaskLoop:
    def __init__(self, bot):
        self.bot = bot
        self._verificar_avisos_task = None
        self._lembrete_task = None

    async def start(self):
        self._verificar_avisos_task = self.verificar_avisos.start()
        self._lembrete_task = self.verificar_lembretes.start()

    def stop(self):
        if self._verificar_avisos_task:
            self._verificar_avisos_task.cancel()
        if self._lembrete_task:
            self._lembrete_task.cancel()

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

    @tasks.loop(minutes=1)
    async def verificar_lembretes(self):
        if not config.channel_id:
            return

        canal = self.bot.get_channel(config.channel_id)
        if not canal:
            return

        agora = datetime.now()
        agora_str = agora.strftime("%H:%M")

        for nome, evento in db.get_eventos_ativos().items():
            if not evento.hora:
                continue

            try:
                hora_evento = datetime.strptime(evento.hora, "%H:%M")
                hora_evento = hora_evento.replace(
                    year=agora.year,
                    month=agora.month,
                    day=agora.day
                )

                diferenca = hora_evento - agora

                if diferenca.total_seconds() > 0 and diferenca.total_seconds() <= evento.lembrete_minutos * 60:
                    if diferenca.total_seconds() > (evento.lembrete_minutos - 1) * 60:
                        embed = discord.Embed(
                            title="⏰ Lembrete de Evento!",
                            description=f"**{evento.mensagem}**",
                            color=discord.Color.orange()
                        )
                        embed.add_field(name="📅 Data", value=f"**{evento.data}**", inline=True)
                        embed.add_field(name="🕐 Horário", value=f"**{evento.hora}**", inline=True)
                        embed.add_field(name="⏱️ Faltam", value=f"**~{int(diferenca.total_seconds() / 60)} minutos**", inline=True)
                        embed.add_field(name="✅ Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)

                        mentions = []
                        for uid in evento.confirmados:
                            member = canal.guild.get_member(int(uid))
                            if member:
                                mentions.append(member.mention)

                        if mentions:
                            await canal.send(" ".join(mentions[:10]))

                        await canal.send(embed=embed)

            except Exception as e:
                pass

    @verificar_lembretes.before_loop
    async def before_lembrete(self):
        await self.bot.wait_until_ready()