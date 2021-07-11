"""This module runs different scenarios to create datasets for analysis on which weapon/technique
 is best against which opponent, the intent is then to use machine learning to play characters off against one another.

 """

from dnd.util import *
from random import *
from itertools import chain
from dnd.combat import battle




class BattleDataGeneration:
    """Choosing an ideal weapon or attack can depend on a number of factors:
     dexterity score vs strength score
     critical damage vs critical to_hit value
     improved initiative
     speed and location in the case of ranged weapons
     and it can be better to have
    a rapier vs a sword

    This is meant to generate data to allow machine learning to determine the answer to questions like
    Which available weapon should I choose?
    Should I choose feat a, or b?
    What is my best chance of beating character x?
    What character type best suits my scores?
    For this I will need a variety of scenarios, to reduce the complexity, I will for now focus
    on low level characters."""

    def __init__(self):
        self.weapons = weapons35

    def generate_random_character(self):
        base = gen_character()
        chartype = randint(0,1)
        if chartype == 0:
            res = HumanCharacter(base, "Dwarvish")
        elif chartype == 1:
            res = HalfOrcCharacter(base)
        set_max_hitpoints(res, randint(20,60))
        weapon = choice(self.weapons)
        res.add_weapon_to_inventory(weapon)
        return res


    def battle_data_1(self, scaler):
        """generate array with attributes:
        character 1: strength, dexterity, constitution, intelligence, wisdom, charisma, initiative bonus, initial_hitpoints, max_hitpoints,
                     weapon used, final remaining effective hitpoints
        character 2: strength, dexterity...
        results (y values): char1_won, char1_remaininghp, char2_won, char2_remaininghp
        """
        ch1 = self.generate_random_character()
        stats1 = ch1.get_combat_stats()
        ch2 = self.generate_random_character()
        stats2 = ch2.get_combat_stats()
        res = battle(ch1, ch2) #Returns winner index (1 or 2) , number of hitpoints remaining for winner
        ch1_won = res[0] == 1
        if ch1_won:
            ch1_hp = res[1]
            ch2_hp = 0
            ch2_won = False
        else:
            ch2_won = True
            ch1_hp = 0
            ch2_hp = res[1]

        dta = stats1 + stats2
        battle_dta = [ch1_won, ch1_hp] + [ch2_won, ch2_hp]
        return dta, battle_dta

    def run_battle_data_1(self, count):
        """Usage note - https://stackoverflow.com/questions/12974474/how-to-unzip-a-list-of-tuples-into-individual-lists
        use zip(*res) to unzip these"""
        for btl in range(count):
            x, y =  self.battle_data_1()
            yield (x,y)


    def get_headings(self):
        """This has a list of the columns that have useful data for the learning and inference processes
        """
        h1 = ("char1_" + h for h in Character.get_combat_stat_columns() )
        h2 = ("char2_" + h for h in Character.get_combat_stat_columns() )
        j1 = ("char1_" + j for j in ("won", "hp_left"))
        j2 = ("char2_" + j for j in ("won", "hp_left"))
        x_vars = tuple(chain(h1,h2))
        y_vars = tuple(chain(j1, j2))
        return x_vars, y_vars


if __name__ == "__main__":
    datagen = BattleDataGeneration()
    x_headings, y_headings = datagen.get_headings()
    print(",".join(x_headings + y_headings))
    for rec, battle_rec in datagen.run_battle_data_1(10):
        print(",".join(str(r) for r in rec+battle_rec))
