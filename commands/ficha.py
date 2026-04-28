import discord
from discord.ext import commands
from datetime import datetime
import re

from utils import EmbedBuilder, db, config


class ComandosFicha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ficha")
    async def ficha(self, ctx, usuario: discord.Member, *, args: str = ""):
        """
        Envia uma ficha de personagem para um usuário.

        Uso:
        !ficha @usuario | Descrição da atualização
        !ficha @usuario --dm | Descrição da atualização
        !ficha @usuario https://url-da-imagem.com | Descrição
        !ficha @usuario --dm https://url-da-imagem.com | Descrição
        """
        imagem_url = None
        enviar_dm = False
        descricao = args

        if "--dm" in args:
            enviar_dm = True
            descricao = args.replace("--dm", "").strip()

        url_match = re.search(r'(https?://\S+)', descricao)
        if url_match:
            imagem_url = url_match.group(1)
            descricao = descricao.replace(imagem_url, "").strip()

        if "|" in descricao:
            partes = descricao.split("|", 1)
            descricao = partes[1].strip() if len(
                partes) > 1 else "Ficha atualizada"

        if not descricao:
            descricao = "A ficha foi atualizada!"

        criado_por = f"**{ctx.author.display_name}**\nHoje às {datetime.now().strftime('%H:%M')}"

        embed = EmbedBuilder.ficha(
            titulo="Ficha Atualizada!",
            descricao=f"📢 **Aviso**\n{ctx.author.mention}\n{descricao}",
            usuario=usuario,
            criado_por=criado_por,
            imagem_url=imagem_url
        )

        try:
            if enviar_dm:
                await usuario.send(embed=embed)
                embed_confirm = EmbedBuilder.success(
                    titulo="Ficha Enviada",
                    descricao=f"Ficha enviada para {usuario.mention} via mensagem direta."
                )
                await ctx.send(embed=embed_confirm, delete_after=5)
            else:
                await ctx.send(embed=embed)

            try:
                await ctx.message.delete()
            except:
                pass

        except discord.Forbidden:
            embed_erro = EmbedBuilder.error(
                titulo="Erro",
                descricao="Não foi possível enviar a mensagem. Verifique se o usuário aceita DMs ou se tenho permissões."
            )
            await ctx.send(embed=embed_erro, delete_after=10)


async def setup(bot):
    await bot.add_cog(ComandosFicha(bot))
