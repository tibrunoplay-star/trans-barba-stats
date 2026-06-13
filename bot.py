import discord
from discord.ext import commands
import psycopg
import os
import re

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

CANAL_RANKING = 1515340150920446112

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

conn = psycopg.connect(DATABASE_URL)

with conn.cursor() as cur:
cur.execute("""
CREATE TABLE IF NOT EXISTS ranking_semanal (
motorista TEXT PRIMARY KEY,
km BIGINT NOT NULL DEFAULT 0
)
""")
conn.commit()

@bot.event
async def on_ready():
print(f"Bot ligado: {bot.user}")

@bot.event
async def on_message(message):

```
if message.author.bot and message.embeds:

    try:
        embed = message.embeds[0]

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

                km = int(
                    match.group(1).replace(" ", "")
                )

                with conn.cursor() as cur:

                    cur.execute("""
                        INSERT INTO ranking_semanal
                        (motorista, km)
                        VALUES (%s, %s)
                        ON CONFLICT (motorista)
                        DO UPDATE SET
                        km = ranking_semanal.km + EXCLUDED.km
                    """, (motorista, km))

                    conn.commit()

                print(f"{motorista} +{km} km")

    except Exception as e:
        print("ERRO:", e)

await bot.process_commands(message)
```

@bot.command()
async def ranking(ctx):

````
with conn.cursor() as cur:

    cur.execute("""
        SELECT motorista, km
        FROM ranking_semanal
        ORDER BY km DESC
        LIMIT 10
    """)

    rows = cur.fetchall()

if not rows:
    await ctx.send("Sem dados.")
    return

texto = "🏆 Ranking Semanal\n\n"

for pos, (nome, km) in enumerate(rows, start=1):
    texto += f"{pos}. {nome} - {km:,} km\n"

await ctx.send(f"```{texto}```")
````

bot.run(TOKEN)
