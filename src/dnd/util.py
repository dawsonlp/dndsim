
import munch
from math import floor
import random
import uuid


__hit_bonus_for_size__ = {"medium": 0, "small": 1, "tiny": 2, "diminutive": 4, "fine": 8,
                          "large": -1, "huge": -2, "gargantuan": -4, "colassal": -8}

def hit_bonus_for_size(size):
    if size in __hit_bonus_for_size__:
        return __hit_bonus_for_size__[size]
    else: raise Exception("Bad size")

class SuccessfulAttack(object):

    def __init__(self, damage, attacker, defender):
        self.damage_points = damage
        self.attacker = attacker
        self.defender = defender

    def damage(self):
        return self.damage_points

class Armor(object):
    def __init__(self, armor_bonus, shield_bonus, max_dex_bonus,
                 armor_check_penalty,
                 arcane_spell_failure_chance,
                 speed_if_base_30, speed_if_base_20,
                 weight, cost):
        self.armor_bonus = armor_bonus
        self.shield_bonus = shield_bonus
        self.max_dex_bonus = max_dex_bonus
        self.armor_check_penalty = armor_check_penalty
        self.arcane_spell_failure_chance = arcane_spell_failure_chance
        self.speed_if_base_30 = speed_if_base_30
        self.speed_if_base_20 = speed_if_base_20
        self.weight = weight
        self.cost = cost

class PaddedArmor(Armor):
    def __init__(self):
        super().__init__(1, 0, 8, 0, 0.05, 30, 20, 10, 5)

class LeatherArmor(Armor):
    def __init__(self):
        super().__init__(2, 0, 6, 0, 0.1, 30, 20, 15, 10)

class StuddedLeatherArmor(Armor):
    def __init__(self):
        super().__init__(3, 0, 5, -1, 0.15, 30, 20, 20, 25)



class Weapon(object):
    def __init__(self, critical, critical_damage_multiplier, weapon_type, weapon_id, dice_count, dice_size, weight, cost):
        self.critical = critical
        self.critical_damage_multiplier = critical_damage_multiplier
        self.weapon_type = weapon_type
        self.weapon_id = weapon_id
        self.dice_count = dice_count
        self.dice_size = dice_size
        self.weight = weight
        self.cost = cost

    def base_damage(self):
        return rollndx(self.dice_count, self.dice_size)

    def critical_damage(self, damage_modifier):
        dmgs = (max(1, self.base_damage() + damage_modifier) for x in range(self.critical_damage_multiplier - 1))
        return sum(dmgs)

class MeleeWeapon35(Weapon):
    """This is based on the rules for dnd version 3.5 - will need a separate one for the new rules"""
    def __init__(self, critical, critical_damage_multiplier, weapon_type, weapon_id, dice_count, dice_size, weight, cost):
        super().__init__(critical, critical_damage_multiplier, weapon_type, weapon_id, dice_count, dice_size, weight, cost)

    def __calculate_basic_attack__(self, attacker, defender):
        damage_modifier = modifier(attacker.strength)
        base_damage = max(1, self.base_damage() + damage_modifier)
        to_hit = rollndx(1, 20)
        if to_hit == 1:
            return 0
        to_hit_modifier = attacker.base_attack_bonus() + modifier(attacker.strength) + hit_bonus_for_size(attacker.size)
        if to_hit == 20 or (defender.effective_armor_class() < (to_hit + to_hit_modifier)):
            # defender was hit
            if to_hit >= self.critical:
                crit_hit = rollndx(1, 20)  # change this, multipliers don't exactly multiply, they give extra damage rolls
                if crit_hit == 20 or (defender.effective_armor_class() < (crit_hit + to_hit_modifier)):
                    base_damage = base_damage + self.critical_damage(damage_modifier)

        return base_damage


class MediumLongsword35(MeleeWeapon35):

    def __init__(self):
        super().__init__(critical = 19, critical_damage_multiplier = 2,
                         weapon_type = "Longsword", weapon_id=uuid.uuid4().int,
                         dice_count = 1, dice_size = 8,
                         weight = 4, cost=15)

    def get_attack(self, attacker, defender):
        base_damage = self.__calculate_basic_attack__(attacker, defender)
        if base_damage > 0:
            damage = (("slashing", base_damage),)
            return SuccessfulAttack(damage, attacker, defender)
        return



