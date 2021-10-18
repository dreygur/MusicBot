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
  print("Bot Logged In...")

@client.command()
async def play(ctx, url):
  YDL_OPTIONS = {
    "format": "bestaudio",
    "noplaylist": True
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
    await ctx.send("Music is being Played!!!")
  else:
    await ctx.send("Music is already Playing...")
    return

# Stop Playing Music
@client.command()
async def stop(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)

  if voice.is_playing():
    voice.stop()
    await ctx.send("Music Stopping...")

# Pause the Music
@client.command()
async def pause(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)
  if voice.is_playing():
    voice.pause()
    await ctx.send("Music Paused...")

# Resume the Music
@client.command()
async def resume(ctx):
  voice = get(client.voice_clients, guild=ctx.guild)
  if not voice.is_playing():
    voice.resume()
    await ctx.send("Music Resumed...")

# Run the Bot
client.run(os.getenv("DISCORD_TOKEN"))
