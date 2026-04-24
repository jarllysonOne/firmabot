from discord.ext import commands
from utils import db, EmbedBuilder


class ComandosAviso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="aviso")
    async def create_aviso(self, ctx, *, args: str):
        try:
            nome, mensagem = args.split("|")
            nome = nome.strip()
            mensagem = mensagem.strip()
        except ValueError:
            embed = EmbedBuilder.error(
                "Formato Inválido",
                "Use: `!aviso nome | mensagem`"
            )
            await ctx.send(embed=embed)
            return

        if db.add_aviso(nome, mensagem):
            embed = EmbedBuilder.success(
                "✅ Aviso Criado",
                f"**{nome}**\n{mensagem}",
                fields=[
                    {"name": "📝 Nome", "value": nome, "inline": True},
                    {"name": "💬 Mensagem", "value": mensagem, "inline": True}
                ]
            )
        else:
            embed = EmbedBuilder.warning(
                "Aviso Existente",
                f"O aviso **{nome}** já existe no sistema."
            )
        await ctx.send(embed=embed)

    @commands.command(name="listar_avisos")
    async def list_avisos(self, ctx):
        avisos = db.list_avisos()
        
        if not avisos:
            embed = EmbedBuilder.info(
                "📋 Avisos",
                "Nenhum aviso cadastrado no momento."
            )
            await ctx.send(embed=embed)
            return

        items = []
        for nome, aviso in avisos.items():
            items.append(f"• **{nome}**: {aviso.mensagem}")

        embed = EmbedBuilder.create(
            titulo="📋 Lista de Avisos",
            descricao="\n".join(items),
            cor_dinamica=True,
            footer_text=f"Total: {len(avisos)} aviso(s)",
            fields=[
                {"name": "📋 Total", "value": f"**{len(avisos)}** avisos cadastrados", "inline": False}
            ]
        )
        await ctx.send(embed=embed)

    @commands.command(name="enviar_aviso")
    async def enviar_aviso(self, ctx, nome: str, mencionar: str = None):
        aviso = db.get_aviso(nome)
        
        if not aviso:
            embed = EmbedBuilder.error(
                "Aviso Não Encontrado",
                f'O aviso "{nome}" não existe no sistema.'
            )
            await ctx.send(embed=embed)
            return

        embed = EmbedBuilder.aviso(
            f"📢 Aviso: {nome}",
            aviso.mensagem,
            footer_text=f"Avisado por: {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url if ctx.author.display_avatar else None
        )
        
        mensagem = await ctx.send(embed=embed)
        
        if mencionar and mencionar.lower() == "everyone":
            await ctx.send("@everyone")

    @commands.command(name="del_aviso")
    async def delete_aviso(self, ctx, nome: str):
        if db.delete_aviso(nome):
            embed = EmbedBuilder.success(
                "🗑️ Aviso Removido",
                f'O aviso "{nome}" foi removido com sucesso.'
            )
        else:
            embed = EmbedBuilder.error(
                "Aviso Não Encontrado",
                f'O aviso "{nome}" não existe no sistema.'
            )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosAviso(bot))