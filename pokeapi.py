import requests
import pprint
from IPython.display import clear_output as co
from os import system, name


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


class Pokedex:
    dex_dict = {}
    last_added = []
    pokemon_present = []

    def add(self, pokemon):
        """ Adds a Pokemon to the Pokedex if the input name is a valid one """
        # Get response from the request
        res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        # 1. Checks if the status code of requestis 200(Success) or not(Fail)
        if res.status_code != 200:
            print(f"Failed to find {pokemon.title()}")
            return
        # 2. Checks if Pokemon is already in the Pokedex
        elif pokemon in self.pokemon_present:
            print(f"{pokemon.title()} is already in the Pokedex!")
            return
        # 3. Adds the Pokemon to the Pokedex
        else:
            # Creates a Pokemon object using the response(res), and gets the dictionary containing its info
            pokeinfo = Pokemon(res).info

            # When adding a pokemon, get its type category and index for that categroy(i.e. ('electric', 2))
            last_entry = []   # list bc pokemon may have 2 types, and have different indexes for each type
            # (will be used for the remove method)

            # Append Pokemon's info dict to the lists of its types(i.e. Charizard to 'flying' and 'fire' lists)
            for poketype in pokeinfo['types']:
                # If a list for the type already exists, append the pokemon info dictionary to the list
                if poketype in self.dex_dict:
                    last_entry.append((poketype, len(self.dex_dict[poketype])))
                    self.dex_dict[poketype].append(pokeinfo)
                # If the list for the type is not yet created, create the list and add Pokemon's info dict
                else:
                    last_entry.append((poketype, 0))
                    # assigns list containing the info dict to the new type category
                    self.dex_dict[poketype] = [pokeinfo]

            # append the last_entry to last_added to allow for Pokemon deletion later
            self.last_added.append(last_entry)
            # add pokemon's name to list of Pokemon present in the Pokedex
            self.pokemon_present.append(pokemon)

            print(f"Added {pokemon.title()}")

    def remove(self):
        """ Removes the last added Pokemon from the Pokedex """
        # Gets the last added pokemon
        last_entry = self.last_added[-1]

        # Delete the Pokemon in all of the type categories it's in
        # (i.e. Removing Charizard from the 'Fire' list at index 2, from 'Flying' list at index 5)
        for coord in last_entry:
            category = coord[0]
            idx = coord[1]
            name = self.dex_dict[category][idx]['name']
            del self.dex_dict[category][idx]
            if not self.dex_dict[category]:
                del self.dex_dict[category]

        # Since the Pokemon is deleted, don't need the last_entry anymore, so delete it
        del self.last_added[-1]
        del self.pokemon_present[-1]
        print(f"Removed {name}")

    def clear(self):
        """ Clears all Pokemon from the Pokedex """
        print(
            f"Removed {(', '.join([p.title() for p in self.pokemon_present]) or 'Nothing!')}")
        self.dex_dict.clear()
        self.last_added.clear()
        self.pokemon_present.clear()


class Pokemon:
    def __init__(self, res):
        data = res.json()
        self.info = {}

        # Name
        self.info['name'] = data['name'].title()

        # ID
        self.info['id'] = data['id']

        # Types
        types = []
        for poketype in data['types']:
            types.append(poketype['type']['name'])
        self.info['types'] = types

        # Height
        self.info['height'] = data['height']

        # Weight
        self.info['weight'] = data['weight']

        # Abilities
        abilities = []
        for ability in data['abilities']:
            abilities.append(ability['ability']['name'])
        self.info['ability'] = abilities

        # Stats
        stats = {}
        for stattype in data['stats']:
            stats[stattype['stat']['name']] = stattype['base_stat']
        self.info['basestats'] = stats


while True:
    clear()
    co()
    pd = Pokedex()
    print("Welcome to the Pokedex! What would you like to do?")
    command = input(
        "- 'Add' to Pokedex\n- 'View' Pokedex\n- 'Remove' last added Pokemon from Pokedex\n- 'Clear' Pokedex\n- 'Quit'\n").lower()
    clear()
    co()
    if command == "add":
        pokemon = input("Which Pokemon do you wish to add? ").lower()
        pd.add(pokemon)
    elif command == "remove":
        pd.remove()
    elif command == "view":
        print("POKEDEX:")
        pprint.pprint(pd.dex_dict, sort_dicts=False)
    elif command == "clear":
        pd.clear()
    elif command == "quit":
        co()
        clear()
        break
    else:
        print("Please enter a valid command")
    input("Press any key to continue ")
