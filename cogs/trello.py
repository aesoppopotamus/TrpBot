import discord
from discord.ext import commands
from utils.trello_utils import create_card, get_lists_in_board, create_card_default_list, get_card_details, search_cards, get_cards_in_list

class TrelloCrud(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='idea')
    async def quick_create_card(self, ctx, card_name: str, *, card_desc: str = ''):
        response = create_card_default_list(card_name, card_desc)
        if response.status_code == 200:
            await ctx.send("<:: Idea submitted to planning board.")
        else:
            await ctx.send("<:: Failed to create card.")


    @commands.command(name='createcard')
    async def create_card_command(self, ctx, list_id: str, card_name: str, card_desc: str):
        response = create_card(list_id, card_name, card_desc)
        if response.status_code == 200:
            await ctx.send("<:: Card created successfully.")
        else:
            await ctx.send("<:: Failed to create card.")

    @commands.command(name='trellolists')
    async def list_lists(self, ctx):
        response = get_lists_in_board()
        if response.status_code == 200:
            lists = response.json()
            if lists:
                list_entries = [f"{lst['name']}" for lst in lists]
                lists_str = "\n".join(list_entries)
            embed = discord.Embed(title=':: Available Lists ::',
                                   description=f"[View Board](https://trello.com/b/gRO33mV6/trp4-planning-board)\n\n" + lists_str, color=0x00ff00)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:: Failed to retrieve lists.")

    @commands.command(name='carddetails')
    async def card_details(self, ctx, card_id: str):
        response = get_card_details(card_id)
        if response.status_code == 200:
            card = response.json()
            card_url = card['url']
            card_name = card['name']
            card_desc = card['desc'][:120] + '...' if len(card['desc']) > 120 else card['desc']

            embed = discord.Embed(title=card_name, card_url=card_url, description=card_desc, color=0x00ff00)
            await ctx.send(embed=embed)
        else:
            await ctx.send("<:: Failed to retrieve card details.")

    @commands.command(name='searchcards')
    async def search_cards_command(self, ctx, *, query: str):
        matching_cards = search_cards(query)
        if matching_cards:
            response = "\n".join([f"[{card['name']}]({card['url']}) - {card['desc'][:120]}" for card in matching_cards])
            await ctx.send(response)
        else:
            await ctx.send("No cards found matching your query.")

    @commands.command(name='listcards')
    async def list_cards(self, ctx, list_name: str):
        response = get_lists_in_board()
        if response.status_code == 200:
            lists = response.json()
            list_id = next((lst['id'] for lst in lists if lst['name'].lower() == list_name.lower()), None)

            if list_id:
                # Now fetch and display cards from this list
                card_response = get_cards_in_list(list_id)
                if card_response.status_code == 200:
                    cards = card_response.json()
                    if cards:
                        embed = discord.Embed(title=f"Cards in {list_name}", color=0x00ff00)
                        file = discord.File('images/thumbnails/topheader.png', filename='topheader.png')
                        embed.set_thumbnail(url='attachment://topheader.png')
                        for card in cards[:25]:  # Limit to 25 cards
                            card_name = card['name']
                            card_url = card['url']
                            card_desc = card['desc'][:120] + '...' if len(card['desc']) > 120 else card['desc']
                            card_field_value = f"[View Card]({card_url})\nDescription: {card_desc}"
                            embed.add_field(name=f"> {card_name}", value=card_field_value, inline=False)

                        await ctx.send(file=file, embed=embed)
                    else:
                        await ctx.send(f"No cards found in the list '{list_name}'.")
                else:
                    await ctx.send(f"Failed to retrieve cards from the list '{list_name}'.")
            else:
                await ctx.send(f"List '{list_name}' not found on the board.")
        else:
            await ctx.send("Failed to retrieve lists from the board.")

async def setup(bot):
    await bot.add_cog(TrelloCrud(bot))
