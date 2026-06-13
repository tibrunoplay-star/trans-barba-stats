import discord
from discord.ext import commands
import os
import re
import json

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ARQUIVO = "ranking.json"

def carregar():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

@bot.event
async def on_ready():
    print(f"Bot ligado: {bot.user}")

@bot.event
async def on_message(message):

    if message.author.bot and message.embeds:

        embed = message.embeds[0]

        try:
            motorista = embed.author.name

            detalhes = embed.fields[2].value

            match = re.search(
                r"Distância Aceita:\s*([\d\s]+)\s*km",
                detalhes
            )

            if match:

                km = int(match.group(1).replace(" ", ""))

                ranking = carregar()

                ranking[motorista] = ranking.get(motorista, 0) + km

                guardar(ranking)

                print(
                    f"{motorista} +{km} km | Total: {ranking[motorista]}"
                )

        except Exception as e:
            print("ERRO:", e)

    await bot.process_commands(message)

@bot.command()
async def ranking(ctx):

    dados = carregar()

    if not dados:
        await ctx.send("Sem dados.")
        return

    ordenado = sorted(
        dados.items(),
        key=lambda x: x[1],
        reverse=True
    )

    texto = "🏆 Ranking da Trans Barba\n\n"

    for pos, (nome, km) in enumerate(ordenado[:10], start=1):
        texto += f"{pos}. {nome} - {km:,} km\n"

    await ctx.send(f"```{texto}```")

bot.run(TOKEN)
