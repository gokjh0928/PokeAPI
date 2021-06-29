import requests
import pprint
from IPython.display import clear_output as co
from os import system, name
from collections import defaultdict


def clear():
    # for windows
    if name == 'nt':
        _ = system('cls')
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


class Pokedex:
    dex_dict = defaultdict(list)
    last_added = []
    pokemon_present = []
    stat_lists = defaultdict(lambda: defaultdict(list))
    avg_stat_vals = defaultdict(dict)

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
                # Append the pokemon info dictionary to the list
                last_entry.append((poketype, len(self.dex_dict[poketype])))
                # assigns list containing the info dict to the new type category
                self.dex_dict[poketype].append(pokeinfo)

                for stat in pokeinfo['basestats']:
                    self.stat_lists[poketype][stat].append(
                        pokeinfo['basestats'][stat])
                    self.avg_stat_vals[poketype][stat] = sum(
                        self.stat_lists[poketype][stat]) / len(self.stat_lists[poketype][stat])

            # append the last_entry to last_added to allow for Pokemon deletion later
            self.last_added.append(last_entry)
            # add pokemon's name to list of Pokemon present in the Pokedex
            self.pokemon_present.append(pokemon)

            print(f"Added {pokemon.title()}")

    def remove(self):
        """ Removes the last added Pokemon from the Pokedex """
        # Gets the last added pokemon
        last_entry = self.last_added[-1]

        del_avg_category = False
        # Delete the Pokemon in all of the type categories it's in
        # (i.e. Removing Charizard from the 'Fire' list at index 2, from 'Flying' list at index 5)
        for coord in last_entry:
            category = coord[0]
            idx = coord[1]
            name = self.dex_dict[category][idx]['name']
            del self.dex_dict[category][idx]
            for stat in ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']:
                del self.stat_lists[category][stat][-1]
                if self.stat_lists[category][stat]:
                    self.avg_stat_vals[category][stat] = sum(
                        self.stat_lists[category][stat]) / len(self.stat_lists[category][stat])
                else:
                    del_avg_category = True
            if del_avg_category:
                del self.avg_stat_vals[category]
                del_avg_category = False
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
        self.avg_stat_vals.clear()
        self.stat_lists.clear()

    def print(self):
        print("POKEDEX:")
        pprint.pprint(dict(self.dex_dict), sort_dicts=False)
        print("STAT AVG PER TYPE:")
        pprint.pprint(dict(dict(self.avg_stat_vals)), sort_dicts=False)


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
        if not pd.pokemon_present:
            print("No Pokemon to remove!")
        else:
            pd.remove()
    elif command == "view":
        pd.print()
    elif command == "clear":
        pd.clear()
    elif command == "quit":
        co()
        clear()
        break
    else:
        print("Please enter a valid command")
    input("Press any key to continue ")
