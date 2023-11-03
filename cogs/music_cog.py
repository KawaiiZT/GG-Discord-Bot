import discord
from discord.ext import commands
from asyncio import run_coroutine_threadsafe
from urllib import parse, request

import interactions
import re
import yt_dlp
import threading
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
        

    #On ready status command
    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            id = int(guild.id)
            self.musicQueue[id] = []
            self.queueIndex[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False
            
    def now_playing_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.avatar.url
        
        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title}]({link})',
            color = self.embedPurple
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
            title = "Song added to queue",
            description = f'[{title}]({link})',
            color = self.embedPurple
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
    
    #join voice chat commands
    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        if id not in self.vc or not self.vc[id].is_connected():
            self.vc[id] = await channel.connect()
            if self.vc[id] == None:
                await ctx.send("Could not connect to the voice channel")
                return
        else:
            await self.vc[id].move_to(channel)

    
    #search for yt audio
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

    #extract yt link
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


    #play the song
    async def play_music(self, ctx):
        id = int(ctx.guild.id)
        # Check if the bot is already playing
        if self.is_playing.get(id, False):
            await ctx.send("I'm already playing music.")
            return
        # Check if there are songs in the queue
        if not self.musicQueue.get(id):
            await ctx.send("There are no songs in the queue.")
            return
        # Get the first song in the queue
        song = self.musicQueue[id][0][0]
        # Join the voice channel
        await self.join_VC(ctx, self.musicQueue[id][0][1])
        # Play the song
        self.vc[id].play(discord.FFmpegPCMAudio(song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        # Update state
        self.is_playing[id] = True
        # Send the now playing embed
        embed = self.now_playing_embed(ctx, song)
        await ctx.send(embed=embed)

    
    @commands.command(name="play", aliases=["Play", "P", "PLAY", "p"])
    #add asterisks on *args for reading everything after the !p commands
    async def play(self, ctx, *args):
        search = " ".join(args)
        id = int(ctx.guild.id)

        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You must be connected to a voice channel.")
            return

        search_results = await self.search_yt_async(search)
        if not search_results:
            await ctx.send("No search results found.")
            return

        # Fetch information for the first result asynchronously
        song = await self.extract_yt_async(search_results[0])

        if type(song) == type(True):
            await ctx.send("Could not download the song. Incorrect format, try some different keywords.")
        else:
            if id not in self.musicQueue:
                self.musicQueue[id] = []

            self.musicQueue[id].append([song, userChannel])

            if id not in self.is_playing:
                self.is_playing[id] = False

            if not self.is_playing[id]:
                await self.play_music(ctx)
            else:
                message = self.now_playing_embed(ctx, song)
                await ctx.send(embed=message)

    #play next song
    def play_next(self, ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            return
        if self.queueIndex[id] + 1 < len(self.musicQueue[id]):
            self.is_playing[id] = True
            self.queueIndex[id] += 1
            
            song = self.musicQueue[id][self.queueIndex[id][0]]
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
    
    @commands.command(name = "pause", aliases = ["stop", "STOP", "Pause", "PAUSE", "Stop"], help = "")
    async def pause(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no audio to be paused at the moment.")
        elif self.is_playing[id]:
            await ctx.send("Audio paused.")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()
    
    @commands.command(name = "resume", aliases = ["RESUME", "r", "Resume", "R"], help = "")
    async def resume(self, ctx):
        id = int(ctx.guild.id)
        if not self.vc[id]:
            await ctx.send("There is no audio to be played at the moment.")
        elif self.is_paused[id]:
            await ctx.send("The audio is now playing.")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()
    
    
    @commands.command(name = "join", aliases = ["j", "J", "JOIN", "Join"], help = "")
    async def join(self, ctx):
        if ctx.author.voice:
            userChannel = ctx.author.voice.channel
            await self.join_VC(ctx, userChannel)
            await ctx.send(f'I have been summoned in **{userChannel}**')
        else:
            await ctx.send("You need to be connected to a voice channel.")

    @commands.command(name = "leave", aliases = ["l", "Leave", "LEAVE", "L"], help= "")
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0
        if self.vc[id] != None:
            await ctx.send("The bot has left the channel.")
            await self.vc[id].disconnect()
    
    @commands.command(name = "add", aliases = ["Add", "ADD", "a"], help= "")
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
            song = self.extract_yt(self.search_yt(search)[0])
            if type(song) == type(False):
                await ctx.send("Could not download the song, incorrect format. Try a different keywords.")
            else:
                self.musicQueue[ctx.guild.id].append([song, userChannel])
                
            if id not in self.is_playing:
                self.is_playing[id] = False

            if not self.is_playing[id]:
                await self.play_music(ctx)
            else:
                message = self.added_song_embed(ctx, song)
                await ctx.send(embed=message)
        
async def setup(client:commands.Bot) -> None:
    await client.add_cog(Music(client))