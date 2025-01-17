from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from config import MONGO_DB_CLIENT_URI
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import time
import random
import logging
from typing import List, NamedTuple

# MongoDB setup
client = MongoClient(MONGO_DB_CLIENT_URI)
db = client.Scrapper
pokemon_Data_collection = db.pokemon_Data_new

# Ensure the 'id' field is unique in the collection
pokemon_Data_collection.create_index("id", unique=True)

# Configure logging
logging.basicConfig(filename="scraper.log", level=logging.ERROR)

# Retry mechanism for fetching URLs
def fetch_url_with_retries(url, retries=3, backoff_factor=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers={'User-agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()  # Raise HTTPError for bad responses
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                # Wait before retrying
                time.sleep(backoff_factor * (2 ** attempt) + random.uniform(0, 1))
            else:
                logging.error(f"Failed to fetch {url} after {retries} attempts: {e}")
                raise e

# Data scraping setup
scraped_pokemon_data = []

class Pokemon(NamedTuple):
    id: int
    name: str
    avatar: str
    details_path: str
    types: List[str]
    total: int
    HP: int
    attack: int
    defense: int
    sp_attack: int
    sp_defense: int
    speed: int
    entry: str

url = 'https://pokemondb.net/pokedex/all'

# Fetch the main page
try:
    page_html = fetch_url_with_retries(url)
except Exception as e:
    print(f"Error fetching main page: {e}")
    exit(1)

soup = BeautifulSoup(page_html, "html.parser")

pokemon_rows = soup.find_all("table", id="pokedex")[0].find_all("tbody")[0].find_all("tr")
scraped_count = 0

for pokemon in pokemon_rows:
    pokemon_data = pokemon.find_all("td")
    id = pokemon_data[0]['data-sort-value']
    avatar = pokemon_data[0].find("img")['src']

    name = pokemon_data[1].find_all("a")[0].getText()
    if pokemon_data[1].find("small"):
        name = pokemon_data[1].find("small").getText()
    details_uri = pokemon_data[1].find_all("a")[0]["href"]
    
    types = []
    for pokemon_type in pokemon_data[2].find_all("a"):
        types.append(pokemon_type.getText())
    
    total = pokemon_data[3].getText()
    HP = pokemon_data[4].getText()
    attack = pokemon_data[5].getText()
    defense = pokemon_data[6].getText()
    sp_attack = pokemon_data[7].getText()
    sp_defense = pokemon_data[8].getText()
    speed = pokemon_data[9].getText()

    entry_url = f'https://pokemondb.net{details_uri}'

    # Fetch the Pokémon entry page with retries
    try:
        entry_page_html = fetch_url_with_retries(entry_url)
    except Exception as e:
        print(f"Failed to fetch entry page for {name}: {e}")
        entry_text = ""
        continue

    entry_soup = BeautifulSoup(entry_page_html, "html.parser")
    
    try:
        entry_text = entry_soup.find_all("main")[0].find_all("div", {"class": "resp-scroll"})[2].find_all("tr")[0].find_all("td")[0].getText()
    except Exception as e:
        logging.error(f"Error extracting entry text for {name}: {e}")
        entry_text = ""

    typed_pokemon = Pokemon(
        id=int(id),
        name=name,
        avatar=avatar,
        details_path=details_uri,
        types=types,
        total=int(total),
        HP=int(HP),
        attack=int(attack),
        defense=int(defense),
        sp_attack=int(sp_attack),
        sp_defense=int(sp_defense),
        speed=int(speed),
        entry=entry_text,
    )
    scraped_pokemon_data.append(typed_pokemon)

    # Insert or update Pokémon data in MongoDB
    try:
        pokemon_Data_collection.update_one(
            {"id": typed_pokemon.id},  # Find Pokémon by ID
            {
                "$set": {
                    "name": typed_pokemon.name,
                    "avatar": typed_pokemon.avatar,
                    "details_path": typed_pokemon.details_path,
                    "types": typed_pokemon.types,
                    "total": typed_pokemon.total,
                    "HP": typed_pokemon.HP,
                    "attack": typed_pokemon.attack,
                    "defense": typed_pokemon.defense,
                    "sp_attack": typed_pokemon.sp_attack,
                    "sp_defense": typed_pokemon.sp_defense,
                    "speed": typed_pokemon.speed,
                    "entry": typed_pokemon.entry,
                }
            },
            upsert=True  # Insert if not found, otherwise update
        )
        scraped_count += 1
        print(f'{name}, scraped count: {scraped_count}')
    except DuplicateKeyError:
        print(f"Duplicate entry for Pokémon ID {typed_pokemon.id}. Skipping...")

    # Throttle requests to avoid overloading the server
    time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds

print("--------------------------------------------Done----------------------------------")
print(len(scraped_pokemon_data))
