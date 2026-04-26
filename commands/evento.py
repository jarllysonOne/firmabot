from discord.ext import commands
import re
import discord
from utils import db, EmbedBuilder
from discord import ui


class BotoesRSVP(ui.View):
    def __init__(self, nome_evento: str, autor_id: int):
        super().__init__(timeout=None)
        self.nome_evento = nome_evento
        self.autor_id = autor_id

    @ui.button(label="✅ Confirmar", style=discord.ButtonStyle.success, custom_id="rsvp_confirmar")
    async def confirmar(self, interaction: discord.Interaction, button: ui.Button):
        user_id = str(interaction.user.id)
        
        if db.confirmar_participacao(self.nome_evento, user_id):
            evento = db.get_evento(self.nome_evento)
            if evento:
                embed = discord.Embed(
                    title="🎉 Presença Confirmada!",
                    description=f"Você confirmou presença no evento **{self.nome_evento}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="📊 Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)
                embed.add_field(name="❌ Recusados", value=f"**{len(evento.recusados)}**", inline=True)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await self.atualizar_msg(interaction)
        else:
            await interaction.response.send_message("❌ Evento não encontrado.", ephemeral=True)

    @ui.button(label="❌ Recusar", style=discord.ButtonStyle.danger, custom_id="rsvp_recusar")
    async def recusar(self, interaction: discord.Interaction, button: ui.Button):
        user_id = str(interaction.user.id)
        
        if db.recusar_participacao(self.nome_evento, user_id):
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
                await interaction.message.edit(embed=emb)
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
                description="Use: `!evento data|descrição|@menções`\n\nOpcional: `!evento data|descrição|@menções|lembrete`\n\nEx: `!evento 25/04|Jogo de mesa|@玩家1 @玩家2|15`\n\nO lembrete é em minutos (padrão: 15 min)",
                color=discord.Color.magenta()
            )
            embed.set_footer(text="Sistema de Eventos")
            await ctx.send(embed=embed)
            return
        
        parts = texto.split("|")
        if len(parts) < 2:
            embed = EmbedBuilder.error(
                "Formato Inválido",
                "Use: `!evento data|descrição|@menções`"
            )
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
        
        nome = desc[:30] if len(desc) < 30 else desc[:27] + "..."
        db.add_evento(nome, desc, data=data, participantes=["@" + p for p in parti], lembrete_minutos=lembrete)
        
        embed = discord.Embed(
            title="🎭 Novo Evento Criado!",
            description=f"**{desc}**",
            color=discord.Color.magenta(),
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="📅 Data", value=f"```{data}```", inline=True)
        
        if parti:
            user_mentions = []
            for uid_str in parti:
                try:
                    uid = int(uid_str)
                    member = ctx.guild.get_member(uid)
                    if member:
                        user_mentions.append(member.mention)
                except:
                    pass
            if user_mentions:
                embed.add_field(name="👥 Convidados", value=" ".join(user_mentions), inline=True)
        
        embed.add_field(name="✅ Confirmados", value="**0**", inline=True)
        embed.add_field(name="❌ Recusados", value="**0**", inline=True)
        
        embed.set_footer(text=f"Criado por: {ctx.author.display_name}", icon=ctx.author.display_avatar.url)
        
        view = BotoesRSVP(nome, ctx.author.id)
        self.persisted_views.append(view)
        await ctx.send(embed=embed, view=view)
        
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
            embed.add_field(
                name=f"🎭 {nome}",
                value=f"📅 Data: {evento.data}\n✅ Confirmados: **{len(evento.confirmados)}**\n❌ Recusados: **{len(evento.recusados)}**",
                inline=False
            )
        
        embed.set_footer(text="Use !evento para criar novo evento")
        await ctx.send(embed=embed)

    @commands.command(name="encerrar")
    async def encerrar_evento(self, ctx, *, texto: str = None):
        await ctx.message.delete()
        
        if not texto:
            embed = EmbedBuilder.info(
                "🎭 Encerrar Evento",
                "Use: `!encerrar nome_do_evento`"
            )
            await ctx.send(embed=embed)
            return
        
        nome = texto.strip()
        evento = db.get_evento(nome)
        
        if not evento:
            embed = EmbedBuilder.error(
                "Evento Não Encontrado",
                f"Evento **{nome}** não existe."
            )
            await ctx.send(embed=embed)
            return
        
        db.update_evento(nome, ativo=False)
        
        embed = discord.Embed(
            title="✅ Evento Encerrado",
            description=f"Evento **{nome}** foi encerrado.",
            color=discord.Color.green()
        )
        embed.add_field(name="✅ Confirmados", value=f"**{len(evento.confirmados)}**", inline=True)
        embed.add_field(name="❌ Recusados", value=f"**{len(evento.recusados)}**", inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosEvento(bot))