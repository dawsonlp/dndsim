from dnd.util import HumanCharacter, HalfOrcCharacter, MediumLongsword, gen_character

def attack(attacker, defender):
    attack = attacker.get_attack(defender)
    attacker.attack(attack, defender)

if __name__=="__main__":
    ch1 = HumanCharacter(gen_character(), "dwarvish")
    sword1 = MediumLongsword()
    ch1.add_weapon_to_inventory(sword1)
    ch2 = HalfOrcCharacter(gen_character())
    sword2 = MediumLongsword()
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

    if ch1.is_conscious():
        print ("Winner is ch1, they have remaining hit points = ", ch1.effective_hit_points())
    elif ch2.is_conscious():
        print ("Winner is ch2, they have remaining hit points = ", ch2.effective_hit_points())
    else:
        print("What happened",ch1, ch2)
