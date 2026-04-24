from discord.ext import commands
import re
import discord
from utils import db, EmbedBuilder


class ComandosEvento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="evento")
    async def create_evento(self, ctx, *, texto: str = None):
        await ctx.message.delete()
        
        if not texto:
            embed = EmbedBuilder.create(
                titulo="🎭 Criar Evento",
                descricao="Use: `!evento data|descrição|@menções`\n\nEx: `!evento 25/04|Jogo de mesa|@玩家1 @玩家2`",
                cor=discord.Color.magenta()
            )
            await ctx.send(embed=embed)
            return
        
        try:
            parts = texto.split("|")
            if len(parts) < 2:
                await ctx.send("⚠️ Use: `!evento data|descrição|@menções`")
                return
            
            data = parts[0].strip()
            desc = parts[1].strip()
            parti = re.findall(r'<@!?\d+>', parts[2]) if len(parts) > 2 else []
            
            nome = desc[:30] if len(desc) < 30 else desc[:27] + "..."
            db.add_evento(nome, desc, data=data, participantes=parti)
            
            campos = []
            if parti:
                user_mentions = []
                for men in parti:
                    user_mentions.append(men)
                campos.append({"name": "👥 Participantes", "value": " ".join(user_mentions), "inline": True})
            
            embed = EmbedBuilder.evento(
                data,
                desc,
                data=data,
                campos=campos,
                footer_text=f"Criado por: {ctx.author.display_name}",
                footer_icon=ctx.author.display_avatar.url if ctx.author.display_avatar else None
            )
            await ctx.send(embed=embed)
            
            for men in parti:
                try:
                    uid = int(men.strip('<@!>'))
                    user = ctx.guild.get_member(uid)
                    if user:
                        emb = EmbedBuilder.evento(
                            "Você foi convidado!",
                            desc,
                            data=data
                        )
                        await user.send(embed=emb)
                except:
                    pass
            
        except Exception as e:
            await ctx.send(f"⚠️ Erro: {e}")


async def setup(bot):
    await bot.add_cog(ComandosEvento(bot))