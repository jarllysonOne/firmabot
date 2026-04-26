import discord
from discord.ext import commands
from utils import EmbedBuilder, config


class ComandosMention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="everyone")
    async def mention_everyone(self, ctx, *, mensagem: str = None):
        embed = EmbedBuilder.create(
            titulo="📢 Mention Global",
            descricao=mensagem or "Atenção todos!",
            cor_dinamica=True,
            footer_text=f"Solicitado por: {ctx.author.display_name}",
            footer_icon=ctx.author.display_avatar.url if ctx.author.display_avatar else None,
            fields=[
                {"name": "👤 Solicitante", "value": ctx.author.mention, "inline": True},
                {"name": "🏠 Servidor", "value": ctx.guild.name, "inline": True}
            ]
        )
        
        msg = await ctx.send(embed=embed)
        await ctx.send("@everyone")

    @commands.command(name="filtrar")
    async def filtrar_membros(self, ctx, *, args: str = None):
        if not args:
            embed = EmbedBuilder.info(
                "🔍 Filtrar Membros",
                "Use: `!filtrar @cargo` ou `!filtrar nome_do_cargo`"
            )
            await ctx.send(embed=embed)
            return

        role_name = args.strip()
        role = None
        
        if ctx.message.role_mentions:
            role = ctx.message.role_mentions[0]
        else:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if not role:
            roles_found = [r.name for r in ctx.guild.roles if role_name.lower() in r.name.lower()]
            embed = EmbedBuilder.error(
                "Cargo Não Encontrado",
                f'Cargo "{role_name}" não encontrado.\n\nCargos similares: {", ".join(roles_found[:5]) if roles_found else "Nenhum"}'
            )
            await ctx.send(embed=embed)
            return

        membros = [m for m in ctx.guild.members if role in m.roles]
        
        if not membros:
            embed = EmbedBuilder.warning(
                "Sem Membros",
                f"Nenhum membro com o cargo **{role.name}**"
            )
            await ctx.send(embed=embed)
            return

        lista = "\n".join([f"• {m.mention} ({m.display_name})" for m in membros[:25]])
        footer = f"Mostrando {min(len(membros), 25)} de {len(membros)} membros"

        embed = EmbedBuilder.create(
            titulo=f"🔍 Membros com {role.name}",
            descricao=lista + (f"\n...e mais {len(membros) - 25}" if len(membros) > 25 else ""),
            cor_dinamica=True,
            footer_text=footer,
            thumbnail_url=ctx.guild.icon.url if ctx.guild.icon else None,
            fields=[
                {"name": "📊 Total", "value": f"**{len(membros)}** membros", "inline": True},
                {"name": "🎭 Cargo", "value": role.mention, "inline": True}
            ]
        )
        await ctx.send(embed=embed)

    @commands.command(name="mencionar")
    async def mention_cargo(self, ctx, cargo_id: int = None, *, mensagem: str = None):
        role = ctx.guild.get_role(cargo_id) if cargo_id else None
        
        if not role:
            embed = EmbedBuilder.error(
                "Cargo Não Encontrado",
                "Mencione um cargo ou forneça o ID."
            )
            await ctx.send(embed=embed)
            return

        membros = [m for m in ctx.guild.members if role in m.roles]
        
        embed = EmbedBuilder.create(
            titulo=f"📢 Mencionando {role.name}",
            descricao=mensagem or f"@{role.name}",
            cor_dinamica=True,
            footer_text=f"Solicitado por: {ctx.author.display_name}",
            fields=[
                {"name": "👥 Membros", "value": f"**{len(membros)}**", "inline": True},
                {"name": "🎭 Cargo", "value": role.mention, "inline": True}
            ]
        )
        
        await ctx.send(embed=embed)
        for membro in membros[:100]:
            await ctx.send(membro.mention)


async def setup(bot):
    await bot.add_cog(ComandosMention(bot))