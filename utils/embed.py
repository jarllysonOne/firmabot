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
            footer_text="✅ Operação realizada com sucesso",
            **kwargs
        )

    @staticmethod
    def error(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.red(),
            footer_text="❌ Ocorreu um erro",
            **kwargs
        )

    @staticmethod
    def warning(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.orange(),
            footer_text="⚠️ Atenção",
            **kwargs
        )

    @staticmethod
    def info(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.blue(),
            footer_text="ℹ️ Informações",
            **kwargs
        )

    @staticmethod
    def event(titulo: str, descricao: str, data: str = "", **kwargs) -> discord.Embed:
        fields = [
            {"name": "📅 Data", "value": f"**{data}**", "inline": True},
        ]
        if kwargs.get("hora"):
            fields.insert(0, {"name": "🕐 Horário", "value": f"**{kwargs.pop('hora')}**", "inline": True})

        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.purple(),
            footer_text="🎭 Eventos do Servidor",
            fields=fields,
            **kwargs
        )

    @staticmethod
    def aviso(titulo: str, descricao: str, **kwargs) -> discord.Embed:
        return EmbedBuilder.create(
            titulo=titulo,
            descricao=descricao,
            cor=discord.Color.yellow(),
            footer_text="📢 Avisos",
            **kwargs
        )