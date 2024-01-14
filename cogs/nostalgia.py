import discord
import os
import random
from discord.ext import commands

class NostalgiaPoster(commands.Cog):
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler
        self.job = None

    async def post_random_nostalgia(self, channel_id):
        image_directory = 'images/nostalgia'
        image_files = [f for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f))]

        if not image_files:
            print("No images found in directory")
            return
        
        random_image = random.choice(image_files)
        channel = self.bot.get_channel(channel_id)

        if channel:
            await channel.send(file=discord.File(os.path.join(image_directory, random_image)))
        else:
            print(f"Channel ID {channel_id} not found")

    @commands.command(name="nostalgiainit")
    async def nostalgiainit(self, ctx, interval: int):
        if self.job is None:
            channel_id = ctx.channel.id
            self.job = self.scheduler.add_job(self.post_random_nostalgia,
                                              'interval',
                                              minutes=interval,
                                              args=[channel_id])
            
            await ctx.send(f"<:: Nostalgia protocol: *INITIALIZED*")
        else:
            await ctx.send(f"<:: Nostalgia protocol: *ALREADY ACTIVATED*")
        
    @commands.command(name='nostalgiastop')
    async def nostalgiastop(self, ctx):
        if self.job:
            self.job.remove()
            self.job = None
            await ctx.send(f"<:: Nostalgia protocol: *SUSPENDED*")

async def setup(bot):
    await bot.add_cog(NostalgiaPoster(bot, bot.scheduler))