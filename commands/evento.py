from discord.ext import commands
import re
import discord
from utils import db, EmbedBuilder
from discord import ui
from datetime import datetime


class BotoesRSVP(ui.View):
    def __init__(self, nome_evento: str, autor_id: int):
        super().__init__(timeout=None)
        self.nome_evento = nome_evento
        self.autor_id = autor_id

    @ui.button(label="✅ Confirmar", style=discord.ButtonStyle.success, custom_id="rsvp_confirmar")
    async def confirmar(self, interaction: discord.Interaction, button: ui.Button):
        user_id = str(interaction.user.id)
        evento = db.get_evento(self.nome_evento)

        if not evento:
            await interaction.response.send_message("❌ Evento não encontrado.", ephemeral=True)
            return

        if evento.limite_participantes and len(evento.confirmados) >= evento.limite_participantes:
            if user_id not in evento.confirmados and user_id not in evento.lista_espera:
                evento.lista_espera.append(user_id)
                db.update_evento(self.nome_evento, lista_espera=evento.lista_espera)
                await interaction.response.send_message("⏳ Você entrou na lista de espera!", ephemeral=True)
                await self.atualizar_msg(interaction)
                return

        if db.confirmar_participacao(self.nome_evento, user_id):
            if user_id in evento.lista_espera:
                evento.lista_espera.remove(user_id)
                db.update_evento(self.nome_evento, lista_espera=evento.lista_espera)

            evento = db.get_evento(self.nome_evento)
            embed = discord.Embed(
                title="🎉 Presença Confirmada!",
                description=f"Você confirmou presença no evento **{self.nome_evento}**",
                color=discord.Color.green()
            )
            embed.add_field(name="📊 Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)
            embed.add_field(name="❌ Recusados", value=f"**{len(evento.recusados)}**", inline=True)
            if evento.limite_participantes:
                embed.add_field(name="🎫 Limite", value=f"**{evento.limite_participantes}**", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.atualizar_msg(interaction)
        else:
            await interaction.response.send_message("❌ Erro ao confirmar.", ephemeral=True)

    @ui.button(label="❌ Recusar", style=discord.ButtonStyle.danger, custom_id="rsvp_recusar")
    async def recusar(self, interaction: discord.Interaction, button: ui.Button):
        user_id = str(interaction.user.id)

        if db.recusar_participacao(self.nome_evento, user_id):
            evento = db.get_evento(self.nome_evento)
            if evento and evento.lista_espera:
                if evento.limite_participantes and len(evento.confirmados) < evento.limite_participantes:
                    prox = evento.lista_espera.pop(0)
                    db.confirmar_participacao(self.nome_evento, prox)
                    db.update_evento(self.nome_evento, lista_espera=evento.lista_espera)
                    try:
                        guild = interaction.guild
                        member = guild.get_member(int(prox))
                        if member:
                            dm_embed = EmbedBuilder.success(
                                titulo="🎉 Vagas Liberadas!",
                                descricao=f"Você foi movido da lista de espera para confirmado no evento **{self.nome_evento}**!"
                            )
                            await member.send(embed=dm_embed)
                    except:
                        pass

            evento = db.get_evento(self.nome_evento)
            if evento:
                embed = discord.Embed(
                    title="❌ Presença Recusada",
                    description=f"Você declinedu participar do evento **{self.nome_evento}**",
                    color=discord.Color.red()
                )
                embed.add_field(name="📊 Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)
                embed.add_field(name="❌ Recusados", value=f"**{len(evento.recusados)}**", inline=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await self.atualizar_msg(interaction)
        else:
            await interaction.response.send_message("❌ Evento não encontrado.", ephemeral=True)

    async def atualizar_msg(self, interaction: discord.Interaction):
        try:
            evento = db.get_evento(self.nome_evento)
            if evento and interaction.message.embeds:
                emb = interaction.message.embeds[0]
                for field in emb.fields:
                    if field.name == "✅ Confirmados":
                        emb.set_field_at(emb.fields.index(field), name="✅ Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)
                    elif field.name == "❌ Recusados":
                        emb.set_field_at(emb.fields.index(field), name="❌ Recusados", value=f"**{len(evento.recusados)}**", inline=True)
                await interaction.message.edit(embed=emb, view=self)
        except:
            pass


class ComandosEvento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persisted_views = []

    @commands.command(name="evento")
    async def create_evento(self, ctx, *, texto: str = None):
        await ctx.message.delete()

        if not texto:
            embed = discord.Embed(
                title="🎭 Criar Evento",
                description="Use: `!evento data|descrição|@menções`\n\n"
                           "Opcional: `!evento data|descrição|@menções|lembrete`\n\n"
                           "Novos parâmetros:\n"
                           "`--everyone` - Menciona everyone (ex: `!evento 25/04|Jogo|--everyone`)\n"
                           "`--limite X` - Limita participantes (ex: `!evento 25/04|Jogo||15|--limite 5`)\n"
                           "`--recorrencia diario|semanal|mensal`\n\n"
                           "Ex: `!evento 25/04|Jogo de mesa|@player1|15|--everyone|--limite 10`",
                color=discord.Color.magenta()
            )
            embed.set_footer(text="Sistema de Eventos Avançado")
            await ctx.send(embed=embed)
            return

        everyone = "--everyone" in texto
        texto = texto.replace("--everyone", "").strip()

        limite = None
        limite_match = re.search(r'--limite\s+(\d+)', texto)
        if limite_match:
            limite = int(limite_match.group(1))
            texto = texto.replace(limite_match.group(0), "").strip()

        recorrencia = None
        rec_match = re.search(r'--recorrencia\s+(diario|semanal|mensal)', texto)
        if rec_match:
            recorrencia = rec_match.group(1)
            texto = texto.replace(rec_match.group(0), "").strip()

        parts = texto.split("|")
        if len(parts) < 2:
            embed = EmbedBuilder.error("Formato Inválido", "Use: `!evento data|descrição|@menções`")
            await ctx.send(embed=embed)
            return

        data = parts[0].strip()
        desc = parts[1].strip()
        mentions_text = parts[2].strip() if len(parts) > 2 else ""
        parti = re.findall(r'<@!?(\d+)>', mentions_text)

        lembrete = 15
        if len(parts) > 3:
            try:
                lembrete = int(parts[3].strip())
            except:
                lembrete = 15

        tipo = "everyone" if everyone else "normal"
        nome = desc[:30] if len(desc) < 30 else desc[:27] + "..."
        db.add_evento(nome, desc, data=data, participantes=["@" + p for p in parti],
                      lembrete_minutos=lembrete, tipo=tipo, recorrencia=recorrencia, limite_participantes=limite)

        embed = EmbedBuilder.evento_everyone(
            titulo=nome,
            descricao=f"{'@everyone ' if everyone else ''}{desc}",
            data=data,
            hora=""
        )

        if everyone:
            embed.description = f"@everyone\n{desc}"

        embed.add_field(name="✅ Confirmados", value="**0**", inline=True)
        embed.add_field(name="❌ Recusados", value="**0**", inline=True)
        if limite:
            embed.add_field(name="🎫 Limite", value=f"**{limite}**", inline=True)
        if recorrencia:
            embed.add_field(name="🔄 Recorrência", value=f"**{recorrencia.title()}**", inline=True)

        embed.set_footer(text=f"Criado por: {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url if ctx.author.display_avatar else None)

        view = BotoesRSVP(nome, ctx.author.id)
        self.persisted_views.append(view)

        if everyone:
            await ctx.send(content="@everyone", embed=embed, view=view)
        else:
            await ctx.send(embed=embed, view=view)

        if not everyone:
            for member in ctx.message.mentions:
                try:
                    dm_embed = discord.Embed(
                        title="🎟️ Você foi convidado para um evento!",
                        description=f"**{desc}**\n\n📅 Data: {data}\n\nUse os botões abaixo para confirmar ou recusar.",
                        color=discord.Color.magenta()
                    )
                    await member.send(embed=dm_embed, view=view)
                except:
                    pass

    @commands.command(name="eventos")
    async def listar_eventos(self, ctx):
        await ctx.message.delete()

        eventos = db.get_eventos_ativos()

        if not eventos:
            embed = discord.Embed(
                title="📅 Eventos Ativos",
                description="Nenhum evento ativo no momento.",
                color=discord.Color.greyple()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="📅 Eventos Ativos",
            description=f"Total: **{len(eventos)}** evento(s)",
            color=discord.Color.magenta()
        )

        for nome, evento in eventos.items():
            tipo_str = "🌐 Everyone" if evento.tipo == "everyone" else "👥 Normal"
            rec_str = f" • 🔄 {evento.recorrencia.title()}" if evento.recorrencia else ""
            limite_str = f" • 🎫 Limite: {evento.limite_participantes}" if evento.limite_participantes else ""
            embed.add_field(
                name=f"🎭 {nome}",
                value=f"📅 Data: {evento.data}\n{tipo_str}{rec_str}{limite_str}\n✅ Confirmados: **{len(evento.confirmados)}**\n❌ Recusados: **{len(evento.recusados)}**",
                inline=False
            )

        embed.set_footer(text="Use !evento para criar novo evento")
        await ctx.send(embed=embed)

    @commands.command(name="editar")
    async def editar_evento(self, ctx, nome: str, *, args: str):
        await ctx.message.delete()

        evento = db.get_evento(nome)
        if not evento:
            embed = EmbedBuilder.error("Evento Não Encontrado", f"Evento **{nome}** não existe.")
            await ctx.send(embed=embed)
            return

        updates = {}
        if "--desc" in args:
            desc_match = re.search(r'--desc\s+(.+)', args)
            if desc_match:
                updates["mensagem"] = desc_match.group(1).strip()

        if "--data" in args:
            data_match = re.search(r'--data\s+(\S+)', args)
            if data_match:
                updates["data"] = data_match.group(1).strip()

        if "--limite" in args:
            lim_match = re.search(r'--limite\s+(\d+)', args)
            if lim_match:
                updates["limite_participantes"] = int(lim_match.group(1))

        if updates:
            db.update_evento(nome, **updates)
            embed = EmbedBuilder.success("Evento Atualizado", f"Evento **{nome}** foi atualizado com sucesso!")
        else:
            embed = EmbedBuilder.warning("Nenhuma Alteração", "Use parâmetros como --desc, --data, --limite")

        await ctx.send(embed=embed)

    @commands.command(name="excluir")
    async def excluir_evento(self, ctx, *, nome: str):
        await ctx.message.delete()

        if db.delete_evento(nome):
            embed = EmbedBuilder.success("Evento Excluído", f"Evento **{nome}** foi excluído permanentemente.")
        else:
            embed = EmbedBuilder.error("Evento Não Encontrado", f"Evento **{nome}** não existe.")

        await ctx.send(embed=embed)

    @commands.command(name="encerrar")
    async def encerrar_evento(self, ctx, *, texto: str = None):
        await ctx.message.delete()

        if not texto:
            embed = EmbedBuilder.info("🎭 Encerrar Evento", "Use: `!encerrar nome_do_evento`")
            await ctx.send(embed=embed)
            return

        nome = texto.strip()
        evento = db.get_evento(nome)

        if not evento:
            embed = EmbedBuilder.error("Evento Não Encontrado", f"Evento **{nome}** não existe.")
            await ctx.send(embed=embed)
            return

        db.update_evento(nome, ativo=False, arquivado=True)

        embed = discord.Embed(
            title="✅ Evento Encerrado",
            description=f"Evento **{nome}** foi encerrado e arquivado.",
            color=discord.Color.green()
        )
        embed.add_field(name="✅ Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)
        embed.add_field(name="❌ Recusados", value=f"**{len(evento.recusados)}**", inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosEvento(bot))
