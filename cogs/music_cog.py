import discord, pytube, asyncio, yt_dlp
from discord import app_commands
from discord.ext import commands
from pytube import YouTube
from youtubesearchpython import VideosSearch


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.embedPurple = 0x9B59B6
        self.queue = []

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
        embed.add_field(name="Channel Author:", value=f"`{channel_author}`")
        embed.add_field(name="🕐 Duration:", value=f"`{duration}`", inline=False)
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
        voice_channel = interaction.user.voice.channel

        if voice_channel:
            await interaction.response.send_message("Processing your request...")
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
            
            with yt_dlp.YoutubeDL() as ydl:  # Use yt_dlp instead of youtube_dl
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
            # Send an embed message to confirm the song was added
            await interaction.edit_original_response(embed=now_playing_embed)
        else:
            await interaction.response.send_message("You must be in a voice channel to use this command.")


    @app_commands.command(name='queue', description='Display the current song queue.')
    async def show_queue(self, interaction: discord.Interaction):
        if len(self.queue) > 0:
            queue_str = '\n'.join([f'{index + 1}. {song}' for index, song in enumerate(self.queue)])
            await interaction.response.send_message(f'**Current Queue:**\n{queue_str}')
        else:
            await interaction.response.send_message('The queue is empty.')

    @app_commands.command(name='skip', description='Skip the current song.')
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is not None and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await self.play_next(interaction)
            await interaction.response.send_message("Skipped the current song")

    @app_commands.command(name='leave', description='Make the bot leave the voice channel.')
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect()
            self.queue = []
            await interaction.response.send_message("I've been disconnected from the voice channel.", ephemeral=True)
    
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