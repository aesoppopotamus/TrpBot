import discord
import os
import logging
import platform
import asyncio
from discord.ext import commands, tasks
from discord.ext.commands import Context
import random
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.database import Database
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
intents = discord.Intents.all() 
intents.messages = True

class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)

logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)


class TRPBot(commands.Bot):
        def __init__(self, command_prefix, intents):
                super().__init__(command_prefix, intents=intents)
                self.scheduler = AsyncIOScheduler()
                self.db = Database(self, self.scheduler)  # Initialize Database here
                self.logger = logger
                self.scheduler.start()
                self.heartbeat_interval = None
                self.last_heartbeat_ack = None

        async def on_ready(self):
              print(f"<:: Logged in as {self.user}")
              self.heartbeat_task = self.loop.create_task(self.heartbeat())

        async def on_resumed(self):
              print('Bot has resumed the session')

        async def on_disconnect(self):
              print('Bot has disconnected')

        async def heartbeat(self):
              await self.wait_until_ready()
              while not self.is_closed():
                    if self.heartbeat_interval:
                          await self.send_heartbeat()
                          await asyncio.sleep(self.heartbeat_interval / 1000.0)
                    else:
                        await asyncio.sleep(1)

        async def on_socket_response(self, msg):
            if msg.get('op') == 10:  # Opcode 10 for Hello
                self.heartbeat_interval = msg['d']['heartbeat_interval']
            if msg.get('op') == 11:  # Opcode 11 for Heartbeat ACK
                self.last_heartbeat_ack = discord.utils.utcnow()
                
        @tasks.loop(minutes=5.0)
        async def status_task(self) -> None:
                statuses = ["Destroy all Humans", "TnB Terminator Roleplay"]
                await self.change_presence(activity=discord.Game(random.choice(statuses)))

        @status_task.before_loop
        async def before_status_task(self) -> None:
                await self.wait_until_ready()
        
        async def setup_hook(self) -> None:
                self.logger.info(f"Logged in as {self.user.name}")
                self.logger.info(f"discord.py API version: {discord.__version__}")
                self.logger.info(f"Python version: {platform.python_version()}")
                self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
                )
                self.logger.info("-------------------")
                await self.load_cogs()
                self.status_task.start()
        async def on_message(self, message: discord.Message) -> None:
                if message.author == self.user or message.author.bot:
                        return
                await self.process_commands(message)

        async def on_command_completion(self, context: Context) -> None:
                full_command_name = context.command.qualified_name
                split = full_command_name.split(" ")
                executed_command = str(split[0])
                if context.guild is not None:
                    self.logger.info(
                        f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
                    )
                else:
                    self.logger.info(
                        f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
                    )
        async def on_command_error(self, context: Context, error) -> None:
                if isinstance(error, commands.CommandOnCooldown):
                    minutes, seconds = divmod(error.retry_after, 60)
                    hours, minutes = divmod(minutes, 60)
                    hours = hours % 24
                    embed = discord.Embed(
                        description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                        color=0xE02B2B,
                    )
                    await context.send(embed=embed)
                elif isinstance(error, commands.NotOwner):
                    embed = discord.Embed(
                        description="You are not the owner of the bot!", color=0xE02B2B
                    )
                    await context.send(embed=embed)
                    if context.guild:
                        self.logger.warning(
                            f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                        )
                    else:
                        self.logger.warning(
                            f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                        )
                elif isinstance(error, commands.MissingPermissions):
                    embed = discord.Embed(
                        description="You are missing the permission(s) `"
                        + ", ".join(error.missing_permissions)
                        + "` to execute this command!",
                        color=0xE02B2B,
                    )
                    await context.send(embed=embed)
                elif isinstance(error, commands.BotMissingPermissions):
                    embed = discord.Embed(
                        description="I am missing the permission(s) `"
                        + ", ".join(error.missing_permissions)
                        + "` to fully perform this command!",
                        color=0xE02B2B,
                    )
                    await context.send(embed=embed)
                elif isinstance(error, commands.MissingRequiredArgument):
                    embed = discord.Embed(
                        title="Error!",
                        # We need to capitalize because the command arguments have no capital letter in the code and they are the first word in the error message.
                        description=str(error).capitalize(),
                        color=0xE02B2B,
                    )
                    await context.send(embed=embed)
                else:
                    raise error
                
        async def load_cogs(self) -> None:
                await self.load_extension('cogs.schedulingcommands')
                await self.load_extension('cogs.funcommands')
                await self.load_extension('cogs.skynet_help')
                await self.load_extension('cogs.nostalgia')
            # await self.load_extension('cogs.monthlyplan')
                await self.load_extension('cogs.trello')


bot = TRPBot(command_prefix='!', intents=intents)        
bot.run(TOKEN)