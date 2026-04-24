from discord.ext import commands
import discord
from utils import EmbedBuilder


class ComandosAviso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="aviso")
    async def create_aviso(self, ctx, *, texto: str = None):
        await ctx.message.delete()
        
        if not texto:
            embed = EmbedBuilder.create(
                titulo="📢 Criar Aviso",
                descricao="Use: `!aviso sua mensagem aqui`",
                cor=discord.Color.gold()
            )
            await ctx.send(embed=embed)
            return
        
        embed = EmbedBuilder.aviso(
            "Aviso",
            texto,
            footer_text=f"Criado por: {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url if ctx.author.display_avatar else None
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosAviso(bot))