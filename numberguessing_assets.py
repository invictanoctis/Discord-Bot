from random import randint
import asyncio

class GuessingGame:
    def __init__(self, ctx, highest_number: int):
        self.ctx = ctx
        self.max_number = highest_number
        self.ran_number = randint(1, self.max_number)
        self.amount_guesses = 0
        self.is_running = True

    async def start_game(self):
        await self.ctx.send(f"Guess a number between 1 and {self.max_number}!")

        def check(m):
            return m.author == self.ctx.author and m.channel == self.ctx.channel

        while self.is_running:
            try:
                message = await self.ctx.bot.wait_for('message', check=check, timeout=60)
                self.amount_guesses += 1
                guessed_number = int(message.content)

                if guessed_number < 1 or guessed_number > self.max_number:
                    await self.ctx.send(f"Invalid number, please pick a number between 1 and {self.max_number}.")
                elif guessed_number > self.ran_number:
                    await self.ctx.send("Your number was too high, try again!")
                elif guessed_number < self.ran_number:
                    await self.ctx.send("Your number was too low, try again!")
                else:
                    await self.ctx.send(f"Congratulations {self.ctx.author.mention}, you won with {self.amount_guesses} guesses!")
                    self.is_running = False

            except ValueError:
                await self.ctx.send("That was not a valid number!")
            except asyncio.TimeoutError:
                await self.ctx.send("You took too long! The game has ended.")
                self.is_running = False

        await self.ask_play_again()

    async def ask_play_again(self):
        await self.ctx.send("Do you want to play again? (Type 'yes' or 'no')")

        def check(m):
            return m.author == self.ctx.author and m.channel == self.ctx.channel

        try:
            response = await self.ctx.bot.wait_for('message', check=check, timeout=30)
            if response.content.lower() == 'yes':
                self.ran_number = randint(1, self.max_number)  # Reset for a new game
                self.amount_guesses = 0
                await self.start_game()  # Restart the game
            else:
                await self.ctx.send("Thanks for playing!")
        except asyncio.TimeoutError:
            await self.ctx.send("You took too long to respond! The game has ended.")