import os
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
avisos = {}
eventos = {}


@bot.event
async def on_ready():
    print(f"Bot iniciado como {bot.user}")
    verificar_avisos.start()


def embed_generator(titulo, descricao, cor=discord.Color.blue()):
    embed = discord.Embed(title=titulo, description=descricao,
                          color=cor, timestamp=datetime.now())
    return embed


@bot.command(name="aviso")
async def create_aviso(ctx, *, args: str):
    try:
        nome, mensagem = args.split("|")
        nome = nome.strip()
        mensagem = mensagem.strip()
        avisos[nome] = mensagem
        embed = embed_generator(
            "Aviso Criado", f"**{nome}**\n{mensagem}", discord.Color.green())
        await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("用法: !aviso nome | mensagem")


@bot.command(name="listar_avisos")
async def list_aviso(ctx):
    if not avisos:
        await ctx.send("Nenhum aviso encontrado.")
        return
    desc = "\n".join([f"• **{k}**: {v}" for k, v in avisos.items()])
    await ctx.send(embed=embed_generator("Avisos", desc))


@bot.command(name="aviso_hora")
async def aviso_horario(ctx, hora: str, *, args: str):
    try:
        nome, mensagem = args.split("|")
        nome = nome.strip()
        mensagem = mensagem.strip()
        eventos[nome] = {"hora": hora.strip(
        ), "mensagem": mensagem, "ativo": True}
        embed = embed_generator(
            "Aviso Agendado", f"**{nome}** às {hora}\n{mensagem}", discord.Color.orange())
        await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("用法: !aviso_hora HH:MM | nome | mensagem")


@bot.command(name="evento")
async def create_evento(ctx, *, args: str):
    try:
        nome, data, mensagem = args.split("|")
        nome = nome.strip()
        data = data.strip()
        mensagem = mensagem.strip()
        eventos[nome] = {"data": data, "mensagem": mensagem, "tipo": "evento"}
        embed = embed_generator(
            "Evento Criado", f"**{nome}**\n📅 {data}\n{mensagem}", discord.Color.purple())
        await ctx.send(embed=embed)
    except ValueError:
        await ctx.send("用法: !evento nome | data | mensagem")


@bot.command(name="listar_eventos")
async def list_evento(ctx):
    if not eventos:
        await ctx.send("Nenhum evento encontrado.")
        return
    desc = "\n".join(
        [f"• **{k}**: {v.get('mensagem', v)}" for k, v in eventos.items()])
    await ctx.send(embed=embed_generator("Eventos", desc))


@bot.command(name="enviar_aviso")
async def send_aviso(ctx, nome: str):
    if nome in avisos:
        embed = embed_generator(
            f"Aviso: {nome}", avisos[nome], discord.Color.yellow())
        await ctx.send(embed=embed)
    else:
        await ctx.send("Aviso não encontrado.")


@task.loop(minutes=1)
async def verificar_avisos():
    if not CHANNEL_ID:
        return
    agora = datetime.now().strftime("%H:%M")
    canal = bot.get_channel(CHANNEL_ID)
    if not canal:
        return
    for nome, dados in list(eventos.items()):
        if dados.get("ativo") and dados.get("hora") == agora:
            embed = embed_generator(
                f"Aviso Agendado: {nome}", dados["mensagem"], discord.Color.red())
            await canal.send(embed=embed)
            dados["ativo"] = False


@bot.command(name="cancelar")
async def cancelar(ctx, nome: str):
    if nome in eventos:
        eventos[nome]["ativo"] = False
        await ctx.send(f"Aviso '{nome}' cancelado.")
    else:
        await ctx.send("Aviso não encontrado.")
if __name__ == "__main__":
    bot.run(TOKEN)
