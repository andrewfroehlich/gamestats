import random
import math

totalruns = 5000

pairs = {
    1:38,
    4:14,
    9:31,
    21:42,
    28:84,
    51:67,
    71:91,
    80:100,
    17:7,
    54:34,
    62:19,
    64:60,
    87:24,
    93:73,
    95:75,
    98:79
}

totalturns = 0 #sum of all turns, for average
turnlist = [] #list of all turn results for min/max/median
turnfrequency = [0]*300 #count of occurrences per turn number for graphing
mode_turns = 0
mode_count = 0
for run in range(totalruns):
    turns = 0
    position = 0
    while position != 100:
        turns += 1
        roll = random.randint(1,6)
        newposition = position + roll
        if newposition in pairs:
            position = pairs[newposition]
        elif newposition <= 100:
            position = newposition
    turnlist.append(turns)
    totalturns += turns
    turnfrequency[turns] = turnfrequency[turns] + 1
    if turnfrequency[turns] > mode_count:
        mode_turns = turns
        mode_count = turnfrequency[turns]

turnlist.sort()

def turnlist_percentile(perc):
    return turnlist[int(round(len(turnlist)*perc/100.0))]
    
print("Over " + str(totalruns) + " runs:")
print("Minimum: " + str(turnlist[0]))
print("5th Percentile: " + str(turnlist_percentile(5)))
print("25th Percentile: " + str(turnlist_percentile(25)))
print("Mode: " + str(mode_turns) + " (" + str(mode_count) + " occurrences)")
print("Median: " + str(turnlist_percentile(50)))
print("Average: " + str(totalturns/totalruns))
print("75th Percentile: " + str(turnlist_percentile(75)))
print("95th Percentile: " + str(turnlist_percentile(95)))
print("Maximum: " + str(turnlist[totalruns-1]))

print("=========")
print("Occurrence Graph:")
for turnnumber in range(turnlist[0],turnlist[totalruns-1]+1):
    print(str(turnnumber) + ":" + ("x"*turnfrequency[turnnumber]))