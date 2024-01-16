import requests
import os
import discord
from datetime import datetime

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
BASE_URL = "https://api.trello.com/1/"

### trello defs

### CREATE

def create_card(list_id, card_name, card_desc):
    url = BASE_URL + "cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'idList': list_id,
        'name': card_name,
        'desc': card_desc
    }
    return requests.post(url, params=query)

TRELLO_DEFAULT_LIST_ID = os.getenv('TRELLO_DEFAULT_LIST_ID')  # or your default list ID

def create_card_default_list(card_name, card_desc):
    url = BASE_URL + "cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'idList': TRELLO_DEFAULT_LIST_ID,
        'name': card_name,
        'desc': card_desc
    }
    return requests.post(url, params=query)


### READ

def get_card(card_id):
    url = BASE_URL + f"cards/{card_id}"
    query = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    return requests.get(url, params=query)

def get_lists_in_board():
    """
    Fetch all lists in the specified Trello board.
    :return: Response object from the requests library.
    """
    url = BASE_URL + f"boards/{TRELLO_BOARD_ID}/lists"
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(url, params=params)
    return response

def get_card_details(card_id):
    """
    Fetch details of a specific Trello card.

    :param card_id: The ID of the card.
    :return: Response object from the requests library.
    """
    url = BASE_URL + f"cards/{card_id}"
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(url, params=params)
    return response

def search_card_in_list(card_name, list_name):
    """
    Search for a card by name within a specific list in Trello.

    :param card_name: The name of the card to search for.
    :param list_name: The name of the list to search in.
    :return: The ID of the card if found, otherwise None.
    """
    # First, get the list ID for the specified list name
    list_id = get_list_id_by_name(list_name)
    if not list_id:
        return None

    # URL to get all cards in the specified list
    url = BASE_URL + f"lists/{list_id}/cards"
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        cards = response.json()
        for card in cards:
            if card['name'].lower() == card_name.lower():
                return card['id']

    return None

def get_list_id_by_name(list_name):
    """
    Get the list ID for a given list name.

    :param list_name: The name of the list.
    :return: The ID of the list if found, otherwise None.
    """
    # Assume TRELLO_BOARD_ID is the ID of your Trello board
    url = BASE_URL + f"boards/{TRELLO_BOARD_ID}/lists"
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        lists = response.json()
        for lst in lists:
            if lst['name'].lower() == list_name.lower():
                return lst['id']

    return None

def search_cards(card_name):
    """
    Search for Trello cards by name.

    :param card_name: The name of the card to search for.
    :return: Response object from the requests library.
    """
    url = BASE_URL + "search"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'query': card_name,
        'modelTypes': 'cards',
        'card_fields': 'name,id'
    }
    response = requests.get(url, params=params)
    return response

def get_cards_in_list(list_id):
    """
    Fetch all cards in a specified Trello list.

    :param list_id: The ID of the Trello list.
    :return: Response object from the requests library.
    """
    url = BASE_URL + f"lists/{list_id}/cards"
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(url, params=params)
    return response

def get_card_comments(card_id):
    """
    Fetch comments of a specific Trello card.

    :param card_id: The ID of the card.
    :return: Response
    object from the requests library.
    """
    url = BASE_URL + f"cards/{card_id}/actions"
    params = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_API_TOKEN,
    'filter': 'commentCard'
    }
    response = requests.get(url, params=params)
    return response

### UPDATE

def update_card(card_id, name=None, desc=None, due=None, closed=None):
    url = BASE_URL + f"cards/{card_id}"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'name': name,
        'desc': desc,
        'due': due,
        'closed': closed
    }
    # Remove None values from params
    params = {k: v for k, v in params.items() if v is not None}
    
    response = requests.put(url, params=params)
    return response

def add_comment_to_card(card_id, comment_text, discord_username):
    """
    Add a comment to a specific Trello card.

    :param card_id: The ID of the card to comment on.
    :param comment_text: The text of the comment to add.
    :return: Response object from the requests library.
    """
    full_comment = f"Comment added in discord by {discord_username}:\n{comment_text}"
    url = BASE_URL + f"cards/{card_id}/actions/comments"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'text': full_comment
    }
    response = requests.post(url, params=params)
    return response

def move_card_to_list(card_id, list_name):
    """
    Move a Trello card to a different list.

    :param card_id: The ID of the card to move.
    :param list_name: The name of the list to move the card to.
    :return: True if the move was successful, False otherwise.
    """
    # First, get the list ID for the specified list name
    list_id = get_list_id_by_name(list_name)
    if not list_id:
        return False

    # URL to update the card's list
    url = BASE_URL + f"cards/{card_id}"
    params = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'idList': list_id
    }
    response = requests.put(url, params=params)

    return response.status_code == 200


## embeds

def display_card_details(card_id):
    response = get_card_details(card_id)
    if response.status_code == 200:
        card = response.json()
        card_url = card.get('url', 'No URL available')
        card_name = card.get('name', 'No name available')
        card_desc = card.get('desc', 'No description available')
        card_desc = card_desc[:4090] + '...' if len(card_desc) > 4096 else card_desc

        embed = discord.Embed(title=card_name, url=card_url, description=f"**Description:**\n{card_desc}", color=0x00ff00)
        return embed
    else:
        return None
    
def get_card_comments_embed(card_id, card_name):
    """
    Fetch comments of a specific Trello card and return them in a Discord Embed,
    including the timestamp for each comment.

    :param card_id: The ID of the card.
    :return: A discord.Embed object containing the comments and timestamps.
    """
    response = get_card_comments(card_id)  # Use your existing function to fetch comments
    if response.status_code == 200:
        comments = response.json()
        embed = discord.Embed(title=f"Comments for Card: {card_name}", color=0x00ff00)

        for comment in comments:
            # Formatting timestamp
            timestamp = datetime.strptime(comment['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
            formatted_time = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # Adding comment to embed
            embed.add_field(
                name=f"{comment['memberCreator']['username']} at {formatted_time}", 
                value=comment['data']['text'], 
                inline=False
            )

        return embed
    else:
        return None  # Or handle errors differently

def list_cards_embed(cards, list_name):
    embed = discord.Embed(title=f"Cards in {list_name}", color=0x00ff00)
    file = discord.File('images/thumbnails/topheader.jpg', filename='topheader.jpg')
    embed.set_thumbnail(url='attachment://topheader.jpg')

    for card in cards[:25]:  # Limit to 25 cards
        card_name = card['name']
        card_url = card['url']
        card_desc = card.get('desc', None)
        if not card_desc:
            card_desc = 'None'
        if len(card['desc']) > 120:
            card_desc = f"{card_desc[:117]}..."
        card_field_value = f"[View Card]({card_url})\nDescription: {card_desc}"
        embed.add_field(name=f"> {card_name}", value=card_field_value, inline=False)

    return file, embed