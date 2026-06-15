from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

RANKING_CHANNEL_ID = 1515340150920446112

async def publicar_ranking():

    canal = bot.get_channel(RANKING_CHANNEL_ID)

    if canal is None:
        return

    with conn.cursor() as cur:

        cur.execute("""
            SELECT motorista, km
            FROM ranking_semanal
            ORDER BY km DESC
            LIMIT 10
        """)

        rows = cur.fetchall()

    if not rows:
        await canal.send("Nenhum registo esta semana.")
        return

    texto = "🏆 **RANKING SEMANAL TRANS BARBA** 🏆\n\n"

    medalhas = ["🥇", "🥈", "🥉"]

    for pos, (nome, km) in enumerate(rows, start=1):

        if pos <= 3:
            texto += f"{medalhas[pos-1]} {nome} — {km:,} km\n"
        else:
            texto += f"{pos}. {nome} — {km:,} km\n"

    await canal.send(texto)

    with conn.cursor() as cur:
        cur.execute("DELETE FROM ranking_semanal")
        cur.execute("DELETE FROM lider_semanal")

    conn.commit()

    try:

       canal_lider = bot.get_channel(CANAL_LIDER_ID)

       if canal_lider:

          mensagem = await canal_lider.fetch_message(
              MENSAGEM_LIDER_ID
         )

         await mensagem.edit(
             content=
             "👑 **PASSA-ME SE FORES CAPAZ** 👑\n\n"
             "🚚 Ainda não existe líder esta semana.\n"
             "📏 Quilómetros: **0 km**"
        )

   except Exception as e:
       print(f"Erro ao reiniciar líder: {e}")
   

   print("Ranking semanal publicado e reiniciado.")

import os
import re
import discord
import psycopg
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg.connect(DATABASE_URL)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking_semanal (
            motorista TEXT PRIMARY KEY,
            km BIGINT NOT NULL DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS lider_semanal (
            motorista TEXT PRIMARY KEY,
            km BIGINT NOT NULL DEFAULT 0
        )
    """)

    conn.commit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():

    print(f"Bot ligado: {bot.user}")

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        publicar_ranking,
        "cron",
        day_of_week="sun",
        hour=22,
        minute=59
    )

    scheduler.start()

    print("Agendador semanal iniciado.")
    
@bot.event
async def on_message(message):

    if message.author.bot and message.embeds:

        try:
            embed = message.embeds[0]

            if not embed.author:
                await bot.process_commands(message)
                return

            motorista = embed.author.name

            detalhes = None

            for field in embed.fields:
                if field.name == "Detalhes":
                    detalhes = field.value
                    break

            if detalhes:

                match = re.search(
                    r"Distância Aceita:\s*([\d\s]+)\s*km",
                    detalhes
                )

                if match:

                    km = int(match.group(1).replace(" ", ""))

                    with conn.cursor() as cur:

    # Ranking semanal (acumula)
    cur.execute("""
        INSERT INTO ranking_semanal (motorista, km)
        VALUES (%s, %s)
        ON CONFLICT (motorista)
        DO UPDATE SET km = ranking_semanal.km + EXCLUDED.km
    """, (motorista, km))

    # Líder semanal (melhor entrega)
    cur.execute("""
        INSERT INTO lider_semanal (motorista, km)
        VALUES (%s, %s)
        ON CONFLICT (motorista)
        DO UPDATE SET km =
            GREATEST(lider_semanal.km, EXCLUDED.km)
    """, (motorista, km))

    conn.commit()

                    print(f"{motorista} +{km} km")

                    await atualizar_lider()

        except Exception as e:
            print("ERRO:", e)

    await bot.process_commands(message)

@bot.command()
async def ranking(ctx):

    with conn.cursor() as cur:

        cur.execute("""
            SELECT motorista, km
            FROM lider_semanal
            ORDER BY km DESC
            LIMIT 1

        rows = cur.fetchall()

    if not rows:
        await ctx.send("Sem dados.")
        return

    texto = "🏆 Ranking Semanal\n\n"

    for pos, (nome, km) in enumerate(rows, start=1):
        texto += f"{pos}. {km:,} km - {nome}\n"

    await ctx.send(f"```{texto}```")

CANAL_LIDER_ID = 1515340410694664344
MENSAGEM_LIDER_ID = 1515533850128945242

async def atualizar_lider():

    canal = bot.get_channel(CANAL_LIDER_ID)

    if canal is None:
        return

    with conn.cursor() as cur:

        cur.execute("""
            SELECT motorista, km
            FROM ranking_semanal
            ORDER BY km DESC
            LIMIT 1
        """)

        resultado = cur.fetchone()

    if resultado is None:
        return

    motorista, km = resultado

    try:

        mensagem = await canal.fetch_message(MENSAGEM_LIDER_ID)

        await mensagem.edit(
            content=
            "👑 **PASSA-ME SE FORES CAPAZ** 👑\n\n"
            f"🚚 Motorista: **{motorista}**\n"
            f"📏 Quilómetros: **{km:,} km**"
        )

    except Exception as e:
        print(f"Erro ao atualizar líder: {e}")

@bot.command()
async def criar_lider(ctx):

    msg = await ctx.send("A carregar líder...")

    print("ID DA MENSAGEM:", msg.id)
    
bot.run(TOKEN)
    
