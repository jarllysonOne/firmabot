from discord.ext import commands
from utils import db, EmbedBuilder, config


class ComandosEvento(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="evento")
    async def create_evento(self, ctx, *, args: str):
        try:
            nome, data, mensagem = args.split("|")
            nome = nome.strip()
            data = data.strip()
            mensagem = mensagem.strip()
        except ValueError:
            embed = EmbedBuilder.error(
                "Formato Inválido",
                "Use: `!evento nome | data | mensagem`"
            )
            await ctx.send(embed=embed)
            return

        if db.add_evento(nome, mensagem, data):
            embed = EmbedBuilder.event(
                "🎭 Evento Criado",
                mensagem,
                data,
                fields=[
                    {"name": "📛 Nome", "value": f"**{nome}**", "inline": True},
                    {"name": "📅 Data", "value": f"**{data}**", "inline": True}
                ]
            )
        else:
            embed = EmbedBuilder.warning(
                "Evento Existente",
                f'O evento "{nome}" já existe no sistema.'
            )
        await ctx.send(embed=embed)

    @commands.command(name="aviso_hora")
    async def aviso_horario(self, ctx, hora: str, *, args: str):
        try:
            nome, mensagem = args.split("|")
            nome = nome.strip()
            mensagem = mensagem.strip()
        except ValueError:
            embed = EmbedBuilder.error(
                "Formato Inválido",
                "Use: `!aviso_hora HH:MM | nome | mensagem`"
            )
            await ctx.send(embed=embed)
            return

        if db.add_evento(nome, mensagem, hora=hora):
            embed = EmbedBuilder.event(
                "⏰ Aviso Agendado",
                mensagem,
                hora=hora,
                fields=[
                    {"name": "⏰ Horário", "value": f"**{hora}**", "inline": True},
                    {"name": "📛 Nome", "value": f"**{nome}**", "inline": True}
                ]
            )
        else:
            embed = EmbedBuilder.warning(
                "Aviso Existente",
                f'O aviso "{nome}" já existe no sistema.'
            )
        await ctx.send(embed=embed)

    @commands.command(name="listar_eventos")
    async def list_eventos(self, ctx):
        eventos = db.list_eventos()
        
        if not eventos:
            embed = EmbedBuilder.info(
                "🎭 Eventos",
                "Nenhum evento cadastrado no momento."
            )
            await ctx.send(embed=embed)
            return

        items = []
        for nome, evento in eventos.items():
            info = evento.data or evento.hora or ""
            items.append(f"• **{nome}** ({info}): {evento.mensagem}")

        embed = EmbedBuilder.create(
            titulo="🎭 Lista de Eventos",
            descricao="\n".join(items),
            cor_dinamica=True,
            footer_text=f"Total: {len(eventos)} evento(s)",
            fields=[
                {"name": "📊 Total", "value": f"**{len(eventos)}** eventos cadastrados", "inline": False}
            ]
        )
        await ctx.send(embed=embed)

    @commands.command(name="cancelar")
    async def cancelar_evento(self, ctx, nome: str):
        evento = db.get_evento(nome)
        
        if not evento:
            embed = EmbedBuilder.error(
                "Evento Não Encontrado",
                f'O evento/aviso "{nome}" não existe no sistema.'
            )
            await ctx.send(embed=embed)
            return

        db.update_evento(nome, ativo=False)
        
        embed = EmbedBuilder.warning(
            "⏹️ Evento Cancelado",
            f'O evento/aviso "{nome}" foi cancelado.'
        )
        await ctx.send(embed=embed)

    @commands.command(name="ativar")
    async def ativar_evento(self, ctx, nome: str):
        evento = db.get_evento(nome)
        
        if not evento:
            embed = EmbedBuilder.error(
                "Evento Não Encontrado",
                f'O evento/aviso "{nome}" não existe no sistema.'
            )
            await ctx.send(embed=embed)
            return

        db.update_evento(nome, ativo=True)
        
        embed = EmbedBuilder.success(
            "▶️ Evento Ativado",
            f'O evento/aviso "{nome}" foi reativado.'
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ComandosEvento(bot))