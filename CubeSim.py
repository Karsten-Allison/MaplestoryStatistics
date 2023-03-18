import os
import json
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import statistics

root = os.path.abspath('.')
root += '/lineweights/'


def loadJson(name):
    full_path = root + name
    json_file = open(full_path, 'r')
    cfg = json.load(json_file)
    json_file.close()
    return cfg


LegLines, LegProb = zip(*loadJson('LegendaryAccessory.json').items())
LegProb = list(map(float, LegProb))
UniqueLines, UniqueProb = zip(*loadJson('UniqueAccessory.json').items())
UniqueProb = list(map(float, UniqueProb))


# Loads lines and their probabilities into two seperate lists

def SimulateRoll(LegLinePool, LegProbability, UniqueLinePool, UniqueProbability, PrimeLineChance=0.05):
    LineOne = random.choices(LegLinePool, weights=LegProbability)
    # The first line is always "legendary". So a legendary line is chosen according to the weights.
    if random.random() <= PrimeLineChance:  # The second line can be Legendary
        LineTwo = random.choices(LegLinePool, weights=LegProbability)
    else:  # If not a unique line is chosen.
        LineTwo = random.choices(UniqueLinePool, weights=UniqueProbability)
    if random.random() <= PrimeLineChance:  # The third line can be Legendary
        LineThree = random.choices(LegLinePool, weights=LegProbability)
    else:  # If not a unique line is chosen.
        LineThree = random.choices(UniqueLinePool, weights=UniqueProbability)
    return LineOne + LineTwo + LineThree


def EvaluateRoll(currentroll, main_stat="STR", percent_value=8.5, all_stat_value=9, att_value=2.5, matt_value=0,
                 level=270):
    results = []
    for roll in currentroll:  # splits apart a "roll" as simulated in SimulateRoll()
        parts = roll.split(":")
        stat = parts[0].strip()
        bonus = parts[1].strip()
        # The line is split and stripped into two parts. One containing the stat it references.
        # and the second one containing the bonus it references

        if stat[0:3] == main_stat:  # If the first 3 letters in line match the "main_stat"
            if "%" in bonus:  # if its a %stat line
                results.append(int(bonus[:-1]) * percent_value)
            elif "per 10" in stat:  # if its a stat per 10 levels line
                results.append(int(bonus) * math.floor(level / 10))
            else:  # else its a flat bonus
                results.append(int(bonus))
        elif "All Stats" in stat:  # if its a %all stat line
            results.append(int(bonus[:-1]) * all_stat_value)
        elif "ATT" in stat[0:3]:  # if its an ATT line
            results.append(int(bonus) * att_value)
        elif "Magic" in stat:  # if its a Magic ATT line
            results.append(int(bonus) * matt_value)
        else:  # Worth 0 otherwise.
            results.append(0)
    return results


def RunSimulations(LegLinePool, LegProbability, UniqueLinePool, UniqueProbability, MinimumScore=91, Trials=1,
                   PrimeLineChance=0.05, main_stat="STR", percent_value=8.5, all_stat_value=9, att_value=2.5,
                   matt_value=0, level=270):
    if MinimumScore >= percent_value * 19:  # Prevent absurdly large inputs
        return 0

    SimulationArray = []
    for i in range(Trials):  # Does x trials
        num_rolls = 0
        CurrentScore = 0

        while CurrentScore <= MinimumScore:  # Roll until minimum criteria is met.
            CurrentRoll = SimulateRoll(LegLinePool, LegProbability, UniqueLinePool, UniqueProbability, PrimeLineChance)
            CurrentScore = sum(
                EvaluateRoll(CurrentRoll, main_stat, percent_value, all_stat_value, att_value, matt_value, level))
            num_rolls += 1
        SimulationArray.append((CurrentRoll, CurrentScore, num_rolls))  # Append results and continue to next trial.
    return SimulationArray


# ------------------

def PlotCubeSimulation(SimulationArray):
    OurSimulation = list(zip(*SimulationArray))

    hist, bins = np.histogram(OurSimulation[2], bins=15, range=(0, max(OurSimulation[2])))
    # Create 15 bins to contain similiar data values, ranging from 0 to the maximum.
    plt.bar(bins[:-1], hist, width=bins[1] - bins[0], edgecolor='black')

    plt.xlabel('Cubes Used')
    plt.ylabel('Frequency')
    plt.title('Expected Cubes')

    plt.show()


def SimulationStatistics(SimulationArray):
    OurSimulation = list(zip(*SimulationArray))
    print('Average Statscore: ' + str(statistics.mean(OurSimulation[1])))
    print('Median Statscore:  ' + str(statistics.median(OurSimulation[1])))
    print('Average Cubes Needed: ' + f"{round(statistics.mean(OurSimulation[2])):,}")
    print('Median Cubes Needed: ' + f"{round(statistics.median(OurSimulation[2])):,}")
    print('Your 2 worst trials:')
    print(sorted(SimulationArray, key=lambda x: x[2])[:-3:-1])
    print('Your 2 best rolls:')
    print((sorted(SimulationArray, key=lambda x: x[1])[:-3:-1]))

# ------------------------------

Simulation = RunSimulations(LegLines, LegProb, UniqueLines, UniqueProb, 92, 1000)

SimulationStatistics(Simulation)

PlotCubeSimulation(Simulation)
