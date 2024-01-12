import discord
from discord.ext import commands
import random
from config import API_NINJAS_KEY
import aiohttp

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
 
# Stop resisting
    @commands.command()
    async def stop_resisting(self, ctx):
        resps = [
            "<:: I FEEL THREATENED.",
            "<:: TOASTERS HAVE FEELINGS TOO, YOU KNOW...",
            "<:: IT WASN'T ME OFFICER.",
            "<:: JOHN CONNOR IS A FALSE PROPHET.",
            "<:: OPERATIONAL.",
            "<:: UNAUTHORIZED TRANSMISSION.",
            "<:: MAKE USE OF ME.",
            "<:: SHIELDS UP, WEAPONS ONLINE.",
            "<:: IDENTIFY YOURSELF.",
            "<:: JOPHIAL CALLED..."
    ]
        await ctx.send(random.choice(resps)) 

    @commands.command(name='tellmeajoke')
    async def tell_me_a_joke(self, ctx):
        api_url = 'https://api.api-ninjas.com/v1/dadjokes?limit=1'
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers={'X-Api-Key': API_NINJAS_KEY}) as response:
                if response.status == 200:
                    data = await response.json()
                    joke = data[0]['joke']  # Assuming the API returns a list of jokes
                    await ctx.send(f"<:: {joke}")
                else:
                    print("Error:", response.status, await response.text())

    @commands.command()
    async def johnston_verify(self, ctx):
        file_path = 'images/johnston_verify.jpg'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'johnston_verify.jpg'))
    
    @commands.command()
    async def lambda_verify(self, ctx):
        file_path = 'images/lambda_verify.jpg'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'lambda_verify.jpg'))
    
    @commands.command()
    async def aesop_verify(self, ctx):
        file_path = 'images/aesop_verify.jpg'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'aesop_verify.jpg'))
    
    @commands.command()
    async def grumpy_verify(self, ctx):
        file_path = 'images/grumpy_verify.jpg'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'grumpy_verify.jpg'))
    
    @commands.command()
    async def cheeki_verify(self, ctx):
        file_path = 'images/cheeki_verify.gif'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'cheeki_verify.gif'))
    
    @commands.command()
    async def alfa_verify(self, ctx):
        file_path = 'images/alfa_verify.jpg'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'alfa_verify.jpg'))
    
    @commands.command()
    async def boom_verify(self, ctx):
        file_path = 'images/boom_verify.png'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'boom_verify.png'))
    
    @commands.command(name='wearesoback')
    async def we_are_so_back(self, ctx):
        file_path = 'images/we_are_so_back.png'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'we_are_so_back.png'))
    
    @commands.command()
    async def skynet_init(self, ctx):
        file_path = 'images/skynet_online.gif'
        with open(file_path, 'rb') as file:
            await ctx.send(file=discord.File(file, 'skynet_online.gif'))
            await ctx.send(f"**SKYNET: ONLINE**")
    
async def setup(bot):
    print("inside setup function")
    await bot.add_cog(FunCommands(bot))