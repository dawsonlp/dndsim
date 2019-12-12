"""This module runs different scenarios to create datasets for analysis on which weapon/technique
 is best against which opponent, the intent is then to use machine learning to play characters off against one another.

 """

from dnd.util import *
from random import *
from itertools import chain

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
        self.weapons = [MediumLongsword35(), WarHammer35(), Falchion35(),
                        BastardSword35(), Scimitar35()]

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

    def determine_winner(self, char1, char2, initiative_order):
        if initiative_order == 1:
            ch1 = char1
            ch2 = char2
        elif initiative_order == 2:
            ch1 = char2
            ch2 = char1
        else:
            raise Exception("Bad initiative order")
        while ch1.is_conscious() and ch2.is_conscious():
            if ch1.is_conscious():
                a1 = ch1.weapons[0].get_attack(ch1, ch2)
                if a1:
                    ch2.defend_against_attack(a1)
            if ch2.is_conscious():
                a2 = ch2.weapons[0].get_attack(ch2, ch1)
                if a2:
                    ch1.defend_against_attack(a2)
        if char1.is_conscious():
            return (1, char1.effective_hit_points())
        else:
            return (2, char2.effective_hit_points())


    def battle_data_1(self):
        """generate array with attributes:
        character 1: strength, dexterity, constitution, intelligence, wisdom, charisma, initiative bonus, initial_hitpoints, max_hitpoints,
                     weapon used, final remaining effective hitpoints
        character 2: strength, dexterity
        """
        ch1 = self.generate_random_character()
        stats1 = ch1.get_combat_stats()
        ch2 = self.generate_random_character()
        stats2 = ch2.get_combat_stats()
        initiative_1 = 0
        initiative_2 = 0
        while initiative_1 == initiative_2:
            initiative_1 = rollndx(1,20) + ch1.initiative_bonus()
            initiative_2 = rollndx(1,20) + ch2.initiative_bonus()
        if initiative_1 > initiative_2:
            initiative_order = 1
        else:
            initiative_order = 2
        res = self.determine_winner(ch1, ch2, initiative_order)
        ch1_won = res[0] == 1
        if ch1_won:
            ch1_hp = res[1]
            ch2_hp = 0
            ch2_won = False
        else:
            ch2_won = True
            ch1_hp = 0
            ch2_hp = res[1]

        record = stats1 + [ch1_won, ch1_hp] + stats2 + [ch2_won, ch2_hp]
        return record

    def run_battle_data_1(self, count):
        for btl in range(count):
            yield self.battle_data_1()
    
    def show_headings(self):
        h1 = ("char1_" + h for h in Character.get_combat_stat_columns() + ("won", "hp_left"))
        h2 = ("char2_" + h for h in Character.get_combat_stat_columns() + ("won", "hp_left"))
        return tuple(chain(h1,h2))
        


if __name__ == "__main__":
    datagen = BattleDataGeneration()
    print(",".join(datagen.show_headings()))
    for rec in datagen.run_battle_data_1(10):
        print(",".join(str(r) for r in rec))
