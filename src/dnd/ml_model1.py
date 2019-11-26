#!/usr/bin/env python3

import tensorflow as tf
import pandas as pd
from  dnd.analytics_source import BattleDataGeneration
from itertools import chain

def get_normalization_coefficents(srcdf):
    """Returns a tuple of dataframes containing the min and max in positions 0 and 1"""
    res = srcdf.min(), srcdf.max()
    return res

def get_machine_learning_optimized_df(srcdf, normalization_coefficients = None):
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

    if normalization_coefficients is None:
        normalization_coefficients = get_normalization_coefficents(xdf)
    (min, max) = normalization_coefficients
    xdfnorm = (xdf-min)/(max-min)
    xvars = pd.concat([r1, r2, w1, w2, xdfnorm], axis = 1)
    return xvars, yvars, normalization_coefficients

def get_data(training_set_size = 100000, test_set_size = 10000):
    gen = BattleDataGeneration()
    cols = gen.show_headings()
    dta = gen.run_battle_data_1(training_set_size)
    df = pd.DataFrame(data=dta, columns=cols)
    dfx, dfy, norm = get_machine_learning_optimized_df(df)
    testdata = gen.run_battle_data_1(test_set_size)
    testdfx, testdfy, norm = get_machine_learning_optimized_df(pd.DataFrame(data = testdata, columns=cols), norm)
    return (dfx, dfy), (testdfx, testdfy), norm

def get_single_example():
    pass

def show_example(ex):
    """Show two characters and their chance of a winning
    To test should run multiple bouts between a and b and see how that
    compares to the output of the final layer"""
    pass



if __name__ == "__main__":
    (x_train, y_train), (x_test, y_test), normparams = get_data(100000,10000)

    print(x_train.describe())
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(1000, activation='relu'),
        tf.keras.layers.Dense(400, activation='relu'),
        tf.keras.layers.Dense(40, activation='relu'),
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
    2. Need to generate a real estimate of probability to compare results with - the test may be broken  (?) Fix normalization to see if it fixes the problem
    3. How to run this effectively - probably need to do in jupyter? or ipython, how could i run in pycharm interactively?
       - how to test
       - how to generate particular testcase and see how it is encoded.
       
    HOw do I save the model so I can play with it?
    
    
    Run training
    run simulation on a particular character pair and generate a probability estimate 
    Compare to the output of the output unit.
    
    
    Compare the calculated chance of winning to that predicted by the network. 
    
    How to show the weights in a layer in keras?

----
Plan:
build model
show model : to write - 
show output from one test case - really final weight
run test case manually running a few thousand trials to generate an estimate of the probability of winning.

    """
