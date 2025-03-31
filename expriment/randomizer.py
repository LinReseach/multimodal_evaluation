# Congruent vs Incongruent
# FO-GO
# Primary and Secondary

import itertools
import random
def create_random_trials():
    items = ['speech', 'tablet', 'gesture']
    combinations = list(itertools.combinations(items, 2))
    trials = []
    '''
    for combination in combinations:
        for x in range(2): # Primary and Secondary
            for y in range(2): # Congruent and Incongruent
                for z in range(2): # Direction
                    trials.append({
                        'first_item':combination[0],
                        'second_item':combination[1],
                        #'primary': combination[0] if x == 0 else combination[1],
                        'congruent': y == 0,
                        'direction': 'left' if z == 0 else 'right'
                    })
    '''
    items = []
    for comb in combinations:
        items.append(comb)
        items.append(comb[::-1])
    for round in range(5):
        for item in items:
            for con in range(2):
                for lr in range(2):
                    to_append = {
                            'first_item':item[0],
                            'second_item':item[1],
                            #'primary': combination[0] if x == 0 else combination[1],
                            'congruent': con == 0,
                            'direction': 'left' if lr == 0 else 'right'
                        }
                    #print(to_append)
                    trials.append(to_append)
    random.shuffle(trials)
    return trials
