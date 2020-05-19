def block(cell):
	return cell != 0

def empty(cell):
	return cell == 0 

def holesboard(board):
	holes = []
	block_in_col = False
	for x in range(len(board[0])):
		for y in range(len(board)):
			if block_in_col and empty(board[y][x]):
				holes.append((x,y))
			elif block(board[y][x]):
				block_in_col = True
		block_in_col = False
	return holes

def totHoles(board):
	return len(holesboard(board))

def totalblockAboveHoles(board):
	c = 0
	for hole_x, hole_y in holesboard(board):
		for y in range(hole_y-1, 0, -1):
			if block(board[y][hole_x]):
				c += 1
			else:
				break
	return c

def gaps(board):
	gaps = []
	sequence = 0 # 0 = no progress, 1 = found block, 2 = found block-gap, 3 = found block-gap-block
	board_copy = []

	# membuat wall menjadi block
	for y in range(len(board)):
		board_copy.append([1] + board[y] + [1])

	# mencari gaps gaps
	for y in range(len(board_copy)):
		for x in range(len(board_copy[0])):
			if sequence == 0 and block(board_copy[y][x]):
				sequence = 1
			elif sequence == 1 and empty(board_copy[y][x]):
				sequence = 2
			elif sequence == 2:
				if block(board_copy[y][x]):
					gaps.append(board_copy[y][x-1])
					sequence = 1
				else:
					sequence = 0

	return len(gaps)	

def height(board):
	for idx, row in enumerate(board):
		for cell in row:
			if block(cell):
				return len(board) - idx-1

def avgHeight(board):
	total_height = 0
	for height, row in enumerate(reversed(board[1:])):
		for cell in row:
			if block(cell):
				total_height += height
	return total_height / numBlock(board)
	
def numBlock(board):
	c = 0
	for row in board:
		for cell in row:
			if block(cell):
				c += 1
	return c
	
