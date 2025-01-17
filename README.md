# Pokemon Scrapper

A Python-based web scraper that collects detailed Pokémon data from [PokemonDB](https://pokemondb.net/pokedex/all) and stores it in a MongoDB database. This project demonstrates how to use web scraping, MongoDB, and Python for data collection and storage.

## Features
- Scrapes Pokémon stats, types, and entries.
- Stores scraped data in MongoDB with proper indexing to avoid duplication.
- Implements retry mechanisms and throttling to handle web scraping gracefully.
- Logs errors for debugging purposes.

## Prerequisites
Before running the script, ensure you have the following installed:
- Python 3.9 or higher
- MongoDB
- Required Python libraries (listed in `requirements.txt`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Atif-PT/Pokemon-Scrapper.git
   cd Pokemon-Scrapper
