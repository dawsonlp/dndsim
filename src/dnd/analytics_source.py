"""This module runs different scenarios to create datasets for analysis on which weapon/technique
 is best against which opponent, the intent is then to use machine learning to play characters off against one another.

 """

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
        pass

    def generate_random_character(self):

    def battle_data_1(self):
        """generate array with attributes:
        character 1: strength, dexterity, constitution, intelligence, wisdom, charisma, initiative bonus, initial_hitpoints, max_hitpoints,
                     weapon used, final remaining effective hitpoints
        character 2: strength, dexterity
        """
        ch1 = self.generate_random_character()
