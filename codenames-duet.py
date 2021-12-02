import random
# Create a 5x5 codenames board with Spies and Assassins for a 1-player game
board = [['.' for i in range(5)] for j in range(5)]
def placeMarkers(markerChar, count):
    for x in range(count):
        while True:
            cur_x = random.randint(0,4)
            cur_y = random.randint(0,4)
            if board[cur_x][cur_y] == '.':
                break
        board[cur_x][cur_y] = markerChar
placeMarkers('S',9)
placeMarkers('A',3)
for i in board:
	print(" " + " ".join(i))