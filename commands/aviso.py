from discord.ext import commands
import discord
import re
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
                descricao="Use: `!aviso mensagem`\n\nOpcional: `--everyone` ou `--here` para mencionar",
                cor=discord.Color.gold()
            )
            await ctx.send(embed=embed)
            return
        
        mention_mode = None
        if texto.startswith("--everyone"):
            mention_mode = "@everyone"
            texto = texto[11:].strip()
        elif texto.startswith("--here"):
            mention_mode = "@here"
            texto = texto[7:].strip()
        
        embed = EmbedBuilder.aviso(
            "Aviso",
            texto,
            footer_text=f"Criado por: {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url if ctx.author.display_avatar else None
        )
        
        if mention_mode:
            await ctx.send(f"{mention_mode}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosAviso(bot))