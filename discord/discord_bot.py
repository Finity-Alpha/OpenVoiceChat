import discord
import os
from dotenv import load_dotenv
import threading

# from openvoicechat.stt.stt_hf import Ear_hf
import numpy as np
import librosa
import sounddevice as sd
import time


load_dotenv()

# ear = Ear_hf(device="cuda")

bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.command(
    description="Sends the bot's latency."
)  # this decorator makes a slash command
async def ping(
    ctx: discord.ApplicationContext,
):  # a slash command will be created with the name "ping"
    await ctx.respond(f"Pong! Latency is {bot.latency}")


connections = {}


sink = discord.sinks.WaveSink()


async def record_callback(
    this: discord.sinks, channel: discord.TextChannel = None, *args
):
    audio_files = list(this.audio_data.values())
    if len(audio_files) > 0:
        audio_files[0].file.seek(0)
        file = audio_files[0].file.read()
        audio_arr = np.frombuffer(file, dtype=np.int32)
        sd.play(audio_arr, 48_000, blocking=True)


@bot.command()
async def join_voice_channel(ctx: discord.ApplicationContext):
    voice = ctx.author.voice

    await ctx.response.defer()

    if not voice:
        await ctx.followup.send("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    print("connected")

    vc.start_recording(
        sink=sink,
        callback=record_callback,
    )
    print(vc.decoder.SAMPLING_RATE)
    print("started recording")
    await ctx.followup.send(f"Connected to channel {voice.channel.name}")

    connections.update(
        {ctx.guild.id: [vc, voice.channel.name]}
    )  # Updating the cache with the guild and channel.
    # start print transcription thread
    print("starting loop")
    while True:
        audio_files = list(sink.audio_data.values())
        if len(audio_files) > 0:
            audio_files[0].file.seek(0)
            # print(len(audio_files[0].file.read()))
            file = audio_files[0].file.read()
            audio_arr = np.frombuffer(file, dtype=np.int32)
            if librosa.get_duration(y=audio_arr, sr=48_000) > 5:
                break
            # save audio to buffer
        else:
            pass

    print("loop ended")
    # save audio to file

    try:
        vc.stop_recording()  # Stop recording if doing so
    except discord.sinks.errors.RecordingException:
        pass
    await ctx.delete()  # And delete.
    await vc.disconnect()
    await ctx.followup.send(f"Left channel {voice.channel.name}")


@bot.command()
async def leave_voice_channel(ctx: discord.ApplicationContext):
    await ctx.response.defer()
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc: discord.VoiceClient = connections[ctx.guild.id][0]
        vc_name = connections[ctx.guild.id][1]
        try:
            vc.stop_recording()  # Stop recording if doing so
        except discord.sinks.errors.RecordingException:
            pass
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        await ctx.delete()  # And delete.
        await vc.disconnect()
        await ctx.followup.send(f"Left channel {vc_name}")
    else:
        await ctx.followup.send("Not in any voice channel!")


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_KEY"))  # run the bot with the token
