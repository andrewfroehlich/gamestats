import itertools, random

# CONFIGURATIONS SECTION #
totalruns = 1000 #number of runs to simulate
seconds_per_turn = 5
seconds_per_war = 15
# END CONFIGURATIONS SECTION #


totalturns = 0 #sum of all turns, for average
totaltime = 0 #sum of all time taken
turnlist = [] #list of all turn results for min/max/median
timelist = [] #list of all time results for min/max/median

def getcard(deck, discard):
	if not deck:
		random.shuffle(discard)
		deck = discard
		discard = []
	card = deck.pop()
	if not deck:
		random.shuffle(discard)
		deck = discard
		discard = []
	return card

def remaining1():
	return len(p1)+len(p1discard)
	
def remaining2():
	return len(p2)+len(p2discard)

for run in range(totalruns):
	#shuffle and deal, 11=J, 12=Q, 13=K, 14=A
	deck = list(range(2,15))*4
	random.shuffle(deck)
	p1 = deck[:26]
	p2 = deck[26:]
	p1discard = []
	p2discard = []
	turns = 0
	time = 0
	
	while( remaining1() > 0 and remaining2() > 0 ):
		turns += 1
		time += seconds_per_turn
		card1 = [ getcard(p1,p1discard) ]
		card2 = [ getcard(p2,p2discard) ]
		while(card1[-1] == card2[-1]):
			time += seconds_per_war
			cards_to_burn = min([remaining1(), remaining2(), 4])
			if cards_to_burn == 0:
				break
			for x in range(0,cards_to_burn):
				card1.append(getcard(p1,p1discard))
				card2.append(getcard(p2,p2discard))
		if card1[-1] > card2[-1]:
			p1discard.extend(card1)
			p1discard.extend(card2)
		elif card1[-1] < card2[-1]:
			p2discard.extend(card1)
			p2discard.extend(card2)
		else:
			# Assumes that the player that ran out of cards to do further wars is declared the loser (or a draw)
			break

	turnlist.append(turns)
	timelist.append(time)
	totalturns += turns
	totaltime += time

turnlist.sort()
timelist.sort()

def percentile(perc, item_list):
	return item_list[int(round(len(item_list)*perc/100.0))]
	
def run_stats(item_list, total_count):
	print("Minimum: " + str(item_list[0]))
	print("5th Percentile: " + str(percentile(5, item_list)))
	print("25th Percentile: " + str(percentile(25, item_list)))
	print("Median: " + str(percentile(50, item_list)))
	print("Average: " + str(total_count/totalruns))
	print("75th Percentile: " + str(percentile(75, item_list)))
	print("95th Percentile: " + str(percentile(95, item_list)))
	print("Maximum: " + str(item_list[-1]))
	
print("Over " + str(totalruns) + " runs:")
print("=== Turn Stats ===")
run_stats(turnlist, totalturns)
print("=== Time Stats ===")
run_stats(timelist, totaltime)