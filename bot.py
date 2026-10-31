import os
import discord
from discord.ext import tasks
from mcstatus import JavaServer

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = 1565395381687418900  # ID del canal de avisos

client = discord.Client(intents=discord.Intents.default())
tree = discord.app_commands.CommandTree(client)
server = JavaServer.lookup("167.58.9.228:25565", timeout=10)
last = None

@tree.command(name="status", description="Estado del server de Minecraft")
async def status(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        s = await server.async_status()
        if s.players.sample:
            nombres = ", ".join([p.name for p in s.players.sample])
        else:
            nombres = "Ninguno" if s.players.online == 0 else "Sin lista disponible"
            
        await interaction.followup.send(
            f"🟢 **Online:** {s.players.online}/{s.players.max} jugadores \n"
            f"👥 **Conectados:** {nombres}"
        )
    except Exception:
        await interaction.followup.send("🔴 Offline")

@tasks.loop(seconds=30)
async def check():
    global last
    try:
        await server.async_status()
        now = True
    except Exception:
        now = False
    if last is not None and now != last:
        channel = client.get_channel(CHANNEL_ID)
        await channel.send("🟢 **SERVIDOR ENCENDIDO**" if now else "🔴 **SERVIDOR APAGADO**")
    last = now

@client.event
async def on_ready():
    await tree.sync()
    if not check.is_running():
        check.start()

client.run(TOKEN)
