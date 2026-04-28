import discord
from discord.ext import commands
from discord.ui import View, Button
from datetime import datetime
import asyncio

from utils import EmbedBuilder, db, config


class EnqueteView(View):
    def __init__(self, autor_id: int, opcoes: list, message_id: int = None):
        super().__init__(timeout=None)
        self.autor_id = autor_id
        self.opcoes = opcoes[:10]
        self.votos = {i: [] for i in range(len(opcoes[:10]))}
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        self.message_id = message_id

    async def update_embed(self, interaction: discord.Interaction):
        embed = EmbedBuilder.enquete(
            titulo="Enquete Ativa",
            descricao="Clique em um botão para votar. Os resultados aparecem em tempo real!",
            opcoes=self.opcoes,
            autor=interaction.user.display_name,
            autor_icon=interaction.user.display_avatar.url
        )

        total_votos = sum(len(v) for v in self.votos.values())

        for i, opcao in enumerate(self.opcoes):
            qtd = len(self.votos[i])
            barra = "█" * int((qtd / max(total_votos, 1)) * 10) if total_votos > 0 else ""
            espacos = "░" * (10 - len(barra))
            porcentagem = f"{(qtd / max(total_votos, 1)) * 100:.1f}%" if total_votos > 0 else "0%"
            embed.add_field(
                name=f"{self.emojis[i]} {opcao}",
                value=f"`{qtd} voto(s)` • {barra}{espacos} • {porcentagem}",
                inline=False
            )

        embed.add_field(
            name="📈 Total de Votos",
            value=f"**{total_votos}** pessoa(s) votaram",
            inline=False
        )

        await interaction.message.edit(embed=embed, view=self)

    @discord.ui.button(label="1️⃣", style=discord.ButtonStyle.blurple, custom_id="enquete_0")
    async def option_1(self, interaction: discord.Interaction, button: Button):
        await self.handle_vote(interaction, 0)

    @discord.ui.button(label="2️⃣", style=discord.ButtonStyle.blurple, custom_id="enquete_1")
    async def option_2(self, interaction: discord.Interaction, button: Button):
        await self.handle_vote(interaction, 1)

    @discord.ui.button(label="3️⃣", style=discord.ButtonStyle.blurple, custom_id="enquete_2")
    async def option_3(self, interaction: discord.Interaction, button: Button):
        await self.handle_vote(interaction, 2)

    @discord.ui.button(label="4️⃣", style=discord.ButtonStyle.blurple, custom_id="enquete_3")
    async def option_4(self, interaction: discord.Interaction, button: Button):
        await self.handle_vote(interaction, 3)

    @discord.ui.button(label="5️⃣", style=discord.ButtonStyle.blurple, custom_id="enquete_4")
    async def option_5(self, interaction: discord.Interaction, button: Button):
        await self.handle_vote(interaction, 4)

    @discord.ui.button(label="✅", style=discord.ButtonStyle.green, custom_id="enquete_result")
    async def ver_resultados(self, interaction: discord.Interaction, button: Button):
        await self.update_embed(interaction)
        await interaction.response.send_message("📊 Resultados atualizados!", ephemeral=True)

    async def handle_vote(self, interaction: discord.Interaction, option_index: int):
        user_id = interaction.user.id

        for i in range(len(self.opcoes)):
            if user_id in self.votos[i]:
                self.votos[i].remove(user_id)

        self.votos[option_index].append(user_id)

        await self.update_embed(interaction)
        await interaction.response.send_message(
            f"✅ Voto registrado em **{self.opcoes[option_index]}**!",
            ephemeral=True
        )


class ComandosEnquete(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="enquete")
    async def enquete(self, ctx, *, args: str):
        """
        Cria uma enquete interativa com botões.

        Uso: !enquete Título | Descrição | Opção 1 | Opção 2 | Opção 3 ...
        Exemplo: !enquete Melhor jogo? | Vote no seu favorito | Minecraft | Roblox | GTA
        """
        partes = [p.strip() for p in args.split("|")]

        if len(partes) < 3:
            embed = EmbedBuilder.error(
                titulo="Formato Inválido",
                descricao="Use: `!enquete Título | Descrição | Opção 1 | Opção 2 ...`\nMínimo 2 opções."
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        titulo = partes[0]
        descricao = partes[1]
        opcoes = partes[2:12]

        if len(opcoes) < 2:
            embed = EmbedBuilder.error(
                titulo="Poucas Opções",
                descricao="A enquete precisa de pelo menos 2 opções."
            )
            await ctx.send(embed=embed, delete_after=10)
            return

        embed = EmbedBuilder.enquete(
            titulo=titulo,
            descricao=descricao,
            opcoes=opcoes,
            autor=ctx.author.display_name,
            autor_icon=ctx.author.display_avatar.url
        )

        view = EnqueteView(autor_id=ctx.author.id, opcoes=opcoes)
        await ctx.send(embed=embed, view=view)

        try:
            await ctx.message.delete()
        except:
            pass


async def setup(bot):
    await bot.add_cog(ComandosEnquete(bot))
