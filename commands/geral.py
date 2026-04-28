from discord.ext import commands
from utils import EmbedBuilder


class ComandosGerais(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping")
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
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
        await ctx.message.delete()

        embed = EmbedBuilder.create(
            titulo="📚 Central de Ajuda",
            descricao="Lista de comandos disponíveis - Tudo que o bot pode fazer!",
            cor_dinamica=True,
            footer_text="Use o prefixo ! para executar comandos",
            fields=[
                {"name": "📢 Avisos", "value": "`!aviso [--everyone/--here] mensagem`\n`!aviso 25/04|Mensagem` - Aviso agendado", "inline": False},
                {"name": "🎭 Eventos (Atualizado)", "value":
                 "`!evento data|desc|@menc|lembrete|--everyone|--limite X|--recorrencia`\n"
                 "`!eventos` - Listar eventos ativos\n"
                 "`!editar nome --desc X --data X` - Editar evento\n"
                 "`!excluir nome` - Excluir evento\n"
                 "`!encerrar nome` - Encerrar evento", "inline": False},
                {"name": "📜 Ficha (Novo!)", "value":
                 "`!ficha @user | Descrição` - Enviar ficha no canal\n"
                 "`!ficha @user --dm | Descrição` - Enviar ficha por DM\n"
                 "`!ficha @user URL | Descrição` - Com imagem destacada", "inline": False},
                {"name": "📊 Enquetes (Novo!)", "value":
                 "`!enquete Título | Descrição | Opção1 | Opção2 ...`\n"
                 "Votação interativa com botões e resultados em tempo real!", "inline": False},
                {"name": "📣 Menções", "value":
                 "`!everyone msg` - Marque @everyone\n"
                 "`!filtrar @cargo` - Listar membros do cargo\n"
                 "`!mencionar ID_cargo` - Mencionar todos do cargo", "inline": False},
                {"name": "🔧 Geral", "value":
                 "`!ping` - Ver latência\n"
                 "`!info` - Informações do bot\n"
                 "`!ajuda` - Esta mensagem", "inline": False}
            ]
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosGerais(bot))