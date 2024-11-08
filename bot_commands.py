import discord
from tictactoe_assets import Tictactoe
from numberguessing_assets import GuessingGame

games = {}  # Dictionary to store games by channel id

async def start_game_ttt(ctx, player1: discord.User, player2: discord.User):
    if ctx.channel.id in games:
        await ctx.send("A game is already in progress in this channel.")
        return
    games[ctx.channel.id] = Tictactoe(player1.id, player2.id)
    await ctx.send(f"Game started between {player1.mention} (X) and {player2.mention} (O)!\n" + games[ctx.channel.id].draw_board())

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
        
        # Check for draw
        if all(space != "▢" for space in game.board_list):
            await ctx.send("It's a draw! No more moves left.")
            game.reset_game()  # Reset the game state
            del games[ctx.channel.id]
            return
        
        # Switch turns
        game.current_turn = game.ci if current_symbol == "X" else game.cr  
    else:
        await ctx.send("Invalid move! That position is already taken.")

async def reset_game_ttt(ctx):
    game = games.get(ctx.channel.id)
    if game:
        game.reset_game()
        await ctx.send("The game has been reset!")
        del games[ctx.channel.id]
    else:
        await ctx.send("No game is currently active. Start a new game with '!start_ttt @player1 @player2'.")

async def guessing_game_command(ctx, end_interval: int):
    game = GuessingGame(ctx, end_interval)
    await game.start_game()