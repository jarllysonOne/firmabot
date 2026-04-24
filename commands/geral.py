from discord.ext import commands
from utils import EmbedBuilder


class ComandosGerais(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            cor = EmbedBuilder.success.__self__.__class__.color
            emoji = "🟢"
        elif latency < 200:
            emoji = "🟡"
        else:
            emoji = "🔴"
        
        embed = EmbedBuilder.create(
            titulo=f"{emoji} Pong!",
            descricao=f"Latência: **{latency}ms**",
            cor_dinamica=True,
            footer_text=f"Bot: {self.bot.user.display_name}" if self.bot.user else None
        )
        await ctx.send(embed=embed)

    @commands.command(name="info")
    async def info_bot(self, ctx):
        embed = EmbedBuilder.create(
            titulo=f"🤖 {self.bot.user.name}",
            descricao="Bot multifuncional para gerenciamento de avisos e eventos.",
            cor_dinamica=True,
            thumbnail_url=self.bot.user.display_avatar.url if self.bot.user.display_avatar else None,
            footer_text="Sistema de Automação Discord",
            fields=[
                {"name": "📡 Servidores", "value": f"**{len(self.bot.guilds)}**", "inline": True},
                {"name": "💠 Canais", "value": f"**{sum(len(g.channels) for g in self.bot.guilds)}**", "inline": True},
                {"name": "⏱️ Latência", "value": f"**{round(self.bot.latency * 1000)}ms**", "inline": True}
            ]
        )
        await ctx.send(embed=embed)

    @commands.command(name="ajuda")
    async def help_command(self, ctx):
        embed = EmbedBuilder.create(
            titulo="📚 Central de Ajuda",
            descricao="Lista de comandos disponíveis",
            cor_dinamica=True,
            footer_text="Use o prefixo ! para executar comandos",
            fields=[
                {"name": "📢 Avisos", "value": "`!aviso nome | mensagem`\n`!listar_avisos`\n`!enviar_aviso nome [everyone]`\n`!del_aviso nome`", "inline": False},
                {"name": "🎭 Eventos", "value": "`!evento nome | data | mensagem`\n`!aviso_hora HH:MM | nome | msg`\n`!listar_eventos`\n`!cancelar nome`\n`!ativar nome`", "inline": False},
                {"name": "📣 Menções", "value": "`!everyone msg` - Marque @everyone\n`!aqui msg` - Marque @here\n`!filtrar @cargo` - Filtre membros\n`!mencionar idcargo msg`", "inline": False},
                {"name": "🔧 Geral", "value": "`!ping` - Ver latência\n`!info` - Informações do bot\n`!help` - Esta mensagem", "inline": False}
            ]
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosGerais(bot))