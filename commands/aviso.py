from discord.ext import commands
from discord import ui, Interaction
from utils import db, EmbedBuilder


class AvisoModal(ui.Modal):
    def __init__(self):
        super().__init__(title="📢 Criar Aviso")
        self.mensagem = ui.TextInput(
            label="Mensagem",
            placeholder="Digite o aviso...",
            style=ui.TextStyle.paragraph,
            required=True,
            max_length=2000
        )
        self.add_item(self.mensagem)

    async def on_submit(self, interaction):
        embed = EmbedBuilder.aviso(
            "📢 Aviso",
            self.mensagem.value,
            footer_text=f"Criado por: {interaction.user.display_name}",
            footer_icon=interaction.user.display_avatar.url if interaction.user.display_avatar else None
        )
        await interaction.response.send_message(embed=embed)


class ComandosAviso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="aviso")
    async def create_aviso(self, ctx):
        await ctx.message.delete()
        await ctx.send("📢 **Clique no botão abaixo para criar um aviso:**", view=AvisoView())


async def setup(bot):
    await bot.add_cog(ComandosAviso(bot))


class AvisoView(ui.View):
    @ui.button(label="Criar Aviso", style=1, emoji="📢")
    async def callback(self, interaction, button):
        await interaction.response.send_modal(AvisoModal())