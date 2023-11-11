import discord
from discord.ext import commands
from discord import app_commands
from asyncio import run_coroutine_threadsafe
from urllib import parse, request

import json
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
        self.YTDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}
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
            
    def now_playing_embed(self, interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = interaction.user
        avatar = author.avatar.url

        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title}]({link})',
            color = self.embedPurple
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed


    def added_song_embed(self, interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = interaction.user
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
    
    #join voice chat commands
    async def join_VC(self, ctx, channel):
        id = int(ctx.guild.id)
        if not self.vc.get(id) or (self.vc.get(id) and not self.vc[id].is_connected()):
            self.vc[id] = await channel.connect()
        else:
            await self.vc[id].move_to(channel)


    def get_YT_title(self, video_id):
        params = {
        "format": "json", 
        "url": "https://www.youtube.com/watch?v=%s" % video_id
            }
        url = "https://www.youtube.com/oembed"
        queryString = parse.urlencode(params)
        url =  url + "?" + queryString
        with request.urlopen(url) as response:
            responseText = response.read()
            data = json.loads(responseText.decode())
            return data['title']
    
    
    async def search_yt_async(self, search):
        loop = asyncio.get_event_loop()
        ydl = yt_dlp.YoutubeDL(self.YTDL_OPTIONS)

        # Fetch information for multiple search results asynchronously
        try:
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(f"ytsearch:{search}", download=False))
        except yt_dlp.DownloadError:
            return []

        entries = info.get('entries', [])
    
        if not entries:
            return []

        # Return a list of video URLs from the search results
        return [f'https://www.youtube.com/watch?v={entry["id"]}' for entry in entries]


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
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
        }
        ydl = yt_dlp.YoutubeDL(ydl_opts)
        try:
            info = ydl.extract_info(url, download=False)
        except yt_dlp.DownloadError:
            return False

        thumbnail = info['thumbnails'][0]['url'] if 'thumbnails' in info and info['thumbnails'] else 'default_thumbnail_url'
    
        return {
            'link': 'https://www.youtube.com/watch?v=' + info['id'],
            'source': info['url'],
            'title': info['title'],
            'thumbnail': thumbnail  # Set the thumbnail here
        }
        
    async def play_music(self, interaction, url):
        id = int(interaction.guild.id)

        try:
            userChannel = interaction.user.voice.channel
        except AttributeError:
            await interaction.response.send_message("You must be connected to a voice channel.", ephemeral=True)
            return

        if not self.vc.get(id):
            self.vc[id] = await userChannel.connect()

        song = self.extract_yt(url)

        if not song:
            try:
                await interaction.response.send_message("Could not download the song. Incorrect format, try different keywords.", ephemeral=True)
            except discord.errors.NotFound:
                # Handle the "Not Found" error for the interaction
                pass
        else:
            self.is_playing[id] = True
            self.vc[id].play(discord.FFmpegPCMAudio(song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(interaction, id))
            message = self.now_playing_embed(interaction, song)
            try:
                await interaction.response.send_message(embed=message)  # Send the actual response
            except discord.errors.NotFound:
                # Handle the "Not Found" error for the interaction
                pass

    async def add_song(self, interaction: discord.Interaction, query: str):
        try:
            userChannel = interaction.user.voice.channel
        except AttributeError:
            await interaction.followup.send("You must be in a voice channel", ephemeral=True)
            return

        if not query:
            await interaction.followup.send("You need to specify a song to be added", ephemeral=True)
        else:
            guild_id = interaction.guild.id
            try:
                if guild_id not in self.musicQueue:
                    self.musicQueue[guild_id] = []
                search_results = await self.search_yt_async(query)
                if not search_results:
                    await interaction.followup.send("No search results found. Please specify a valid URL or search term.", ephemeral=True)
                else:
                    song_info = await self.extract_yt_async(search_results[0])
                    if not song_info:
                        await interaction.followup.send("Could not download the song, incorrect format. Try different keywords.")
                    else:
                        self.musicQueue[guild_id].append([song_info, userChannel])
                        if guild_id not in self.is_playing:
                            self.is_playing[guild_id] = False

                        if not self.is_playing[guild_id]:
                            await self.play_next(interaction, guild_id)  # Play the first song
                        else:
                            message = self.added_song_embed(interaction, song_info)
                            try:
                                await interaction.followup.send(embed=message)
                            except discord.errors.NotFound:
                                # Handle the "Not Found" error for the interaction
                                pass
            except Exception as e:
                print(f"Error in 'add' command: {e}")
                print(f"Guild ID: {guild_id}")
                print(f"musicQueue: {self.musicQueue}")
                raise



    @app_commands.command(name="play", description="Play the song")
    async def play(self, interaction: discord.Interaction, query: str):
        # Check if the input is a valid URL
        url_pattern = r'^(https?://)?(www\.)?youtube\.com/watch\?v=|youtu\.be/|youtube\.com/playlist\?list='
        is_url = re.match(url_pattern, query)

        if is_url:
            # If it's a URL, play the song directly
            await self.play_music(interaction, query)
        else:
            # If it's not a URL, assume it's a search query and try to find a video
            search_results = await self.search_yt_async(query)
            if not search_results:
                await interaction.response.send_message("No search results found. Please specify a valid URL or search term.", ephemeral=True)
            else:
            # Play the first search result
                await self.play_music(interaction, search_results[0])

    def play_next(self, interaction, guild_id):
        if not self.is_playing[guild_id]:
            return

        self.queueIndex[guild_id] += 1

        if self.queueIndex[guild_id] < len(self.musicQueue[guild_id]):
            song = self.musicQueue[guild_id][self.queueIndex[guild_id]]
            message = "Message"
            coroutine = interaction.send(message)
            fut = run_coroutine_threadsafe(coroutine, self.client.loop)
            try:
                fut.result()
            except:
                pass

            self.vc[guild_id].play(
                discord.FFmpegPCMAudio(song[0]['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(interaction, guild_id)
            )
        else:
            self.is_playing[guild_id] = False

    
    @app_commands.command(name = "pause", description= "Pause the current song.")
    async def pause(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if not self.vc[id]:
            await interaction.response.send_message("There is no audio to be paused at the moment.")
        elif self.is_playing[id]:
            await interaction.response.send_message("Audio paused.")
            self.is_playing[id] = False
            self.is_paused[id] = True
            self.vc[id].pause()
    
    @app_commands.command(name = "resume", description="Resume the current song.")
    async def resume(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        if not self.vc[id]:
            await interaction.response.send_message("There is no audio to be played at the moment.")
        elif self.is_paused[id]:
            await interaction.response.send_message("The audio is now playing.")
            self.is_playing[id] = True
            self.is_paused[id] = False
            self.vc[id].resume()
    
    @app_commands.command(name="join", description="Bot joins the voice chat")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice:
            userChannel = interaction.user.voice.channel
            await self.join_VC(interaction, userChannel)
            await interaction.response.send_message(f'I have been summoned in **{userChannel}**')
        else:
            await interaction.response.send_message("You need to be connected to a voice channel.")

    @app_commands.command(name = "leave", description="Bot leave the voice chat")
    async def leave(self, interaction: discord.Interaction):
        id = int(interaction.guild.id)
        self.is_playing[id] = self.is_paused[id] = False
        self.musicQueue[id] = []
        self.queueIndex[id] = 0
        if self.vc[id] != None:
            await interaction.response.send_message("The bot has left the channel.")
            await self.vc[id].disconnect()
    
    @app_commands.command(name="add", description="Add the song to the queue.")
    async def add(self, interaction: discord.Interaction, query: str):
        try:
            userChannel = interaction.user.voice.channel
        except AttributeError:
            await interaction.response.send_message("You must be in a voice channel", ephemeral=True)
            return

        if not query:
            await interaction.response.send_message("You need to specify a song to be added", ephemeral=True)
        else:
            guild_id = interaction.guild.id
            try:
                if guild_id not in self.musicQueue:
                    self.musicQueue[guild_id] = []
                search_results = await self.search_yt_async(query)
                if not search_results:
                    await interaction.response.send_message("No search results found. Please specify a valid URL or search term.", ephemeral=True)
                else:
                    song_info = await self.extract_yt_async(search_results[0])
                    if not song_info:
                        await interaction.response.send_message("Could not download the song, incorrect format. Try different keywords.")
                    else:
                        self.musicQueue[guild_id].append([song_info, userChannel])
                        if guild_id not in self.is_playing:
                            self.is_playing[guild_id] = False

                        if not self.is_playing[guild_id]:
                            await self.play_next(interaction, guild_id)  # Play the first song
                        else:
                            message = self.added_song_embed(interaction, song_info)
                            await interaction.response.send_message(embed=message)
            except Exception as e:
                print(f"Error in 'add' command: {e}")
                print(f"Guild ID: {guild_id}")
                print(f"musicQueue: {self.musicQueue}")
                raise
        
    @app_commands.command(name="search", description= "Search the first 10 result song from query.")
    async def search(self, interaction: discord.Interaction, query: str):
        search = " ".join(query)
        songNames = []
        selectionOptions = []   
        embedText = ""
            
        if not query:
            await interaction.response.send_message("You must specify search terms to use this command.")
        try:
            userChannel = interaction.autuor.voice.channel
        except:
            await interaction.response.send_message("You must be connected to a voice channel")
            return
            
        await interaction.response.send_message("Fetching search results . . .")
        songTokens = self.search_yt_async(search)
        
        for i, token in enumerate(songTokens):
            url = 'https://www.youtube.com/watch?v=' + token
            name = self.get_YT_title(token)
            songNames.append(name)
            embedText += f"{i+1} - [{name}]()"
            

async def setup(client:commands.Bot) -> None:
    await client.add_cog(Music(client))
