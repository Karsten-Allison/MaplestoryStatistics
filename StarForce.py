import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import statistics

SuccessRates = [0.95, 0.9, 0.85, 0.85, 0.80, 0.75, 0.70, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.3, 0.3, 0.3, 0.3,
             0.3, 0.3, 0.3, 0.03, 0.02, 0.01]
FailureRates = [[1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],
                [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0], [1, 0, 0],
                [1, 0, 0], [0, 1, 0], [0, 0.99, 0.01], [0, 0.98, 0.02], [0, 0.98, 0.02],
                [0.97, 0, 0.03], [0, 0.97, 0.03], [0, 0.97, 0.03], [0, 0.96, 0.04], [0, 0.96, 0.04],
                [0.90, 0, 0.1], [0, 0.9, 0.1], [0, 0.8, 0.2], [0, 0.7, 0.30], [0, 0.6, 0.4]]

StarCatchArray = [False for i in range(25)]
SafeGuardArray = [False for i in range(25)]
# We represent the on/off state for starcatching/safeguarding with an array of booleans.


def EnhancedRates(BaseRatesArray, StarCatchBooleanArray, FiveTenFifteen):
    for i in range(len(StarCatchBooleanArray)):
        if StarCatchBooleanArray[i] == True:
            BaseRatesArray[i] *= 1.05
    if FiveTenFifteen:
        BaseRatesArray[5] = 1
        BaseRatesArray[10] = 1
        BaseRatesArray[15] = 1
    return BaseRatesArray
	# We can create a new array with the "EnchancedRates" based on which enhancement level stars are caught,
	# and if theres a special success rate event being ran at the time.


def NoBoom(FailureRatesArray, SafeGuardBooleanArray):
    for i in range(len(SafeGuardBooleanArray)):
        if SafeGuardBooleanArray[i] == True:
            if FailureRatesArray[i][0] == 0:
                FailureRatesArray[i][1] = 1
                FailureRatesArray[i][2] = 0
            else:
                FailureRatesArray[i][0] = 1
                FailureRatesArray[i][2] = 0
    return FailureRatesArray
	# We can create a new "FailureRates" array based on which enhancement levels are safeguarded.

def SimulateToStar(RatesArray, FailureArray, SafeGuardArray, StartStar, EndStar, ItemLevel, CopyCost, DiscountEvent):
    CurrentStar = StartStar
    ChanceTime = 0
    BoomCount = 0
    MesoCost = 0

    while CurrentStar < EndStar:
        if CurrentStar < 10:
            MesoCost += (((lambda: 0, lambda: 100)[SafeGuardArray[CurrentStar]]() + (lambda: 100, lambda: 70)[DiscountEvent]()
                         ) * round((pow(ItemLevel, 3) * pow(CurrentStar + 1, 1)) / (2500) + 10))     
        elif CurrentStar < 15:
            MesoCost += (((lambda: 0, lambda: 100)[SafeGuardArray[CurrentStar]]() + (lambda: 100, lambda: 70)[DiscountEvent]()
                         ) * round((pow(ItemLevel, 3) * pow(CurrentStar + 1, 2.7)) / (40000) + 10))
        else:
            MesoCost += (((lambda: 0, lambda: 100)[SafeGuardArray[CurrentStar]]() + (lambda: 100, lambda: 70)[DiscountEvent]()
                         ) * round((pow(ItemLevel, 3) * pow(CurrentStar + 1, 2.7)) / (20000) + 10))
						 # ((0 if not safeguarded OR 100 if safeguarded) + (100 if no event discount OR 70 if event discount))
                         # TIMES Round(((EquipLevel^3)*(CurrentStar+1)^2.7)/(20000)+10)
		# Baseprice is increased by 100 if SafeGuardArray at the CurrentStar index is True
        # The BasePrice is then either 100 or 70 depending on if DiscountEvent is True
        # Then multiplied by the given formula above.
        
		
        if ChanceTime == 2:
            ChanceTime = 0
            CurrentStar += 1
			# If two consecutive failures happen, go up a star and reset ChanceTime count
        elif random.random() <= RatesArray[CurrentStar]:
            ChanceTime = 0
            CurrentStar += 1
			# Else if we sucessfully hit the enchancment, go up a star and reset ChanceTime count
        else: # Else if we fail the enchancement 
            if random.random() <= FailureArray[CurrentStar][0]:
                ChanceTime = 0
				# If we hit the stay probability, reset ChanceTime count
            elif random.random() <= FailureArray[CurrentStar][1]:
                ChanceTime += 1
                CurrentStar -= 1
				# Else if we hit the drop probability, drop a star and increment ChanceTime count
            else:
                ChanceTime = 0
                BoomCount += 1
                MesoCost += CopyCost
                CurrentStar = 12
				# Else destroy the item, resetting it to 12 and adding the "CopyCost" to the total "MesoCost"
    return [MesoCost, BoomCount]

