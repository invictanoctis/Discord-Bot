import youtube_dl
import discord

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'source_address': None,
}
ffmpeg_options = {
    'executable': 'D:/Programme/FFMPEG/ffmpeg-2024-10-31-git-87068b9600-full_build/bin/ffmpeg.exe',
    'options': '-vn -ac 2 -ar 48000 -b:a 192k',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class MusicPlayer:
    def __init__(self, ctx):
        self.ctx = ctx

    async def join_channel(self):
        if self.ctx.author.voice:
            channel = self.ctx.author.voice.channel
            await channel.connect()
        else:
            await self.ctx.send("You are not in a voice channel.")

    async def leave_channel(self):
        if self.ctx.voice_client:
            await self.ctx.voice_client.disconnect()
        else:
            await self.ctx.send("I'm not in a voice channel.")

    async def play_music(self, url):
        if not self.ctx.voice_client:
            await self.ctx.send("I need to be in a voice channel to play music.")
            return

        async with self.ctx.typing():
            try:
                info = ytdl.extract_info(url, download=False)
                audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
                if audio_url is None:
                    await self.ctx.send("Could not find a valid audio stream.")
                    return
                print(f"Playing URL: {audio_url}")  # Debugging output
            except Exception as e:
                await self.ctx.send(f"An error occurred while extracting info: {e}")
                return

        try:
            source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            self.ctx.voice_client.play(source)
            await self.ctx.send(f'Now playing: {info["title"]}')
        except Exception as e:
            await self.ctx.send(f"An error occurred while trying to play audio: {e}")

    async def stop_music(self):
        if self.ctx.voice_client and self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            await self.ctx.send("Stopped the playback.")
        else:
            await self.ctx.send("I'm not playing anything.")