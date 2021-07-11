
import munch
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from  dnd.util import *
from dnd.combat import battle, get_win_probability_from_simulation
from random import randint, choice
import tensorflow as tf
import copy
import matplotlib.pyplot as plt

def gen_character():
    scores = tuple(rollndx(4,6, True) for x in range(6))

    #could switch around here for a particular class, or decide what class to optimize for, or what class to choose
    scores = {'strength': scores[0], 'dexterity': scores[1], 'constitution': scores[2],
                      'intelligence': scores[3], 'wisdom': scores[4], 'charisma': scores[5]}
    return munch.Munch(scores)

def generate_random_character():
    base = gen_character()
    chartype = randint(0 ,1)
    if chartype == 0:
        res = HumanCharacter(base, "Dwarvish")
    elif chartype == 1:
        res = HalfOrcCharacter(base)
    set_max_hitpoints(res, randint(20 ,60))
    weapon = choice(weapons35)
    res.add_weapon_to_inventory(weapon)
    return res


non_numeric_cols=["race", "weapon_type"]

def get_single_character_scaler():
    chars = [generate_random_character().get_combat_stats() for char in range(10000)]
    df = pd.DataFrame(chars, columns=Character.get_combat_stat_columns())
    df_non_numeric = df[["race", "weapon_type"]]
    df_numeric = df.drop(non_numeric_cols, axis=1)
    scaler = StandardScaler()
    scaler.fit(df_numeric)
    return scaler

def full_char_data(charlist, scaler):

    """Return the character, the unscaled data and the scaled data along with the one_hot encodings"""
    df = pd.DataFrame((char.get_combat_stats() for char in charlist), columns = Character.get_combat_stat_columns())
    df_non_numeric = df[["race", "weapon_type"]]
    dfn = df.drop(["race", "weapon_type"], axis=1)
    dfs = pd.DataFrame(scaler.transform(dfn), columns=dfn.columns)

    def encode_onehot(column, categories, prefix):
        encoder = OneHotEncoder(categories=[categories], sparse=False)
        cols = [f"{prefix}_is_{category}" for category in categories]
        res = pd.DataFrame(encoder.fit_transform(column), columns=cols)
        return res

    race_cols = encode_onehot(df_non_numeric[['race']],categories=races, prefix="")
    weapon_cols = encode_onehot(df_non_numeric[["weapon_type"]], categories=weapon_types_35, prefix="")
    result = pd.concat([dfs, race_cols, weapon_cols], axis=1)
    return (result, df)

def battle_source_data(charlist1, charlist2, scaler):
    """In order to keep everything together, this function returns the prepared scaled data along with
    the original lists of characters. The intent is that this will now be used
    for both the simulation output and the machine learning data set"""
    scaled_1, df1 = full_char_data(charlist1, scaler)
    scaled_2, df2 = full_char_data(charlist2, scaler)
    scaled_1.columns = [f"char_1_{col}" for col in scaled_1.columns]
    scaled_2.columns = [f"char_2_{col}" for col in scaled_2.columns]
    x_df = pd.concat([scaled_1, scaled_2], axis=1)
    return x_df

def battle_result_data(charlist1, charlist2):
    results = [battle(copy.deepcopy(char1), copy.deepcopy(char2)) for char1, char2 in zip(charlist1, charlist2)]
    res = [(2 - x[0], x[0]-1, x[0], x[1]) for x in results]
    y_df = pd.DataFrame(res, columns=["char1_won", "char2_won", "winner", "remaining_hp"])
    return y_df

def build_model_1():
    """The level of complexity on these layers doesn't seem to have improved much over a 2 layer network,
    However I'm not sure how accurate the simulation numbers are - I have to see how stable they are for
    two give characters
    This model estimates a probability that exceeds 1 :-(
    I need to work out how to build in a softmax layer"""
    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=(52,)),
        tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

def build_softmax_model():
    model = tf.keras.models.Sequential([
        tf.keras.layers.InputLayer(input_shape=(52,)),
        tf.keras.layers.Dense(100, activation='relu'),
        tf.keras.layers.Dense(10, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')])
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def get_source_data(scaler, batch_size=10000):
    charlist1 = [generate_random_character() for i in range(batch_size)]
    charlist2 = [generate_random_character() for i in range(batch_size)]
    x_df = battle_source_data(charlist1, charlist2, scaler)
    y_df = battle_result_data(charlist1, charlist2)
    return charlist1, charlist2, x_df, y_df

def test_softmax():
    def train_iteration(scaler, model):
        charlist1, charlist2, x_df, y_df = get_source_data(scaler, 10000)
        y = y_df[["char1_won", "char2_won"]]
        model.fit(x_df.to_numpy(), y.to_numpy(), epochs=20)

    model = build_softmax_model()

    scaler = get_single_character_scaler()
    for i in range(4):
        train_iteration(scaler, model)
        print(model.history)

    testcharlist1, testcharlist2, test_x, test_y = get_source_data(scaler, 100)
    test_y_model = model.predict(test_x.to_numpy())

    sim_result = [get_win_probability_from_simulation(ch1, ch2, 1000) for ch1, ch2 in zip(testcharlist1, testcharlist2)]
    result = pd.concat([ pd.DataFrame(test_y_model), pd.DataFrame(sim_result), pd.DataFrame(test_y),], axis=1)

    result.columns=[ "model_pct_chance_for_char1", "model_pct_chance_for_char2", "sim_pct_chance_for_char1", "sim_pct_chance_for_char2", "char1_won", "char2_won", "winner", "remaining_hp",]

    return result

def test(rows_per_batch=10000, batches=10, epochs = 20, rows_of_test_data = 100, simulation_iterations=1000):

    def train_iteration(scaler, model):
        charlist1, charlist2, x_df, y_df = get_source_data(scaler, rows_per_batch)
        y = y_df[["char1_won"]]
        model.fit(x_df.to_numpy(), y.to_numpy(), epochs=epochs)

    model = build_model_1()

    scaler = get_single_character_scaler()
    for i in range(batches):
        train_iteration(scaler, model)
        print(model.history)

    testcharlist1, testcharlist2, test_x, test_y = get_source_data(scaler, rows_of_test_data)
    test_y_model = model.predict(test_x.to_numpy())

    sim_result = [get_win_probability_from_simulation(ch1, ch2, simulation_iterations) for ch1, ch2 in zip(testcharlist1, testcharlist2)]
    result = pd.concat([ pd.DataFrame(test_y_model), pd.DataFrame(sim_result), pd.DataFrame(test_y),], axis=1)

    result.columns=[ "model_pct_chance_for_char1", "sim_pct_chance_for_char1", "sim_pct_chance_for_char2", "char1_won", "char2_won", "winner", "remaining_hp",]

    return result

def old_test():
    scaler = get_single_character_scaler()
    char = generate_random_character()
    df = pd.DataFrame([char.get_combat_stats()], columns=Character.get_combat_stat_columns())
    df_non_numeric = df[["race", "weapon_type"]]

    df = df.drop(non_numeric_cols, axis=1)

    dfs = scaler.transform(df, copy=True)
    charlist1 = [generate_random_character() for i in range(100)]
    charlist2 = [generate_random_character() for i in range(100)]

    test1 = full_char_data(charlist1, scaler)

    x_df = battle_source_data(charlist1, charlist2, scaler)
    y_df = battle_result_data(charlist1, charlist2)
    print(y_df)

if __name__=="__main__":
    result= test(rows_per_batch=100000, batches=3, epochs = 20, rows_of_test_data = 100, simulation_iterations=1000)
    print(result[["model_pct_chance_for_char1", "sim_pct_chance_for_char1"]])
