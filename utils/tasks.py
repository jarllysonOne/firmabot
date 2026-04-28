import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from utils import db, config
import calendar


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

    def processar_recorrencia(self, nome, evento):
        """Processa eventos recorrentes, criando nova instância quando necessário"""
        if not evento.recorrencia or not evento.data:
            return

        hoje = datetime.now()
        try:
            data_evento = datetime.strptime(evento.data, "%d/%m")
            data_evento = data_evento.replace(year=hoje.year)
        except:
            return

        if data_evento.date() < hoje.date():
            nova_data = None
            if evento.recorrencia == "diario":
                nova_data = (hoje + timedelta(days=1)).strftime("%d/%m")
            elif evento.recorrencia == "semanal":
                nova_data = (hoje + timedelta(days=7)).strftime("%d/%m")
            elif evento.recorrencia == "mensal":
                mes_seguinte = hoje.month + 1 if hoje.month < 12 else 1
                ano_seguinte = hoje.year if hoje.month < 12 else hoje.year + 1
                try:
                    nova_data_obj = datetime(ano_seguinte if mes_seguinte == 1 else hoje.year,
                                            mes_seguinte, data_evento.day)
                    nova_data = nova_data_obj.strftime("%d/%m")
                except:
                    ultimo_dia = calendar.monthrange(
                        ano_seguinte if mes_seguinte == 1 else hoje.year,
                        mes_seguinte
                    )[1]
                    nova_data_obj = datetime(
                        ano_seguinte if mes_seguinte == 1 else hoje.year,
                        mes_seguinte,
                        ultimo_dia
                    )
                    nova_data = nova_data_obj.strftime("%d/%m")

            if nova_data:
                novo_nome = f"{evento.mensagem[:20]}... ({nova_data})" if len(evento.mensagem) > 20 else f"{evento.mensagem} ({nova_data})"
                db.add_evento(
                    nome=novo_nome,
                    mensagem=evento.mensagem,
                    data=nova_data,
                    hora=evento.hora,
                    participantes=evento.participantes,
                    lembrete_minutos=evento.lembrete_minutos,
                    tipo=evento.tipo,
                    recorrencia=evento.recorrencia,
                    limite_participantes=evento.limite_participantes
                )
                db.update_evento(nome, ativo=False, arquivado=True)

    @tasks.loop(minutes=1)
    async def verificar_avisos(self):
        if not config.channel_id:
            return

        canal = self.bot.get_channel(config.channel_id)
        if not canal:
            return

        agora = datetime.now().strftime("%H:%M")

        for nome, evento in list(db.get_eventos_ativos().items()):
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
                self.processar_recorrencia(nome, evento)
                if not evento.recorrencia:
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

        for nome, evento in list(db.get_eventos_ativos().items()):
            if not evento.hora:
                continue

            if evento.arquivado:
                continue

            try:
                hora_evento = datetime.strptime(evento.hora, "%H:%M")
                hora_evento = hora_evento.replace(
                    year=agora.year,
                    month=agora.month,
                    day=agora.day
                )

                diferenca = hora_evento - agora

                if 0 < diferenca.total_seconds() <= evento.lembrete_minutos * 60:
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

                        if evento.limite_participantes:
                            embed.add_field(name="🎫 Limite", value=f"**{evento.limite_participantes}**", inline=True)

                        mentions = []
                        for uid in evento.confirmados[:10]:
                            try:
                                member = canal.guild.get_member(int(uid))
                                if member:
                                    mentions.append(member.mention)
                            except:
                                pass

                        if mentions:
                            await canal.send(" ".join(mentions))

                        await canal.send(embed=embed)

            except Exception as e:
                pass

    @verificar_lembretes.before_loop
    async def before_lembrete(self):
        await self.bot.wait_until_ready()
