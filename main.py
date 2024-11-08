import discord
import yt_dlp as youtube_dl
from discord.ext import commands
from tictactoe_assets import Tictactoe
from numberguessing_assets import GuessingGame
import pyttsx3
import aiohttp

# General Setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
intents.voice_states = True

@bot.command()
async def ping(ctx):
    ping_embed = discord.Embed(title="Ping", description="Latency in ms", color=discord.Color.blurple())
    ping_embed.add_field(name=f"{bot.user.name}'s Latency (ms): ", value=f"{round(bot.latency * 1000)}ms.", inline=False)
    ping_embed.set_footer(text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.avatar)
    await ctx.send(embed=ping_embed)

@bot.command(name="commands")
async def command_list(ctx):
    ping_embed = discord.Embed(title="Commands", color=discord.Color.blurple())
    ping_embed.add_field(name="Utility", value='''
                        !ping ➝ Display latency of Bot''', inline=False)
    ping_embed.add_field(name="Game: Tic Tac Toe", value='''
                        !start_ttt @player1 @player2 ➝ Start a game of Tic Tac Toe with a friend
                        !move_ttt position ➝ Place symbol at the wanted position
                        !reset_ttt ➝ Reset the game''', inline=False)
    ping_embed.add_field(name="Game: Guess the Number", value='''
                        !start_gg highest_number ➝ Start a Number guessing game 
                         ''', inline=False)
    ping_embed.add_field(name="Music", value='''
                        !join ➝ Joins the channel
                        !leave ➝ Leaves the channel
                        !play yt_url ➝ Plays the Youtube link as a audiofile
                        !stop ➝ Stops playing''', inline=False)
    ping_embed.add_field(name="TTS", value='''
                        !set_voice 0/1/2 ➝ Changes the voices
                        !speak message ➝ Joins channel and speaks the specified message''', inline=False)
    ping_embed.set_footer(text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.avatar)
    await ctx.send(embed=ping_embed)

games = {} # Belongs to the ttt game

@bot.command(name="start_ttt")
async def start_game_ttt(ctx, player1: discord.User, player2: discord.User):
    if ctx.channel.id in games:
        await ctx.send("A game is already in progress in this channel.")
        return
    games[ctx.channel.id] = Tictactoe(player1.id, player2.id)
    await ctx.send(f"Game started between {player1.mention} (X) and {player2.mention} (O)!\n" + games[ctx.channel.id].draw_board())

@bot.command(name="move_ttt")
async def make_move_ttt(ctx, position: int):
    game = games.get(ctx.channel.id)
    if not game:
        await ctx.send("No game is currently active. Start a new game with '!start_ttt @player1 @player2'.")
        return

    # Check if it's the current player's turn
    if ctx.author.id != game.current_turn:
        await ctx.send("It's not your turn!")
        return

    current_symbol = "X" if ctx.author.id == game.cr else "O"

    if game.make_move(position - 1, current_symbol):
        await ctx.send(game.draw_board())
        
        if game.check_win(current_symbol):
            await ctx.send(f"Congratulations {ctx.author.mention}, you won!")
            game.reset_game()  # Reset the game state
            del games[ctx.channel.id]
            return
        
        # Check for draw: if the board is full and no one has won
        if all(space != "▢" for space in game.board_list):
            await ctx.send("It's a draw! No more moves left.")
            game.reset_game()  # Reset the game state
            del games[ctx.channel.id]
            return
        
        # Switch turns
        game.current_turn = game.ci if current_symbol == "X" else game.cr  
    else:
        await ctx.send("Invalid move! That position is already taken.")

@bot.command(name="reset_ttt")
async def reset_game_ttt(ctx):
    game = games.get(ctx.channel.id)
    if game:
        game.reset_game()
        await ctx.send("The game has been reset!")
        del games[ctx.channel.id]
    else:
        await ctx.send("No game is currently active. Start a new game with '!start_ttt @player1 @player2'.")

@bot.command(name="start_gg")
async def guessing_game_command(ctx, end_interval: int):
    game = GuessingGame(ctx, end_interval)
    await game.start_game()

# Setup for the music feature
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

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You are not in a voice channel.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.send("I need to be in a voice channel to play music.")
        return

    async with ctx.typing():
        try:
            info = ytdl.extract_info(url, download=False)
            # Look for an audio stream that is not 'none'
            audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none'), None)
            if audio_url is None:
                await ctx.send("Could not find a valid audio stream.")
                return
            print(f"Playing URL: {audio_url}")  # Debugging output
        except Exception as e:
            await ctx.send(f"An error occurred while extracting info: {e}")
            return

    try:
        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
        ctx.voice_client.play(source)
        await ctx.send(f'Now playing: {info["title"]}')
    except Exception as e:
        await ctx.send(f"An error occurred while trying to play audio: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Stopped the playback.")
    else:
        await ctx.send("I'm not playing anything.")

user_voices = {} # Belongs to the tts

@bot.command(name="set_voice")
async def set_voice(ctx, voice_index: int):
    """Set your preferred voice by index."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Check if the provided index is valid
    if 0 <= voice_index < len(voices):
        user_voices[ctx.author.id] = voice_index
        await ctx.send(f"Your voice has been set to: {voices[voice_index].name}")
    else:
        await ctx.send(f"Invalid voice index. Please choose a number between 0 and {len(voices) - 1}.")

@bot.command(name="speak")
async def speak(ctx, *, message: str):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()

        engine = pyttsx3.init()
        voices = engine.getProperty('voices')

        voice_index = user_voices.get(ctx.author.id, 0)  # Default to the first voice if not set
        engine.setProperty('voice', voices[voice_index].id)

        engine.save_to_file(message, 'D:/Data/Programming/Python/discord_bot/tts_assets.mp3')
        engine.runAndWait()
        
        ctx.voice_client.play(discord.FFmpegPCMAudio('D:/Data/Programming/Python/discord_bot/tts_assets.mp3'))
        await ctx.send(f'Now speaking: "{message}"')
    else:
        await ctx.send("You need to be in a voice channel to use this command.")

with open("D:/Data/Programming/Python/discord_bot/giphy_token.txt") as file_g:
    giphy_token = file_g.read()

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user) # 1 use every 30 seconds per user
async def random_gif(ctx):
    # Giphy API endpoint for random GIFs
    url = f'https://api.giphy.com/v1/gifs/random?api_key={giphy_token}&tag=&rating=g'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            gif_url = data['data']['images']['original']['url']
            
            await ctx.send(gif_url)

@random_gif.error
async def random_gif_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Please try again in {int(error.retry_after)} seconds.")
    else:
        # Handle other errors if needed
        await ctx.send("An error occurred.")

@bot.command()
@commands.has_permissions(manage_nicknames=True) # Ensure the user has permission
async def changenick(ctx, member: discord.Member, *, nickname: str):
    try:
        await member.edit(nick=nickname)
        await ctx.send(f'Nickname for {member.mention} has been changed to `{nickname}`.')
    except discord.Forbidden:
        await ctx.send("I don't have permission to change that user's nickname.")
    except discord.HTTPException:
        await ctx.send("There was an error changing the nickname.")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    main_channel = bot.get_channel(807025341431676952)
    welcome_text = discord.Embed(title="Hey, I'm now ready to be used!", description="Type !commands to see what I have to offer!", color=discord.Color.blurple())
    await main_channel.send(embed=welcome_text)

with open("D:/Data/Programming/Python/discord_bot/discord_token.txt") as file_d:
    discord_token = file_d.read()

bot.run(discord_token)