class Falchion35(MeleeWeapon35):

    def __init__(self):
        super().__init__(critical = 18, critical_damage_multiplier = 2,
                         weapon_type = "Falchion", weapon_id=uuid.uuid4().int,
                         dice_count = 2, dice_size = 4,
                         weight = 8, cost=75)

    def get_attack(self, attacker, defender):
        base_damage = self.__calculate_basic_attack__(attacker, defender)
        if base_damage > 0:
            damage = (("slashing", base_damage),)
            return SuccessfulAttack(damage, attacker, defender)
        return


class Scimitar35(MeleeWeapon35):

    def __init__(self):
        super().__init__(critical=18, critical_damage_multiplier=2,
                         weapon_type="Scimitar", weapon_id=uuid.uuid4().int,
                         dice_count=2, dice_size=4,
                         weight=8, cost=75)

    def get_attack(self, attacker, defender):
        base_damage = self.__calculate_basic_attack__(attacker, defender)
        if base_damage > 0:
            damage = (("slashing", base_damage),)
            return SuccessfulAttack(damage, attacker, defender)
        return


class BastardSword35(MeleeWeapon35):

    def __init__(self):
        super().__init__(critical=19, critical_damage_multiplier=2,
                         weapon_type="BastardSword", weapon_id=uuid.uuid4().int,
                         dice_count=1, dice_size=10,
                         weight=6, cost=35)

    def get_attack(self, attacker, defender):
        base_damage = self.__calculate_basic_attack__(attacker, defender)
        if base_damage > 0:
            damage = (("slashing", base_damage),)
            return SuccessfulAttack(damage, attacker, defender)
        return


class WarHammer35(MeleeWeapon35):

    def __init__(self):
        super().__init__(critical=20, critical_damage_multiplier=3,
                         weapon_type="Warhammer", weapon_id=uuid.uuid4().int,
                         dice_count=1, dice_size=8,
                         weight=5, cost=12)

    def get_attack(self, attacker, defender):
        base_damage = self.__calculate_basic_attack__(attacker, defender)
        if base_damage > 0:
            damage = (("bludgeoning", base_damage),)
            return SuccessfulAttack(damage, attacker, defender)
        return


def rollndx(count=1, sides=6, remove_lowest=False):
    if remove_lowest:
        scores = [random.randint(1,sides) for x in range(count)]
        smallest = min(scores)
        return sum(scores) - smallest
    else:
        return sum(random.randint(1,sides) for x in range(count))

def modifier(score):
    return floor(score/2) - 5  #Note round doesn't work in python3 - because it uses bankers rounding


