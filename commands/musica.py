import discord
from discord.ext import commands
from discord import ui
import asyncio
import yt_dlp
import time

from utils import EmbedBuilder, db, config


class MusicPlayer:
    def __init__(self):
        self.queues = {}
        self.current_song = {}
        self.voice_clients = {}

    def get_queue(self, guild_id):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]

    def add_to_queue(self, guild_id, song_info):
        self.get_queue(guild_id).append(song_info)

    def clear_queue(self, guild_id):
        if guild_id in self.queues:
            self.queues[guild_id] = []

    def remove_from_queue(self, guild_id, index):
        queue = self.get_queue(guild_id)
        if 0 <= index < len(queue):
            return queue.pop(index)
        return None


player = MusicPlayer()


class MusicControls(ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @ui.button(emoji="⏸️", style=discord.ButtonStyle.blurple, custom_id="music_pause")
    async def pause(self, interaction: discord.Interaction, button: ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Música pausada!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nenhuma música tocando.", ephemeral=True)

    @ui.button(emoji="▶️", style=discord.ButtonStyle.green, custom_id="music_resume")
    async def resume(self, interaction: discord.Interaction, button: ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Música retomada!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Música não está pausada.", ephemeral=True)

    @ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple, custom_id="music_skip")
    async def skip(self, interaction: discord.Interaction, button: ui.Button):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("⏭️ Música pulada!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nada tocando.", ephemeral=True)

    @ui.button(emoji="⏹️", style=discord.ButtonStyle.red, custom_id="music_stop")
    async def stop(self, interaction: discord.Interaction, button: ui.Button):
        vc = interaction.guild.voice_client
        if vc:
            player.clear_queue(interaction.guild.id)
            vc.stop()
            await vc.disconnect()
            await interaction.response.send_message("⏹️ Player parado e desconectado!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Não estou em um canal de voz.", ephemeral=True)

    @ui.button(emoji="📜", style=discord.ButtonStyle.grey, custom_id="music_queue")
    async def show_queue(self, interaction: discord.Interaction, button: ui.Button):
        queue = player.get_queue(interaction.guild.id)
        if not queue:
            await interaction.response.send_message("📜 Fila vazia!", ephemeral=True)
            return

        embed = discord.Embed(
            title="📜 Fila de Reprodução",
            color=discord.Color.blurple()
        )

        for i, song in enumerate(queue[:10]):
            duration = time.strftime('%M:%S', time.gmtime(song.get('duration', 0)))
            embed.add_field(
                name=f"{i+1}. {song['title']}",
                value=f"🎵 Duração: `{duration}` • Pedido por: {song['requested_by']}",
                inline=False
            )

        if len(queue) > 10:
            embed.set_footer(text=f"+ {len(queue) - 10} música(s) na fila")

        await interaction.response.send_message(embed=embed, ephemeral=True)


class ComandosMusica(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'extract_flat': False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str):
        if not ctx.author.voice:
            embed = EmbedBuilder.error("Você não está em um canal de voz", "Entre em um canal primeiro!")
            await ctx.send(embed=embed)
            return

        channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            vc = await channel.connect()
        else:
            vc = ctx.voice_client
            if vc.channel != channel:
                await vc.move_to(channel)

        embed_loading = EmbedBuilder.info("🔍 Procurando...", f"Procurando por: `{query}`")
        msg = await ctx.send(embed=embed_loading)

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                if 'entries' in info:
                    info = info['entries'][0]

                url = info.get('url', info.get('webpage_url'))
                title = info.get('title', 'Música Desconhecida')
                duration = info.get('duration', 0)
                thumbnail = info.get('thumbnail', '')

                song_info = {
                    'url': url,
                    'title': title,
                    'duration': duration,
                    'thumbnail': thumbnail,
                    'requested_by': ctx.author.mention
                }

                player.add_to_queue(ctx.guild.id, song_info)

                duration_str = time.strftime('%M:%S', time.gmtime(duration))
                embed_added = EmbedBuilder.success(
                    titulo="🎵 Adicionado à Fila",
                    descricao=f"**{title}**\n🎵 Duração: `{duration_str}`"
                )
                if thumbnail:
                    embed_added.set_thumbnail(url=thumbnail)
                await msg.edit(embed=embed_added)

                if not vc.is_playing():
                    await self.play_next(ctx)

        except Exception as e:
            embed_error = EmbedBuilder.error("Erro ao buscar música", str(e)[:100])
            await msg.edit(embed=embed_error)

    async def play_next(self, ctx):
        vc = ctx.voice_client
        if not vc:
            return

        queue = player.get_queue(ctx.guild.id)
        if not queue:
            await asyncio.sleep(10)
            if not player.get_queue(ctx.guild.id):
                await vc.disconnect()
                player.voice_clients.pop(ctx.guild.id, None)
            return

        song = queue[0]
        player.current_song[ctx.guild.id] = song

        try:
            source = discord.FFmpegPCMAudio(
                song['url'],
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
            source = discord.PCMVolumeTransformer(source, volume=0.5)

            def after_playing(error):
                if error:
                    print(f"Erro: {error}")
                queue.pop(0)
                player.current_song.pop(ctx.guild.id, None)
                asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

            vc.play(source, after=after_playing)

            duration_str = time.strftime('%M:%S', time.gmtime(song['duration']))
            embed_now = EmbedBuilder.create(
                titulo="🎶 Tocando Agora",
                descricao=f"**{song['title']}**\n🎵 Duração: `{duration_str}`\n👤 Pedido por: {song['requested_by']}",
                cor=discord.Color.blurple(),
                thumbnail_url=song.get('thumbnail')
            )
            await ctx.send(embed=embed_now, view=MusicControls(ctx.guild.id))

        except Exception as e:
            print(f"Erro ao tocar: {e}")
            queue.pop(0)
            await self.play_next(ctx)

    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        vc = ctx.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            embed = EmbedBuilder.success("⏭️ Pulado", "Música pulada!")
            await ctx.send(embed=embed)
        else:
            embed = EmbedBuilder.error("Nada tocando", "Não há música para pular.")
            await ctx.send(embed=embed)

    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        queue = player.get_queue(ctx.guild.id)
        if not queue:
            embed = EmbedBuilder.info("📜 Fila Vazia", "Nenhuma música na fila.")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="📜 Fila de Reprodução",
            color=discord.Color.blurple()
        )

        for i, song in enumerate(queue[:10]):
            duration = time.strftime('%M:%S', time.gmtime(song.get('duration', 0)))
            embed.add_field(
                name=f"{i+1}. {song['title']}",
                value=f"🎵 Duração: `{duration}` • Pedido por: {song['requested_by']}",
                inline=False
            )

        if len(queue) > 10:
            embed.set_footer(text=f"+ {len(queue) - 10} música(s) na fila")

        await ctx.send(embed=embed)

    @commands.command(name="pause")
    async def pause(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            embed = EmbedBuilder.warning("⏸️ Pausado", "Música pausada.")
            await ctx.send(embed=embed)
        else:
            embed = EmbedBuilder.error("Nada tocando", "Não há música para pausar.")
            await ctx.send(embed=embed)

    @commands.command(name="resume")
    async def resume(self, ctx):
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            embed = EmbedBuilder.success("▶️ Retomado", "Música retomada.")
            await ctx.send(embed=embed)
        else:
            embed = EmbedBuilder.error("Não pausado", "A música não está pausada.")
            await ctx.send(embed=embed)

    @commands.command(name="stop")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if vc:
            player.clear_queue(ctx.guild.id)
            vc.stop()
            await vc.disconnect()
            embed = EmbedBuilder.success("⏹️ Parado", "Player parado e desconectado!")
            await ctx.send(embed=embed)
        else:
            embed = EmbedBuilder.error("Não conectado", "Não estou em um canal de voz.")
            await ctx.send(embed=embed)

    @commands.command(name="nowplaying", aliases=["np"])
    async def now_playing(self, ctx):
        current = player.current_song.get(ctx.guild.id)
        if not current:
            embed = EmbedBuilder.info("🎵 Nada Tocando", "Nenhuma música tocando agora.")
            await ctx.send(embed=embed)
            return

        duration_str = time.strftime('%M:%S', time.gmtime(current['duration']))
        embed = EmbedBuilder.create(
            titulo="🎶 Tocando Agora",
            descricao=f"**{current['title']}**\n🎵 Duração: `{duration_str}`\n👤 Pedido por: {current['requested_by']}",
            cor=discord.Color.blurple(),
            thumbnail_url=current.get('thumbnail')
        )
        await ctx.send(embed=embed, view=MusicControls(ctx.guild.id))


async def setup(bot):
    await bot.add_cog(ComandosMusica(bot))
