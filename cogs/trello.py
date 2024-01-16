import discord
import os
from discord.ext import commands
import asyncio
import utils.trello_utils as trello_utils
from utils.utils import has_role

class TrelloCrud(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

## CREATE -------------------

    @commands.command(name='idea')
    async def quick_create_card(self, ctx, card_name: str, *, card_desc: str = ''):
        response = trello_utils.create_card_default_list(card_name, card_desc)
        if response.status_code == 200:
            await ctx.send("<:: Idea submitted to planning board.")
        else:
            await ctx.send("<:: Failed to create card.")


   # @commands.command(name='createcard')
   # async def create_card_command(self, ctx, list_id: str, card_name: str, card_desc: str):
   #     response = create_card(list_id, card_name, card_desc)
   #     if response.status_code == 200:
   #         await ctx.send("<:: Card created successfully.")
   #     else:
   #         await ctx.send("<:: Failed to create card.")

## READ -------------------

    @commands.command(name='trellolists')
    async def list_lists(self, ctx):
        response = trello_utils.get_lists_in_board()
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
    async def card_details(self, ctx, *, card_name: str):
        search_response = trello_utils.search_cards(card_name)
        if search_response.status_code == 200 and search_response.json()['cards']:
            cards = search_response.json()['cards']

            # If only one card is found, display its details directly
            if len(cards) == 1:
                embed = trello_utils.display_card_details(cards[0]['id'])
                if embed:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("<:: Failed to retrieve card details.")
                return

            # If multiple cards are found, list them for the user to choose
            card_list = [f"{idx + 1}. {card['name']}" for idx, card in enumerate(cards)]
            card_list_message = "\n".join(card_list)
            await ctx.send(f"Multiple cards found. Please select a card by number:\n{card_list_message}")

            # Check for user's response
            def check(m):
                return m.author == ctx.author and m.content.isdigit() and 0 < int(m.content) <= len(cards)

            try:
                user_msg = await self.bot.wait_for('message', check=check, timeout=30.0)  # 30 seconds to respond
                selected_index = int(user_msg.content) - 1
                embed = trello_utils.display_card_details(cards[selected_index]['id'])
                if embed:
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("<:: Failed to retrieve card details.")
            except asyncio.TimeoutError:
                await ctx.send("You didn't respond in time. Please try the command again.")
        else:
            await ctx.send(f"<:: No results found for '{card_name}'.")

   # @commands.command(name='searchcards')
   # async def search_cards_command(self, ctx, *, query: str):
   #     matching_cards = search_cards(query)
   #     if matching_cards:
   #         response = "\n".join([f"[{card['name']}]({card['url']}) - {card['desc'][:120]}" for card in matching_cards])
   #         await ctx.send(response)
   #     else:
   #         await ctx.send("No cards found matching your query.")

    @commands.command(name='listcards')
    async def list_cards(self, ctx, list_name: str):
        response = trello_utils.get_lists_in_board()
        if response.status_code == 200:
            lists = response.json()
            list_id = next((lst['id'] for lst in lists if lst['name'].lower() == list_name.lower()), None)
            if list_id:
                # Now fetch and display cards from this list
                card_response = trello_utils.get_cards_in_list(list_id)
                if card_response.status_code == 200:
                    cards = card_response.json()
                    if cards:
                        file, embed = trello_utils.list_cards_embed(cards, list_name)
                        await ctx.send(file=file, embed=embed)
                    else:
                        await ctx.send(f"<:: No cards found in the list '{list_name}'.")
                else:
                    await ctx.send(f"<:: Failed to retrieve cards from the list '{list_name}'.")
            else:
                await ctx.send(f"<:: List '{list_name}' not found on the board.")
        else:
            await ctx.send("<:: Failed to retrieve lists from the board.")

    @commands.command(name='listcomments')
    async def list_comments(self, ctx, *, card_name: str):
        # Search for the card
        search_response = trello_utils.search_cards(card_name)
        if search_response.status_code == 200 and search_response.json()['cards']:
            cards = search_response.json()['cards']
    
            # Handle single card match
            if len(cards) == 1:
                await self.display_card_comments(ctx, cards[0]['id'], cards[0]['name'])
                return
    
            # Handle multiple card matches
            card_list = [f"{idx + 1}. {card['name']}" for idx, card in enumerate(cards)]
            card_list_message = "\n".join(card_list)
            await ctx.send(f"Multiple cards found. Please select a card by number:\n{card_list_message}")
    
            def check(m):
                return m.author == ctx.author and m.content.isdigit() and 0 < int(m.content) <= len(cards)
    
            try:
                user_msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                selected_index = int(user_msg.content) - 1
                selected_card = cards[selected_index]
                await self.display_card_comments(ctx, cards[selected_index]['id'], selected_card['name'])
            except asyncio.TimeoutError:
                await ctx.send("You didn't respond in time. Please try the command again.")
        else:
            await ctx.send(f"<:: No results found for '{card_name}'.")
    
    async def display_card_comments(self, ctx, card_id, card_name):
        embed = trello_utils.get_card_comments_embed(card_id, card_name)
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to retrieve comments or no comments found on this card.")

    @commands.command(name='needsreview')
    async def needs_review(self, ctx):
        required_role = "t800"
        if not has_role(ctx, required_role):
            await ctx.send("<:: You do not have the required role to review ideas.")
            return
        
        TRELLO_NEEDSREVIEW_LIST_ID = os.getenv('TRELLO_NEEDSREVIEW_LIST_ID')
        card_response = trello_utils.get_cards_in_list(TRELLO_NEEDSREVIEW_LIST_ID)
        if card_response.status_code == 200:
            cards = card_response.json()
        if cards:
            card_titles = [card['name'] for card in cards]
            await ctx.send("\n".join(card_titles))
        else:
            await ctx.send("<:: No ideas currently need review.")
            
## UPDATE -------------------
            
    @commands.command(name='addcomment')
    async def add_comment(self, ctx, *, card_name: str):
        # Search for the card
        search_response = trello_utils.search_cards(card_name)
        if search_response.status_code == 200 and search_response.json()['cards']:
            cards = search_response.json()['cards']

            # Handle single card match
            if len(cards) == 1:
                await self.prompt_for_comment(ctx, cards[0]['id'])
                return

            # Handle multiple card matches
            card_list = [f"{idx + 1}. {card['name']}" for idx, card in enumerate(cards)]
            card_list_message = "\n".join(card_list)
            await ctx.send(f"<:: Multiple cards found. Please select a card by number:\n{card_list_message}")

            def check(m):
                return m.author == ctx.author and m.content.isdigit() and 0 < int(m.content) <= len(cards)

            try:
                user_msg = await self.bot.wait_for('message', check=check, timeout=30.0)
                selected_index = int(user_msg.content) - 1
                await self.prompt_for_comment(ctx, cards[selected_index]['id'])
            except asyncio.TimeoutError:
                await ctx.send("<:: You didn't respond in time. Please try the command again.")
        else:
            await ctx.send(f"<:: No results found. Please try again.")

    async def prompt_for_comment(self, ctx, card_id):
        await ctx.send("<:: Please enter your comment")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            comment_msg = await self.bot.wait_for('message', check=check, timeout=60.0)  # 1 minute to respond
            discord_username = ctx.author.display_name
            response = trello_utils.add_comment_to_card(card_id, comment_msg.content, discord_username)
            if response.status_code == 200:
                await ctx.send("<:: Comment added successfully!")
            else:
                await ctx.send("<:: Failed to add comment to the card.")
        except asyncio.TimeoutError:
            await ctx.send("<:: You didn't respond in time. Please try the command again.")

    @commands.command(name='reviewidea')
    async def review_idea(self, ctx, card_name: str, comments: str, approve: bool):
        # Step 1: Search for the card in the "NEEDS REVIEW" list
        required_role = "t800"

        if not has_role(ctx, required_role):
            await ctx.send("<:: You do not have the required role to review ideas.")
            return
    
        card_id = trello_utils.search_card_in_list(card_name, "NEEDS REVIEW")
    
        # Step 2: Add comments to the card
        if card_id:
            trello_utils.add_comment_to_card(card_id, comments)
    
            # Step 3: Move the card to the appropriate list
            new_list = "APPROVED" if approve else "DENIED"
            trello_utils.move_card_to_list(card_id, new_list)
            await ctx.send(f"Idea '{card_name}' has been {'approved' if approve else 'denied'} and moved to the '{new_list}' list.")
        else:
            await ctx.send("Card not found in 'NEEDS REVIEW' list.")


async def setup(bot):
    await bot.add_cog(TrelloCrud(bot))
