import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import pyttsx3
import aiohttp
from discord_bot.bot_commands import start_game_ttt, make_move_ttt, reset_game_ttt
from bot_commands import guessing_game_command
from musicplayer_assets import MusicPlayer

# Block containing general setup

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
intents.voice_states = True

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    main_channel = bot.get_channel(807025341431676952)
    welcome_text = discord.Embed(title="Hey, I'm now ready to be used!", description="Type !commands to see what I have to offer!", color=discord.Color.blurple())
    await main_channel.send(embed=welcome_text)

# Block containing general commands

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

@bot.command()
async def ping(ctx):
    ping_embed = discord.Embed(title="Ping", description="Latency in ms", color=discord.Color.blurple())
    ping_embed.add_field(name=f"{bot.user.name}'s Latency (ms): ", value=f"{round(bot.latency * 1000)}ms.", inline=False)
    ping_embed.set_footer(text=f"Requested by {ctx.author.name}.", icon_url=ctx.author.avatar)
    await ctx.send(embed=ping_embed)

@bot.command()
@commands.has_permissions(manage_nicknames=True)
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


# Block containing game commands

@bot.command(name="start_ttt")
async def start_game(ctx, player1: discord.User, player2: discord.User):
    await start_game_ttt(ctx, player1, player2)

@bot.command(name="move_ttt")
async def make_move(ctx, position: int):
    await make_move_ttt(ctx, position)

@bot.command(name="reset_ttt")
async def reset_game(ctx):
    await reset_game_ttt(ctx)

@bot.command(name="start_gg")
async def start_game(ctx, end_interval: int):
    await guessing_game_command(ctx, end_interval)

# Block containing music player commands

@bot.command(name="join")
async def join(ctx):
    music_player = MusicPlayer(ctx)
    await music_player.join_channel()

@bot.command(name="leave")
async def leave(ctx):
    music_player = MusicPlayer(ctx)
    await music_player.leave_channel()

@bot.command(name="play")
async def play(ctx, url):
    music_player = MusicPlayer(ctx)
    await music_player.play_music(url)

@bot.command(name="stop")
async def stop(ctx):
    music_player = MusicPlayer(ctx)
    await music_player.stop_music()

# Block containing tts commands

user_voices = {}

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

# Block containing giphy commands

@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user) 
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

# Block containing token handling

with open("D:/Data/Programming/Python/discord_bot/giphy_token.txt") as file_g:
    giphy_token = file_g.read()

with open("D:/Data/Programming/Python/discord_bot/discord_token.txt") as file_d:
    discord_token = file_d.read()

bot.run(discord_token)