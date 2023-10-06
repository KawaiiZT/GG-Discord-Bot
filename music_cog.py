import discord
from discord.ext import commands
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
import re
import yt_dlp



class music_cog(commands.Cog):
    def __init__(self, client):
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
    
    def now_playing_embed(self, ctx, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = ctx.author
        avatar = author.avater_url
        
        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title}] ({link})',
            color = self.embedPurple
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed
    
    
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
    # Modify the search_yt function to handle direct YouTube links
    def search_yt(self, search):
        ydl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS)
        query = parse.urlencode({'search_query': search})

        try:
            result = ydl.extract_info(f"ytsearch:{query}", download=False)
        except yt_dlp.DownloadError:
            return []

        entries = result.get('entries', [])

    # Check if the search result is empty and the input is a direct link
        if not entries and 'youtube.com' in search and 'watch' in search:
                return [search]

        if not entries:
            return []

        return [entry['id'] for entry in entries]



    
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
        # The modified version of the play_music method goes here
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
        await ctx.send(f"Now playing: {song['title']}")

    @commands.command(name = "play", aliases = ["p"], help = "")
    #add asterisks on *args for reading everything after the !p commands
    async def play(self, ctx, *args):
        search = " ".join(args)
        id = int(ctx.guild.id)

        try:
            userChannel = ctx.author.voice.channel
        except:
            await ctx.send("You must be connected to a voice channel.")
            return

        # Check if search result is empty
        search_results = self.search_yt(search)
        if not search_results:
            await ctx.send("No search results found.")
            return

        song = self.extract_yt(search_results[0])

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
                message = self.added_song_embed(ctx, song)
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
    
    
    @commands.command(name = "join", aliases = ["j"], help = "")
    async def join(self, ctx):
        if ctx.author.voice:
            userChannel = ctx.author.voice.channel
            await self.join_VC(ctx, userChannel)
            await ctx.send(f'I have been summoned in **{userChannel}**')
        else:
            await ctx.send("You need to be connected to a voice channel.")

    @commands.command(name = "leave", aliases = ["l"], help= "")
    async def leave(self, ctx):
        id = int(ctx.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0
        if self.vc[id] != None:
            await ctx.send("The bot has left the channel.")
            await self.vc[id].disconnect()
