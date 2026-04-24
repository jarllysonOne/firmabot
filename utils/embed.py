import discord
from datetime import datetime
from typing import Optional, List


class EmbedBuilder:
    @staticmethod
    def create(
        titulo: str,
        descricao: str,
        cor: Optional[discord.Color] = None,
        imagem_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        autor: Optional[str] = None,
        autor_icon: Optional[str] = None,
        footer_text: Optional[str] = None,
        footer_icon: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        fields: Optional[List[dict]] = None,
        cor_dinamica: bool = False,
    ) -> discord.Embed:
        if cor_dinamica:
            cor = discord.Color.from_hsv(datetime.now().timestamp() % 1, 0.7, 0.8)

        embed = discord.Embed(
            title=titulo,
            description=descricao,
            color=cor or discord.Color.random(),
            timestamp=timestamp or datetime.now()
        )

        if imagem_url:
            embed.set_image(url=imagem_url)

        if thumbnail_url:
            embed.set_thumbnail(url=thumbnail_url)

        if autor:
            embed.set_author(name=autor, icon_url=autor_icon or "")

        if footer_text:
            embed.set_footer(text=footer_text, icon_url=footer_icon or "")

        if fields:
            for field_data in fields:
                embed.add_field(
                    name=field_data.get("name", "\u200b"),
                    value=field_data.get("value", "\u200b"),
                    inline=field_data.get("inline", False)
                )

        return embed

    @staticmethod
    def success(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.green(),
            **kwargs
        )

    @staticmethod
    def error(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.red(),
            **kwargs
        )

    @staticmethod
    def warning(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.orange(),
            **kwargs
        )

    @staticmethod
    def info(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.blue(),
            **kwargs
        )

    @staticmethod
    def evento(titulo: str, descricao: str, data: str = "", hora: str = "", campos=None, **kwargs) -> discord.Embed:
        fields = []
        if data:
            fields.append({"name": "📅 Data", "value": f"**{data}**", "inline": True})
        if hora:
            fields.append({"name": "🕐 Horário", "value": f"**{hora}**", "inline": True})
        if campos:
            fields.extend(campos)

        return EmbedBuilder.create(
            titulo="🎭 " + titulo,
            descricao=descricao,
            cor=discord.Color.magenta(),
            fields=fields,
            **kwargs
        )

    @staticmethod
    def aviso(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo="📢 " + titulo,
            descricao=descricao,
            cor=discord.Color.gold(),
            **kwargs
        )