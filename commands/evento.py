from discord.ext import commands
from discord import ui
from utils import db, EmbedBuilder


class EventoModal(ui.Modal):
    def __init__(self):
        super().__init__(title="🎭 Criar Evento")
        self.nome = ui.TextInput(
            label="Nome do Evento",
            placeholder="Ex: Sessão de RPG",
            required=True,
            max_length=100
        )
        self.data = ui.TextInput(
            label="Data",
            placeholder="Ex: 25/04 às 19:00",
            required=True,
            max_length=50
        )
        self.mensagem = ui.TextInput(
            label="Descrição",
            placeholder="Detalhes do evento...",
            style=ui.TextStyle.paragraph,
            required=True,
            max_length=1500
        )
        self.participantes = ui.TextInput(
            label="Participantes (menções)",
            placeholder="@membro1 @membro2 ...",
            required=False,
            max_length=500
        )
        self.add_item(self.nome)
        self.add_item(self.data)
        self.add_item(self.mensagem)
        self.add_item(self.participantes)
        
    async def on_submit(self, interaction):
        participantes_list = self._parse_mentions(self.participantes.value)
        
        db.add_evento(
            self.nome.value,
            self.mensagem.value,
            data=self.data.value,
            participantes=participantes_list
        )
        
        fields = [
            {"name": "📅 Data", "value": f"**{self.data.value}**", "inline": True},
        ]
        if participantes_list:
            fields.append({"name": "👥 Participantes", "value": " ".join(participantes_list), "inline": True})
        
        embed = EmbedBuilder.event(
            "🎭 Evento Criado",
            self.mensagem.value,
            data=self.data.value,
            fields=fields,
            footer_text=f"Criado por: {interaction.user.display_name}",
            footer_icon=interaction.user.display_avatar.url if interaction.user.display_avatar else None
        )
        
        await interaction.response.send_message(embed=embed)
        
        if participantes_list:
            await self._send_dm(interaction, participantes_list)
    
    def _parse_mentions(self, text: str) -> list:
        import re
        return re.findall(r'<@!?\d+>', text)
    
    async def _send_dm(self, interaction, participantes: list):
        embed_dm = EmbedBuilder.event(
            "🎭 Convite para Sessão",
            self.mensagem.value,
            data=self.data.value,
            footer_text="Você foi convidado!",
        )
        
        for mention in participantes:
            user_id = int(mention.strip('<@!>'))
            user = interaction.guild.get_member(user_id)
            if user:
                try:
                    await user.send(embed=embed_dm)
                except:
                    pass


class ComandosEvento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="evento")
    async def create_evento(self, ctx):
        await ctx.message.delete()
        await ctx.send("🎭 **Clique no botão abaixo para criar um evento:**", view=EventoView())


async def setup(bot):
    await bot.add_cog(ComandosEvento(bot))


class EventoView(ui.View):
    @ui.button(label="Criar Evento", style=1, emoji="🎭")
    async def callback(self, interaction, button):
        await interaction.response.send_modal(EventoModal())