def RunSimulations(RatesArray, FailureArray, SafeGuardArray, StartStar, EndStar, ItemLevel, CopyCost, DiscountEvent, Trials):
    SimulationsArray = []
    for i in range(Trials):
        Simulation = SimulateToStar(RatesArray, FailureArray, SafeGuardArray, StartStar, EndStar, ItemLevel, CopyCost, DiscountEvent)
        SimulationsArray.append([Simulation[0],Simulation[1]])
    return SimulationsArray

#------------------------------------------------------

def PlotMesoCostSimulation(SimulationArray):
    OurSimulation = list(zip(*SimulationArray))

    costs = list(map(lambda value: round(value / 1000000000, 1), OurSimulation[0]))
	#Create 15 bins to contain similiar data values, ranging from 0 to the maximum.
    hist, bins = np.histogram(costs, bins=15, range=(0, max(costs)))
    plt.bar(bins[:-1], hist, width=bins[1]-bins[0], edgecolor='black')

    plt.xlabel('Meso Cost (Billions)')
    plt.ylabel('Frequency')
    plt.title('Expected Meso Cost')

    plt.show()
    
def PlotBoomCountSimulation(SimulationArray):
    OurSimulation = list(zip(*SimulationArray))
    
    hist, bins = np.histogram(OurSimulation[1], bins=15, range=(0, max(OurSimulation[1])))
	 #Create 15 bins to contain similiar data values, ranging from 0 to the maximum.
    plt.bar(bins[:-1], hist, width=bins[1]-bins[0], edgecolor='black')

    plt.xlabel('Booms')
    plt.ylabel('Frequency')
    plt.title('Expected Booms')

    plt.show()
    
def SimulationStatistics(SimulationArray):
    OurSimulation = list(zip(*SimulationArray))
    print('Average Booms: '+str(statistics.mean(OurSimulation[1])))
    print('Median Booms:  '+str(statistics.median(OurSimulation[1])))
    print('Average Meso Cost: '+f"{round(statistics.mean(OurSimulation[0])):,}")
    print('Median Meso Cost : '+f"{round(statistics.median(OurSimulation[0])):,}")
    print('Your 5 best trials:')
    print(sorted(SimulationArray)[:5])
    print('Your 5 worst trials:')
    print((sorted(SimulationArray)[:-6:-1]))

# ---------------------------------------

for i in range(17, 22):
    StarCatchArray[i] = True

for i in range(12, 17):
    SafeGuardArray[i] = False

OriginalSimulation = RunSimulations(EnhancedRates(SuccessRates, StarCatchArray, FiveTenFifteen=False), NoBoom(FailureRates, SafeGuardArray), 
                   SafeGuardArray, 12, 22, ItemLevel=150, CopyCost=0, DiscountEvent=False, Trials=1000)

#-----------------------------------------

SimulationStatistics(OriginalSimulation)
PlotMesoCostSimulation(OriginalSimulation)
PlotBoomCountSimulation(OriginalSimulation)