class Character(object):


    def __init__(self, base_character, strength, dexterity, constitution, intelligence, wisdom, charisma, max_hit_points, size, additional_languages, race):
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma
        self.levels = []
        self.skills = []
        self.equipment=[]
        self.weapons = []
        self.armor = []
        self.max_hit_points = max_hit_points
        self.hit_points = self.max_hit_points #start off full
        self.size= size
        self.languages = ["common"] + additional_languages
        self.base_initiative_bonus = 0
        self.base_character = base_character
        self.race = race

    def initiative_bonus(self):
        return self.base_initiative_bonus + modifier(self.dexterity)

    @staticmethod
    def get_combat_stat_columns():
        return ("race", "base_strength", "base_dexterity", "base_constitution",
                "base_intelligence", "base_wisdom", "base_charisma",
                "strength", "dexterity", "constitution",
                "intelligence", "wisdom", "charisma","weapon_type", "critical", "critical_damage_multiplier",
                "initiative_bonus", "hit_points", "max_hit_points", "effective_hit_points", "effective_armor_class")
    
    def get_combat_stats(self):
        return [self.race, self.base_character.strength, self.base_character.dexterity, self.base_character.constitution,
                self.base_character.intelligence, self.base_character.wisdom, self.base_character.charisma,
                self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma,
                self.weapons[0].weapon_type, self.weapons[0].critical, self.weapons[0].critical_damage_multiplier,
                self.initiative_bonus(), self.hit_points, self.max_hit_points, self.effective_hit_points(), self.effective_armor_class()]

    def effective_armor_class(self):
        """10 + armor bonus + shield bonus + Dexterity modifier + size modifier"""
        if self.armor:
            dex_limit = min(a.max_dex_bonus for a in self.armor)
            dex_bonus = min(dex_limit, modifier(self.dexterity))
        else:
            dex_bonus = modifier(self.dexterity)
        return 10 + dex_bonus + \
               hit_bonus_for_size(self.size) + \
               self.armor_bonus() + self.shield_bonus()

    def wear_armor(self, armor):
        """For now assumes that you haven't added too much!
        This needs to be adjusted to allow only one type of armor
        and one shield"""
        self.armor.append(armor)

    def armor_bonus(self):
        return sum(a.armor_bonus for a in self.armor)

    def shield_bonus(self):
        return sum(a.shield_bonus for a in self.armor)

    def effective_hit_points(self):
        res = self.hit_points + modifier(self.constitution)
        return max(res, -10)

    def __str__(self):
        return """****************************
Strength: {strength}
Dexterity: {dexterity}
Constitution: {constitution}
Intelligence: {intelligence}
Wisdom: {wisdom}
Charisma: {charisma}
Effective hit points: {hitpoints}
""".format(strength = self.strength,
                               dexterity=self.dexterity,
                               constitution = self.constitution,
                               intelligence = self.intelligence,
                               wisdom = self.wisdom,
                               charisma = self.charisma,
                               hitpoints = self.effective_hit_points())

    def apply_damage_reduction(self, damage):
        #not implemented properly yet - just sum all the attack components
        return sum(dmg for attack_type, dmg in damage)

    def base_attack_bonus(self):
        #Todo - implement this
        return 0

    def defend_against_attack(self, attack):
        #By the time you get here, the attack is known to be successful or is None,
        # but might be reduced by damage reduction, or
        #perhaps avoided by reflexes for some attack types.
        if attack:
            self.hit_points = self.hit_points - self.apply_damage_reduction(attack.damage())
        #each damage type must be placed together - that is, you can't have two slashing damages
        return self
        #adjust hitpoints and any other items that are affected by the attack

    def is_conscious(self):
        return self.effective_hit_points() > 0

    def is_alive(self):
        return self.effective_hit_points() > -10

    def is_dead(self):
        return self.effective_hit_points() <= -10

    def add_weapon_to_inventory(self, weapon):
        self.weapons.append(weapon)

    def drop_weapon_from_inventory(self, weapon):
        self.weapons = [w for w in self.weapons if w != weapon]

    def to_hit(self):
        return 10

class HumanCharacter(Character):

    def __init__(self, base_character, extra_language):
        super().__init__(base_character, base_character.strength + 1, base_character.dexterity + 1, base_character.constitution + 1,
                         base_character.intelligence + 1, base_character.wisdom + 1, base_character.charisma + 1,
                         max_hit_points= 40,
                         size="medium", additional_languages= [extra_language], race = "Human")
        #How do I get to modify the strength but pass through to the inherited constructor

        self.walk_speed = 30
        self.languages = ["common"]
        self.size = "medium"

    def __stats__(self):
        return

class HalfOrcCharacter(Character):

    def __init__(self, base_character):
        super().__init__(base_character, base_character.strength + 2, base_character.dexterity, base_character.constitution + 1,
                         base_character.intelligence, base_character.wisdom, base_character.charisma,
                         max_hit_points= 40,
                         size="medium", additional_languages= ['orcish'], race = "HalfOrc")
        self.languages = ["common", "orcish"]
        self.darkvision = 60
        self.walk_speed = 30
        self.relentless_endurance = True #If dropped to 0 hitpoints but not killed outright, can drop to 1 instead (use again
                                         #after a long rest - TODO not implemented yet!
        self.savage_attack = True #add extra damage dice to the extra damage due to critical
                                  #TODO - not implemented yet!


def gen_character():
    scores = tuple(rollndx(4,6, True) for x in range(6))

    #could switch around here for a particular class, or decide what class to optimize for, or what class to choose
    scores = {'strength': scores[0], 'dexterity': scores[1], 'constitution': scores[2],
                      'intelligence': scores[3], 'wisdom': scores[4], 'charisma': scores[5]}
    return munch.Munch(scores)


if __name__=="__main__":

    ch1 = gen_character()
    human1 = HumanCharacter(ch1, "dwarvish")
    print( ch1 )
    print(human1)


