import requests
import os


TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
BASE_URL = "https://api.trello.com/1/"

### trello defs

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


def get_card(card_id):
    url = BASE_URL + f"cards/{card_id}"
    query = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    return requests.get(url, params=query)

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

def search_cards(query, list_id=None):
    """
    Search for cards by name or keyword.

    :param query: The search query (part of the card's name).
    :param list_id: Optional ID of the list to search within.
    :return: List of cards matching the query.
    """
    # If list_id is provided, search within that list; otherwise, search the entire board
    search_url = BASE_URL + ("lists/" + list_id + "/cards" if list_id else "boards/" + TRELLO_BOARD_ID + "/cards")
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        return []

    all_cards = response.json()
    return [card for card in all_cards if query.lower() in card['name'].lower()]

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
