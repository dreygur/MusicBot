#!/usr/bin/env python
import os
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from dotenv import load_dotenv
from youtube_dl import YoutubeDL

# Load Environment Variables
load_dotenv()

# Discord Client
client = commands.Bot(command_prefix=".")

# Login Event
@client.event
async def on_ready():
  print(f"Logged in as {client.user} (ID: {client.user.id})")

@client.command()
async def play(ctx, url):
  YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
  }
  FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
  }

  channel = ctx.message.author.voice.channel
  voice = get(client.voice_clients, guild=ctx.guild)

  if voice and voice.is_connected():
    await voice.move_to(channel)
  else:
    voice = await channel.connect()

  if not voice.is_playing():
    with YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download=False)
    URL = info.get('url')
    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
    voice.is_playing()
    await ctx.send(f":fire: Playing {info['title']}")
  else:
    await ctx.send(":fire: Music is already Playing...")
    return

# Stop Playing Music
@client.command()
async def stop(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)

  if voice.is_playing():
    voice.stop()
    await ctx.voice_client.disconnect()
    await ctx.send(":fire: Music Stopped...")

# Pause the Music
@client.command()
async def pause(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
    await ctx.send(":fire: Music Paused...")

# Resume the Music
@client.command()
async def resume(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)
  if not voice.is_playing():
    voice.resume()
    await ctx.send(":fire: Music Resumed...")

# Volume Controll
@client.command()
async def volume(ctx, volume: int):
  if ctx.voice_client is None:
    return await ctx.send("Not connected to a voice channel.")

  ctx.voice_client.source.volume = volume / 100
  await ctx.send(f":fire: Changed volume to {volume}%")

# Checks users connectivity
@play.before_invoke
async def ensure_voice(ctx):
  if ctx.voice_client is None:
    if ctx.author.voice:
      await ctx.author.voice.channel.connect()
    else:
      await ctx.send("You are not connected to a voice channel.")
      raise commands.CommandError("Author not connected to a voice channel.")
  elif ctx.voice_client.is_playing():
    ctx.voice_client.stop()

# Run the Bot
client.run(os.getenv("DISCORD_TOKEN"))
