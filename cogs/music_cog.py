import discord
from discord.ext import commands, tasks
from discord import app_commands, VoiceClient
import youtube_dl
import asyncio
from youtubesearchpython import VideosSearch

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.embedPurple = 0x9B59B6
        self.is_playing = False


    @app_commands.command(name="join", description="Bot joins the voice chat")
    async def join(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel

        await channel.connect()
        await interaction.response.send_message(f"I've been connected to {channel} channel!", ephemeral=True)


    @app_commands.command(name="leave", description="Bot leaves the voice chat.")
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            await voice_client.disconnect()


    @app_commands.command(name="play", description="Play a song from youtube.")
    async def play(self, interaction: discord.Interaction, url: str):
        # Check if the provided input is not a valid YouTube URL
        if not self.is_youtube_url(url):
            await interaction.response.send_message("Please provide a valid YouTube URL or use `/ytsearch` to retrieve the link and use the `/play` command again :(",
                                                    ephemeral=True)
            return

        if not self.is_playing:
            await interaction.response.send_message("Now playing your song.")
            await self.start_playing(interaction, url)

            # Get information about the song for the Now Playing embed
            with youtube_dl.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
                info = ydl.extract_info(url, download=False)
                song_info = {
                    'title': info['title'],
                    'link': f"https://www.youtube.com/watch?v={info['id']}",
                    'thumbnail': info['thumbnail'],
                    'duration': self.format_duration(info['duration']),
                    'channel_author': info['uploader']
                }

            # Create the Now Playing embed
            now_playing_embed = self.now_playing_embed(interaction, song_info)

            # Edit the original message with the new embed
            await interaction.edit_original_response(embed=now_playing_embed)
        
        elif self.is_playing:
            await interaction.response.send_message("Song has been added to the queue.")
            await self.start_playing(interaction, url)

            with youtube_dl.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
                info = ydl.extract_info(url, download=False)
                song_info = {
                    'title': info['title'],
                    'link': f"https://www.youtube.com/watch?v={info['id']}",
                    'thumbnail': info['thumbnail'],
                    'duration': self.format_duration(info['duration']),
                    'channel_author': info['uploader']
                }
                
            added_to_queue = self.added_to_queue_embed(interaction, song_info)
            
            await interaction.edit_original_response(embed=added_to_queue)

    # Helper method to check if the provided URL is a YouTube video URL
    def is_youtube_url(self, url):
        return "youtube.com" in url or "youtu.be" in url
            

    def format_duration(self, duration):
        minutes, seconds = divmod(duration, 60)
        return f"{int(minutes)}:{int(seconds):02}"


    def now_playing_embed(self, interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        duration = song['duration']
        channel_author = song['channel_author']
        author = interaction.user
        avatar = author.avatar.url

        embed = discord.Embed(
            title="Now Playing 🎶",
            description=f'**Music**:\n[{title}]({link})',
            color=self.embedPurple
        )
        embed.add_field(name=f"Channel Author:\n{channel_author}", value="")
        embed.add_field(name="Duration", value=duration, inline=False)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed
    
    
    def added_to_queue_embed(self, interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        duration = song['duration']
        channel_author = song['channel_author']
        author = interaction.user
        avatar = author.avatar.url

        embed = discord.Embed(
            title="Song has been added to queue 🎶",
            description=f'**Music**:\n[{title}]({link})',
            color=self.embedPurple
        )
        
        embed.add_field(name=f"Channel Author:\n{channel_author}", value="")
        embed.add_field(name="Duration", value=duration, inline=False)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed
        

    async def start_playing(self, interaction: discord.Interaction, url: str):
        voice_channel = interaction.user.voice.channel

        if not voice_channel:
            return await interaction.send("You are not connected to a voice channel.")

        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            return await interaction.send("The bot is already connected to a different voice channel.")

        self.queue.append(url)

        if not self.is_playing:
            await self.play_next_song(interaction)


    async def play_next_song(self, interaction: discord.Interaction):
        if not self.queue:
            self.is_playing = False
            return

        url = self.queue.pop(0)
        await self.play_song(interaction, url)


    async def play_song(self, interaction: discord.Interaction, url: str):
        try:
            self.is_playing = True
            YDL_OPTIONS = {'format': 'bestaudio/best'}
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                              'options': '-vn'}
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                url2 = info['formats'][0]['url']
                voice_client = interaction.guild.voice_client
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS), after=lambda e: self.after_playing(interaction))
            
        except Exception as e:
            await interaction.send(f"Error: {str(e)}")


    def after_playing(self, interaction):
        coro = self.play_next_song(interaction)
        fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)
        try:
            fut.result()
        except:
            pass


    @app_commands.command(name="pause", description="Pause the current song.")
    async def pause(self, interaction: discord.Interaction):
        print("Pause command received.")
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
        else:
            print("No song is currently playing.")


    @app_commands.command(name="resume", description="Resume the current song.")
    async def resume(self, interaction: discord.Interaction):
        print("Resume command received.")
        voice_client = interaction.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
        else:
            print("The song is not paused.")


    @app_commands.command(name="queue", description="Display the current song queue.")
    async def queue_command(self, interaction: discord.Interaction):
        if not self.queue:
            noqueue = discord.Embed(title="", description="There is no song in the queue", color=discord.Color.blue())
            return await interaction.response.send_message(embed=noqueue)

        queue_embed = discord.Embed(title="Song Queue", color=discord.Color.blue())

        for i, url in enumerate(self.queue, start=1):
            # Get information about the song for the queue embed
            with youtube_dl.YoutubeDL({'format': 'bestaudio/best'}) as ydl:
                info = ydl.extract_info(url, download=False)
                song_info = {
                    'title': info['title'],
                    'channel': info['uploader'],
                    'link': f"https://www.youtube.com/watch?v={info['id']}",
                    'duration': self.format_duration(info['duration']),
                }

            # Add the song name with a clickable link and duration to the embed
            queue_embed.add_field(
                name=f"Song {i}:",
                value=f"[**{song_info['title']}**]({song_info['link']})\nChannel: {song_info['channel']}\nDuration: {song_info['duration']}",
                inline=False
            )
        
        await interaction.response.send_message(embed=queue_embed)

    
    @app_commands.command(name='ytsearch', description='Search for YouTube link for the music bot')
    async def youtube_search_command(self, interaction: discord.Interaction, query: str):
        query = ''.join(query)

        videos_search = VideosSearch(query, limit=3)  # Set the limit to 3 for the first 3 results
        results = videos_search.result()

        if results:
            embeds = []  # Create a list to hold all the embeds
            for index, video in enumerate(results['result'], start=1):
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                title = video['title']
                channel = video['channel']['name']
                thumbnail_url = video['thumbnails'][0]['url']  # Assuming there is at least one thumbnail

                # Create a new embed for each result
                embed = discord.Embed(color=discord.Color.blue())
                embed.set_thumbnail(url=thumbnail_url)  # Set the thumbnail for each result

                # Set the title for the first embed only
                if index == 1:
                    embed.title = f"YouTube Search Results for: {query}"

                # Add the result as a field in the embed
                embed.add_field(name=f"Result {index}: {title}", value=f"Channel: {channel}\n[Watch on YouTube]({video_url})", inline=False)

                embeds.append(embed)  # Add the embed to the list

            await interaction.response.send_message(embeds=embeds)  # Send all the embeds at once
        else:
            await interaction.response.send_message("No results found.")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Music(client))