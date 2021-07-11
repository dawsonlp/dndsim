#!/usr/bin/env python3

import copy
import pandas as pd
import numpy as np
import pickle
from dnd.combat import *
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import tensorflow as tf

from dnd.analytics_source import BattleDataGeneration

def get_dataframe_for_prediction(ch1, ch2):
    stats1 = ch1.get_combat_stats()
    stats2 = ch2.get_combat_stats()
    res = stats1 + stats2
    return res

def get_normalization_coefficents(srcdf):
    """Returns a tuple of dataframes containing the min and max in positions 0 and 1"""
    return srcdf.min(), srcdf.max()



def get_independent_vars(srcdf, scaler=None):


    def encode_onehot(column, categories, prefix):
        encoder = OneHotEncoder(categories=[categories], sparse=False)
        cols = [f"{prefix}_is_{category}" for category in categories]
        res = pd.DataFrame(encoder.fit_transform(column), columns=cols)
        return res

    weapontypes=[w.weapon_type for w in BattleDataGeneration().weapons] #Yuck

    r1 = encode_onehot(srcdf[['char1_race']],categories=["Human", "HalfOrc"], prefix="char1")
    r2 = encode_onehot(srcdf[['char2_race']],categories=["Human", "HalfOrc"], prefix="char2")
    w1 = encode_onehot(srcdf[['char1_weapon_type']], categories=weapontypes, prefix="char1")
    w2 = encode_onehot(srcdf[["char2_weapon_type"]], categories=weapontypes, prefix="char2")
    xdf = srcdf.drop(columns=[
                              "char1_race", "char2_race",
                              "char1_weapon_type", "char2_weapon_type", "char1_strength",
                              'char1_dexterity', 'char1_constitution', 'char1_intelligence',
                              'char1_wisdom', 'char1_charisma',
                              'char2_strength', 'char2_dexterity', 'char2_constitution',
                              'char2_intelligence', 'char2_wisdom', 'char2_charisma'
                              ])
    #Really need to scale the variables here!
    #However, for symmetry, the same scaling should be applied to both characters! Need to do one at a time
    #And then add the two - but this is structured poorly for this right now.

    # Idea: provide a character generator, a scaler and a character encoder and decoder, and a battle combiner separetly:
    # Then
    # so need a get_independent_vars variant for just a single character

    if scaler == None:
        scaler = StandardScaler()
        scaler.fit(xdf)
    scaled_xdf = pd.DataFrame(scaler.transform(xdf), columns=xdf.columns)

    xvars = pd.concat([r1, r2, w1, w2, scaled_xdf], axis=1)
    return xvars, scaler


def get_data(set_size = 100000, scaler=None):
    gen = BattleDataGeneration()
    cols_x, cols_y = gen.get_headings()
    dta_x, dta_y = zip(*gen.run_battle_data_1(set_size))
    dfx = pd.DataFrame(data=dta_x, columns=cols_x)
    dfx1, scaler = get_independent_vars(dfx, scaler) #Will need the scaler later

    dfy = pd.DataFrame(data=dta_y, columns=cols_y)
    return dfx1, dfy, scaler

def get_datum(char1, char2, scaler):
    gen = BattleDataGeneration()
    cols_x, cols_y = gen.get_headings()
    dta_x = char1.get_combat_stats() + char2.get_combat_stats()
    df = pd.DataFrame(data = [dta_x], columns = cols_x)
    res, scaler = get_independent_vars(df, scaler)
    return res

def get_single_character_datum(char1, scaler):


def show_single_random_fight_and_compare_percentage_chance_vs_neural_net(trained_model, scaler):

    ch1 = HumanCharacter(gen_character(), "dwarvish")
    sword1 = MediumLongsword35()
    ch1.add_weapon_to_inventory(sword1)
    ch2 = HalfOrcCharacter(gen_character())
    sword2 = MediumLongsword35()
    ch2.add_weapon_to_inventory(sword2)
    results = get_win_probability_from_simulation(ch1, ch2)
    results2 = get_win_probability_from_simulation(ch1, ch2)
    x_vals = get_datum(ch1, ch2, scaler)
    neural_result = trained_model.predict(x_vals.to_numpy())
    print(f"Result from simulation {results[0]}, then {results2[0]}\tNeural result: {neural_result[0][0]}\tDifference: {results[0] - neural_result[0][0]}")
    return {"simulation": results[0],"model": neural_result[0][0]}



def build_model_1():
    """The level of complexity on these layers doesn't seem to have improved much over a 2 layer network,
    However I'm not sure how accurate the simulation numbers are - I have to see how stable they are for
    two give characters
    This model estimates a probability that exceeds 1 :-( 
    I need to work out how to build in a softmax layer"""
    model = tf.keras.models.Sequential([
        tf.keras.layers.Input(shape=(40,)),
        tf.keras.layers.Dense(20, activation='sigmoid'),
        tf.keras.layers.Dense(5, activation='sigmoid'),
        tf.keras.layers.Dense(1, activation='sigmoid')])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model
   



def full_test():
    x_train, y_train, scaler = get_data(100000)
    x_test, y_test, dontuse_this_scaler = get_data(10000, scaler)

    model=create_model()
    model.fit(x_train.to_numpy(), (y_train[["char1_won"]]).to_numpy(), epochs=10)

    #Adding additional training sets doesn't appear to help! That is surprising.
    #x_train, y_train, dontuse_this_scaler = get_data(200000, scaler)
    #model.fit(x_train.to_numpy(), (y_train[["char1_won"]]).to_numpy(), epochs=10)

    model.evaluate(x_test.to_numpy(), (y_test[["char1_won"]]).to_numpy(), verbose=2)
    model.save("dnd_model")
    pickle.dump(scaler, open("scaler.pickle", "wb"))
    show_single_random_fight_and_compare_percentage_chance_vs_neural_net(model, scaler)

def single_test():
    model=tf.keras.models.load_model("dnd_model")
    scaler = pickle.load(open("scaler.pickle", "rb"))
    res = [show_single_random_fight_and_compare_percentage_chance_vs_neural_net(model, scaler) for x in range(10)]
    results = pd.DataFrame(res)
    print(results)



if __name__ == "__main__":

    #full_test()
    single_test()
