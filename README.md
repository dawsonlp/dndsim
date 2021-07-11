# dndsim
Provide test data for aws infrastructure

generating a character:- we need a standard scaler to apply to all characters

The class BattleDataGeneration has a generate_random_character, 

TODO:
1. Break scaling out to a separate function - generate a bunch of characters and a scaler 
   just for one character. Then combine the two scaled datasets, so the same scaling is
   applied in both directions rather than having a random difference.
2. reformat the output to make it easier to read
3. Run a simulation multiple times and get a percentage estimate from the actual loop/source dataset
   This should lead to a better estimate with less jitter for less frequently observed data
4. Work on the accuracy statistic - not clear how to interpret it since