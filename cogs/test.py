from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("What is grass?")

    @commands.command()
    async def ping(self, ctx):
        print("inside ping command")
        await ctx.send("Pong from Cogginsville.")
                       
async def setup(bot):
    print("inside setup function")
    await bot.add_cog(Test(bot))