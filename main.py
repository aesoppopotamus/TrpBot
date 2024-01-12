import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from dotenv import load_dotenv
from database.database import Database

load_dotenv()

# intents setup
intents = discord.Intents.all() 
intents.messages = True

TOKEN = os.getenv('BOT_TOKEN')

class MyBot(commands.Bot):
        def __init__(self, command_prefix, intents):
                super().__init__(command_prefix, intents=intents)
                self.scheduler = AsyncIOScheduler()
                self.db = Database(self, self.scheduler)  # Initialize Database here
        
        async def send_message(self, channel_id, message):
                channel = self.get_channel(channel_id)
                if channel:
                        await channel.send(message)
                else:
                        print(f"Channel {channel_id} not found")

        async def on_ready(self):
                await self.db.queue_repeating_messages()
                self.scheduler.start()

                # Load cogs here
                await self.load_extension('cogs.schedulingcommands')
                await self.load_extension('cogs.funcommands')
                await self.load_extension('cogs.skynet_help')
                print(f'Logged in as {self.user.name}')

bot = MyBot(command_prefix='!', intents=intents)        
bot.run(TOKEN)