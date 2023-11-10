import discord
from discord.ext import commands
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
from discord import app_commands

import yt_dlp
import asyncio


class Music(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}
        self.YTDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.embedPurple = 0x9B59B6
        self.vc = {}

    # On ready status command
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            id = int(guild.id)
            self.musicQueue[id] = []
            self.queueIndex[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False

    def now_playing_embed(self, interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = interaction.user
        avatar = author.avatar.url

        embed = discord.Embed(
            title="Now Playing",
            description=f'[{title}]({link})',
            color=self.embedPurple
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed

    def added_song_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.avatar.url

        embed = discord.Embed(
            title="Song added to queue",
            description=f'[{title}]({link})',
            color=self.embedPurple
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        if member.id != self.client.user.id and before.channel != None and after.channel != before.channel:
            remainingChannelMembers = before.channel.members
            if len(remainingChannelMembers) == 1 and remainingChannelMembers[0].id == self.client.user.id and self.vc[id].is_connected():
                self.is_playing[id] = self.is_paused[id] = False
                self.musicQueue[id] = []
                self.queueIndex[id] = 0
                await self.vc[id].disconnect()

    # join voice chat commands
    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        if id not in self.vc or not (self.vc[id] and self.vc[id].is_connected()):
            self.vc[id] = await channel.connect()
            if self.vc[id] is None or not self.vc[id].is_connected():
                await ctx.send("Could not connect to the voice channel")
                return
        else:
            await self.vc[id].move_to(channel)


    # search for yt audio
    async def search_yt_async(self, search):
        loop = asyncio.get_event_loop()
        ydl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS)

        # Fetch information for multiple search results asynchronously
        try:
            result = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{search}", download=False))
        except yt_dlp.DownloadError:
            return []

        entries = result.get('entries', [])

        if not entries and 'youtube.com' in search and 'watch' in search:
            return [search]

        return [entry['id'] for entry in entries]

    async def extract_yt_async(self, url):
        loop = asyncio.get_event_loop()
        ydl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS)

        # Fetch information for a single URL asynchronously
        try:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
        except yt_dlp.DownloadError:
            return False

        return {
            'link': 'https://www.youtube.com/watch?v=' + info['id'],
            'thumbnail': info['thumbnails'][0]['url'],  # Assuming there is at least one thumbnail
            'source': info['url'],
            'title': info['title']
        }

    # extract yt link
    def extract_yt(self, url):
        ydl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS)
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError:
            return False

        return {
            'link': 'https://www.youtube.com/watch?v=' + info['id'],
            'thumbnail': info['thumbnails'][0]['url'],  # Assuming there is at least one thumbnail
            'source': info['url'],
            'title': info['title']
        }

    async def play_music(self, interaction):
        id = int(interaction.guild.id)

        # Check if the bot is already playing
        if self.is_playing.get(id, False):
            await interaction.followup.send("I'm already playing music.")
            return

        # Check if there are songs in the queue
        if not self.musicQueue.get(id):
            await interaction.followup.send("There are no songs in the queue.")
            return

        # Join the voice channel
        await self.join_VC(interaction, self.musicQueue[id][0][1])

        # Wait for the bot to connect before playing the song
        while not self.vc[id].is_connected():
            await asyncio.sleep(1)

        # Get the first song in the queue
        song = self.musicQueue[id][0][0]

        # Play the song directly from the source URL
        self.vc[id].play(discord.FFmpegPCMAudio(song['source'], **self.FFMPEG_OPTIONS), after=self.play_next)

        # Update state
        self.is_playing[id] = True

        # Send the now playing embed
        embed = self.now_playing_embed(interaction, song)
        try:
            await interaction.followup.send(embed=embed)
        except discord.errors.NotFound:
            print("Webhook not found. Please check the webhook's existence.")




    @app_commands.command(name="play", description="Play a song, video, or audio.")
    async def play(self, interaction: discord.Interaction, query: str):
        search = " ".join(query)
        id = int(interaction.guild.id)

        try:
            userChannel = interaction.user.voice.channel
        except AttributeError:
            await interaction.response.send_message("You must be connected to a voice channel.")
            return

        search_results = await self.search_yt_async(search)
        if not search_results:
            await interaction.response.send_message("No search results found.")
            return

        song = await self.extract_yt_async(search_results[0])

        if type(song) == type(True):
            await interaction.response.send_message("Could not download the song. Incorrect format, try some different keywords.")
        else:
            if id not in self.musicQueue:
                self.musicQueue[id] = []

            self.musicQueue[id].append([song, userChannel])

            if id not in self.is_playing:
                self.is_playing[id] = False

            if not self.is_playing[id]:
                await self.play_music(interaction)
            else:
                message = self.now_playing_embed(interaction, song)
                await interaction.send(embed=message)

    # play next song
    def play_next(self, ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            return
        if self.queueIndex[id] + 1 < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.queueIndex[id] += 1

            song = self.musicQueue[id][self.queueIndex[id]]  # Removed [0] here
            message = "Message"
            coroutine = ctx.send(message)
            fut = run_coroutine_threadsafe(coroutine, self.client.loop)
            try:
                fut.result()
            except:
                pass

            self.vc[id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            self.queueIndex[id] += 1
            self.is_playing[id] = False

    @commands.command(name="pause", aliases=["stop", "STOP", "Pause", "PAUSE", "Stop"], help="")
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no audio to be paused at the moment.")
        elif self.is_playing[id]:
            await ctx.send("Audio paused.")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()

    @commands.command(name="resume", aliases=["RESUME", "r", "Resume", "R"], help="")
    async def resume(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no audio to be played at the moment.")
        elif self.is_paused[id]:
            await ctx.send("The audio is now playing.")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()

    @app_commands.command(name="join", description="Bot joins a voice channel.")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            userChannel = interaction.user.voice.channel  # Change here
            await self.join_VC(interaction, userChannel)
            await interaction.response.send_message(f'I have been summoned in **{userChannel}**')
        else:
            await interaction.response.send_message("You need to be connected to a voice channel.")

    @commands.command(name="leave", aliases=["l", "Leave", "LEAVE", "L"], help="")
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0
        if self.vc[id] != None:
            await ctx.send("The bot has left the channel.")
            await self.vc[id].disconnect()

    @commands.command(name="add", aliases=["Add", "ADD", "a"], help="")
    async def add(self, ctx, *args):
        search = " ".join(args)
        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You must be in a voice channel")
            return
        if not args:
            await ctx.send("You need to specify a song to be added")
        else:
            search_results = await self.search_yt_async(search)
            if not search_results:
                await ctx.send("No search results found.")
                return

            song = await self.extract_yt_async(search_results[0])

            if type(song) == type(False):
                await ctx.send("Could not download the song, incorrect format. Try different keywords.")
            else:
                self.musicQueue[ctx.guild.id].append([song, userChannel])

            if ctx.guild.id not in self.is_playing:
                self.is_playing[ctx.guild.id] = False

            if not self.is_playing[ctx.guild.id]:
                await self.play_music(ctx)
            else:
                message = self.added_song_embed(ctx, song)
                await ctx.send(embed=message)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Music(client))
