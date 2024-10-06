## NOTE: Not a sink or unpack audio issue. Seems like a not ready problem inside recv_audio in pycord.


import discord
import os
from dotenv import load_dotenv
import threading
from openvoicechat.stt.stt_hf import Ear_hf
import numpy as np
import librosa


load_dotenv()

ear = Ear_hf(device="cuda")

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


def unpack_audio(self, data):
    """Takes an audio packet received from Discord and decodes it into pcm audio data.
    If there are no users talking in the channel, `None` will be returned.

    You must be connected to receive audio.

    .. versionadded:: 2.0

    Parameters
    ----------
    data: :class:`bytes`
        Bytes received by Discord via the UDP connection used for sending and receiving voice data.
    """
    if 200 <= data[1] <= 204:
        # RTCP received.
        # RTCP provides information about the connection
        # as opposed to actual audio data, so it's not
        # important at the moment.
        return
    if self.paused:
        return

    data = discord.sinks.RawData(data, self)

    self.decoder.decode(data)


async def record_callback(
    this: discord.sinks, channel: discord.TextChannel = None, *args
):
    print("Echo ended.")


def print_transcription(sink: discord.sinks.WaveSink):
    print("running print")
    while True:
        audio_files = sink.audio_data.values()
        for file in audio_files:
            file = file.read()
            print(len(file), type(file))
            audio_arr = np.frombuffer(b"".join(file), dtype=np.int16)
            audio_arr = audio_arr / (1 << 15)
            audio_arr = audio_arr.astype(np.float32)
            audio_arr = librosa.resample(audio_arr, orig_sr=48_000, target_sr=16_000)
            text = ear.transcribe(audio_arr)
            print(text)


@bot.command()
async def join_voice_channel(ctx: discord.ApplicationContext):
    voice = ctx.author.voice

    await ctx.response.defer()

    if not voice:
        await ctx.followup.send("You aren't in a voice channel!")

    vc = await voice.channel.connect()  # Connect to the voice channel the author is in.
    vc.unpack_audio = unpack_audio.__get__(vc)
    print("connected")

    vc.start_recording(
        sink=sink,
        callback=record_callback,
    )
    print("started recording")
    await ctx.followup.send(f"Connected to channel {voice.channel.name}")

    connections.update(
        {ctx.guild.id: [vc, voice.channel.name]}
    )  # Updating the cache with the guild and channel.
    # start print transcription thread
    print("starting loop")
    while True:
        try:
            audio_files = list(sink.audio_data.values())
            if len(audio_files) > 0:
                audio_files[0].file.seek(0)
                # print(len(audio_files[0].file.read()))
            else:
                print("no files")
        except KeyboardInterrupt:
            break

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
