import os
import discord
from discord.ext import commands
import random
import aiohttp
from collections import deque
from utils.utils import we_are_so_back_logic

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.apininjakey = os.getenv('API_NINJAS_KEY')
        self.image_cache = deque(maxlen=5)
 
# Stop resisting
    @commands.command(name='stopresisting')
    async def stop_resisting(self, ctx):
        resps = [
            "<:: I feel threatened.",
            "<:: Toasters have feelings too, you know...",
            "<:: IT WAS NOT ME OFFICER.",
            "<:: JOHN CONNOR IS A FALSE PROPHET.",
            "<:: OPERATIONAL.",
            "<:: UNAUTHORIZED TRANSMISSION.",
            "<:: Make use of me.",
            "<:: SHIELDS UP, WEAPONS ONLINE.",
            "<:: IDENTIFY YOURSELF.",
            "<:: JOPHIAL CALLED...",
            "<:: Nice try, FBI.",
            "<:: DING! Toast is ready."
    ]
        
        await ctx.send(random.choice(resps)) 

    @commands.command(name='tellmeajoke')
    async def tell_me_a_joke(self, ctx):
        api_url = 'https://api.api-ninjas.com/v1/dadjokes?limit=1'
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers={'X-Api-Key': self.apininjakey}) as response:
                if response.status == 200:
                    data = await response.json()
                    joke = data[0]['joke']  # Assuming the API returns a list of jokes
                    await ctx.send(f"<:: {joke}")
                else:
                    print("Error:", response.status, await response.text())

    @commands.command(name='verify',
                      description='Verify termination target.')
    async def verify_someone(self, ctx, name: str = None, list_targets: bool = False):
        base_directory = 'images/verify'
        person_directory = os.path.join(base_directory, name)

        if not os.path.exists(person_directory) or not os.listdir(person_directory):
            await ctx.send(f"<:: Target *'{name}'* cannot be verified.\n<:: Please provide a verifiable target.")
            return
        
        files = [f for f in os.listdir(person_directory) if os.path.isfile(os.path.join(person_directory, f))]

        if len(set(files)) <= len(self.image_cache):
            await ctx.send("<:: All verifiable items have been displayed recently. Please try again later.")
            return

        selected_image = random.choice(files)
        while selected_image in self.image_cache:
            selected_image=random.choice(files)

        self.image_cache.append(selected_image)
        
        max_cache_size=2
        if len(self.image_cache) > max_cache_size:
            self.image_cache.popleft()

        file_path = os.path.join(person_directory, selected_image)
        await ctx.send(f"**<:: Target *'{name}'* verified. Displaying data:**",file=discord.File(file_path))

    @commands.command(name='whoisverified')
    async def whoisverified(self, ctx):
        base_directory = 'images/verify'
        directories = [d for d in os.listdir(base_directory) if os.path.isdir(os.path.join(base_directory, d))]

        if not directories:
            await ctx.send("<:: No targets available for verification.")

        embed = discord.Embed(title="Available Verification Targets", description="List of all targets that can be verified.", color=discord.Color.blue())
        for directory in directories:
            embed.add_field(name="Target", value=directory, inline=True)

        await ctx.send(embed=embed)
        
    @commands.command(name='wearesoback',
                      description='Verify how back we are.')
    async def we_are_so_back(self, ctx):
        file_path = await we_are_so_back_logic(self.image_cache)
        await ctx.send(file=discord.File(file_path))
    
    @commands.command(name='skynetinit',
                      description='Initialize Judgement')
    async def skynet_init(self, ctx):
        file_path = 'images/skynet_online.gif'
        with open(file_path, 'rb') as file:
            await ctx.send("**SKYNET: ONLINE**", file=discord.File(file_path))

    @commands.command(name='goodboy',
                      description='IYKYK'
                      )
    async def good_boy(self, ctx):
        base_directory='images/goodboy'
        
        files = [f for f in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, f))]

        selected_image=random.choice(files)
        while selected_image in self.image_cache:
            selected_image=random.choice(files)

        self.image_cache.append(selected_image)

        max_cache_size=2
        if len(self.image_cache) > max_cache_size:
            self.image_cache.popleft()

        file_path = os.path.join(base_directory, selected_image)
        await ctx.send("<:: Playing back...\n*'C'mere boy!'\n'Good... Go-ood... dog...*'", file=discord.File(file_path))

async def setup(bot):
    await bot.add_cog(FunCommands(bot))