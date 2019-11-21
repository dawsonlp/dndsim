#!/usr/bin/env python3

import tensorflow as tf
import pandas as pd
from  dnd.analytics_source import BattleDataGeneration
from itertools import chain

def get_machine_learning_optimized_df(srcdf):
    #Need also to know what the divisors are for the items
    r1 = pd.get_dummies(srcdf['char1_race'], prefix = "char1")
    r2 = pd.get_dummies(srcdf["char2_race"], prefix = "char2")
    w1 = pd.get_dummies(srcdf['char1_weapon_type'], prefix = "char1")
    w2 = pd.get_dummies(srcdf["char2_weapon_type"], prefix = "char2")
    yvars = srcdf[["char1_won", "char2_won", "char1_hp_left", "char2_hp_left"]]
    xdf = srcdf.drop(columns=["char1_won", "char2_won", "char1_hp_left", "char2_hp_left",
                              "char1_race", "char2_race",
                              "char1_weapon_type", "char2_weapon_type",
                              'char1_dexterity', 'char1_constitution', 'char1_intelligence',
                              'char1_wisdom', 'char1_charisma', 'char1_critical',
                              'char1_critical_damage_multiplier',
                              'char2_strength', 'char2_dexterity', 'char2_constitution',
                              'char2_intelligence', 'char2_wisdom', 'char2_charisma',
                              'char2_critical', 'char2_critical_damage_multiplier'
                              ])
    xdfnorm = (xdf-xdf.min())/(xdf.max()-xdf.min())
    xvars = pd.concat([r1, r2, w1, w2, xdfnorm], axis = 1)
    return xvars, yvars

def get_data(training_set_size = 100000, test_set_size = 10000):
    gen = BattleDataGeneration()
    cols = gen.show_headings()
    dta = gen.run_battle_data_1(training_set_size)
    df = pd.DataFrame(data=dta, columns=cols)
    dfx, dfy = get_machine_learning_optimized_df(df)
    testdata = gen.run_battle_data_1(test_set_size)
    testdfx, testdfy = get_machine_learning_optimized_df(pd.DataFrame(data = testdata, columns=cols))
    return (dfx, dfy), (testdfx, testdfy)


if __name__ == "__main__":
    (x_train, y_train), (x_test, y_test) = get_data(10000,1000)

    print(x_train.describe())
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(400, activation='relu'),
        tf.keras.layers.Dense(80, activation='relu'),
        tf.keras.layers.Dense(80, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


    model.fit(x_train.to_numpy(), (y_train[["char1_won"]]).to_numpy(), epochs=5)

    model.evaluate(x_test.to_numpy(), (y_test[["char1_won"]]).to_numpy(), verbose=2)


    """
    Problem:- when I run this model, I end up getting accuracy of very close to 50%
    This is as good as a coin toss, and not what I was expecting!
    
    I think I need to get the normalization eqn out so I can see how a particular case runs
    
    1. Need to have normalization numbers available to apply to test dataset and to any items I come up with to test
    2. Need to generate a real estimate of probability to compare results with - the test may be broken (?)
    3. How to run this effectively - probably need to do in jupyter? or ipython, how could i run in pycharm interactively?
    
    Run training
    run simulation on a particular character pair and generate a probability estimate 
    Compare to the output of the output unit.
    
    """
