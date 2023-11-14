import discord, pytube, yt_dlp
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
from youtubesearchpython import VideosSearch
import re


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.embedPurple = 0x9B59B6
        self.queue = []
        self.song_names = []
        self.durations = []
        self.channel_authors =[]

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot and after.channel is None and self.queue:
            interaction = self.queue.pop(0)
            await self.play_next(interaction)
    
    def now_playing_embed(self, interaction, song):
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        duration = song['duration']
        channel_author = song['channel_author']
        author = interaction.user
        avatar = author.avatar.url

        embed = discord.Embed(
            title="Songs added to the queue 🎶",
            description=f'**Music**:\n[{title}]({link})',
            color=self.embedPurple
        )
        embed.add_field(name="**Channel Author:**", value=f"`{channel_author}`")
        embed.add_field(name="**🕐 Duration:**", value=f"`{duration}`", inline=False)
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed
    
    async def play_next(self, interaction: discord.Interaction):
        if len(self.queue) == 0:
            if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_connected():
                await interaction.guild.voice_client.disconnect()
            return

        voice_channel = interaction.user.voice.channel
        voice_channel = discord.utils.get(interaction.guild.voice_channels, name=voice_channel.name)

        if interaction.guild.voice_client is None:
            vc = await voice_channel.connect()
        else:
            vc = interaction.guild.voice_client

        if vc.is_playing():
            vc.stop()

        if self.queue:
            song_url = self.queue.pop(0)
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }
            vc.play(discord.FFmpegPCMAudio(song_url, **FFMPEG_OPTIONS), after=lambda e: self.client.loop.create_task(self.play_next(interaction)))
        else:
            voice_client = discord.utils.get(interaction.guild.voice_clients, guild=interaction.guild)
            if voice_client.is_connected():
                await voice_client.disconnect()

    def format_duration(self, duration):
        minutes, seconds = divmod(duration, 60)
        return f"{int(minutes)}:{int(seconds):02}"

    @app_commands.command(name='play', description='Play a song from YouTube.')
    async def play(self, interaction: discord.Interaction, url: str):
        url_pattern = re.compile(r'^https?://(?:www\.)?(?:youtube\.com/.*(?:\?|\&)v=|youtu\.be/)([^"&?/\s]{11})$')
        if re.match(url_pattern, url):
            if interaction.user.voice and interaction.user.voice.channel:
                voice_channel = interaction.user.voice.channel
                req = discord.Embed(description="Processing your request...", color=discord.Color.green())
                await interaction.response.send_message(embed=req)
                video = YouTube(url)
                song_url = video.streams.filter(only_audio=True).first().url

                if interaction.guild.voice_client is None:
                    vc = await voice_channel.connect()
                else:
                    vc = interaction.guild.voice_client

                # Add the song to the queue
                self.queue.append(song_url)

                # If the bot is not currently playing, start playing
                if not vc.is_playing():
                    await self.play_next(interaction)

                with yt_dlp.YoutubeDL() as ydl:
                    info = ydl.extract_info(url, download=False)
                    song_name = info['title']
                    channel_author = info['uploader']
                    duration = self.format_duration(info['duration'])
                    song_info = {
                        'title': song_name,
                        'link': f"https://www.youtube.com/watch?v={info['id']}",
                        'thumbnail': info['thumbnail'],
                        'duration': duration,
                        'channel_author': channel_author
                    }
                self.song_names.append(song_name)
                self.durations.append(duration)
                self.channel_authors.append(channel_author)

                # Create the Now Playing embed
                now_playing_embed = self.now_playing_embed(interaction, song_info)
                # Send an embed message to confirm the song was added
                await interaction.edit_original_response(embed=now_playing_embed)
            else:
                await interaction.response.send_message("You must be in a voice channel to use this command.", ephemeral=True)
        else:
            error_embed = discord.Embed(
                title='Error 🚨',
                description='Please use `/ytsearch` to get the YouTube link and use `/play` command with a valid YouTube link again.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)




    @app_commands.command(name='queue', description='Display the current song queue.')
    async def show_queue(self, interaction: discord.Interaction):
        if len(self.queue) > 0:
            embed = discord.Embed(
                title='Current Song Queue',
                color=0x3498db  # You can change the color to your preference
            )

            for index, (song_name, duration, channel_author) in enumerate(zip(self.song_names, self.durations, self.channel_authors)):
                embed.add_field(
                    name=f'🎶Song {index + 1}:',
                    value=f'{song_name} - {channel_author}\n🕐**Duration:** \n{duration}',
                    inline=False
                )

            await interaction.response.send_message(embed=embed)
        else:
            emptyq = discord.Embed(description='The queue is empty', color=discord.Color.red())
            await interaction.response.send_message(embed=emptyq)

    @app_commands.command(name='skip', description='Skip the current song.')
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await self.play_next(interaction)
            skipp = discord.Embed(description="Skipped the current song", color=discord.Color.green())
            await interaction.response.send_message(embed=skipp)

    @app_commands.command(name='leave', description='Make the bot leave the voice channel.')
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect()
            self.queue = []
            await interaction.response.send_message("I've been disconnected from the voice channel.", ephemeral=True)
    
    @app_commands.command(name='pause', description='Pause the currently playing song.')
    async def pause(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_playing():
            voice_client.pause()
            songp = discord.Embed(description="Song paused.", color=discord.Color.dark_red())
            await interaction.response.send_message(embed=songp)
        else:
            nosong = discord.Embed(description="No song is currently playing.", color=discord.Color.red())
            await interaction.response.send_message(embed=nosong)


    @app_commands.command(name='resume', description='Resume the paused song.')
    async def resume(self, interaction: discord.Interaction):
        voice_client = discord.utils.get(self.client.voice_clients, guild=interaction.guild)

        if voice_client and voice_client.is_paused():
            voice_client.resume()
            songr = discord.Embed(description="Song resumed.", color=discord.Color.green())
            await interaction.response.send_message(embed=songr)
        else:
            nosongr = discord.Embed(description="No song is currently paused.", color=discord.Color.red())
            await interaction.response.send_message(embed=nosongr)
            
    
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

async def setup(client:commands.Bot) -> None:
    await client.add_cog(Music(client))