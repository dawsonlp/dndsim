from dnd.util import HumanCharacter, HalfOrcCharacter, MediumLongsword35, gen_character, rollndx
import pandas as pd
import copy

def battle(ch1, ch2):
    """res[0] says if 1 or 2 won, res[1] has number of hitpoints remaining"""
    initiative_1 = 0
    initiative_2 = 0
    while initiative_1 == initiative_2:
        initiative_1 = rollndx(1, 20) + ch1.initiative_bonus()
        initiative_2 = rollndx(1, 20) + ch2.initiative_bonus()
    if initiative_1 > initiative_2:
        initiative_order = 1
    else:
        initiative_order = 2
    res = determine_winner(ch1, ch2, initiative_order)
    ch1_won = res[0] == 1
    if ch1_won:
        ch1_hp = res[1]
        ch2_hp = 0
        ch2_won = False
    else:
        ch2_won = True
        ch1_hp = 0
        ch2_hp = res[1]
    return res

def determine_winner(char1, char2, initiative_order):
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

def get_win_probability_from_simulation(ch1, ch2, trials=10000):
    """Show two characters and their chance of a winning
    To test should run multiple bouts between a and b and see how that
    compares to the output of the final layer"""

    def trial(ch1, ch2):
        char1 = copy.deepcopy(ch1)
        char2 = copy.deepcopy(ch2)
        res = battle(char1, char2)
        if res[0] == 1:
            return (1, 0)
        else:
            return (0, 1)
    battleres = [trial(ch1, ch2) for t in range(trials)]
    winner_record = pd.DataFrame(battleres).mean()
    return winner_record

def attack(attacker, defender):
    attack = attacker.get_attack(defender)
    attacker.attack(attack, defender)

def test1():
    ch1 = HumanCharacter(gen_character(), "dwarvish")
    sword1 = MediumLongsword35()
    ch1.add_weapon_to_inventory(sword1)
    ch2 = HalfOrcCharacter(gen_character())
    sword2 = MediumLongsword35()
    ch2.add_weapon_to_inventory(sword2)
    print(ch1, "\n", ch2, "\n*******************************\n")
    while ch1.is_conscious() and ch2.is_conscious():
        if ch1.is_conscious():
            a1 = sword1.get_attack(ch1, ch2)
            print("ch1 is attacking")
            if a1:
                ch2.defend_against_attack(a1)
            print(ch1.effective_hit_points(), ch2.effective_hit_points())
        if ch2.is_conscious():
            print("ch2 is attacking")
            a2 = sword2.get_attack(ch2, ch1)
            if a2:
                ch1.defend_against_attack(a2)
            print(ch1.effective_hit_points(), ch2.effective_hit_points())
    if ch1.is_conscious():
        print("Winner is ch1, they have remaining hit points = ", ch1.effective_hit_points())
    elif ch2.is_conscious():
        print("Winner is ch2, they have remaining hit points = ", ch2.effective_hit_points())
    else:
        print("What happened", ch1, ch2)


def test2():
    ch1 = HumanCharacter(gen_character(), "dwarvish")
    sword1 = MediumLongsword35()
    ch1.add_weapon_to_inventory(sword1)
    ch2 = HalfOrcCharacter(gen_character())
    sword2 = MediumLongsword35()
    ch2.add_weapon_to_inventory(sword2)
    print(ch1)
    print(ch2)
    results = get_win_probability_from_simulation(ch1, ch2)
    print(results)

if __name__=="__main__":
    test2()
