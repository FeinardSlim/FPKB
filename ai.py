from tetris import CollisionCheck, COLS, join_matrices, rotate
import heuristic
from collections import namedtuple

Move = namedtuple('Move', ['x_pos', 'rotation', 'result'])

class AI(object):
	def __init__(self, tetris):
		self.tetris = tetris
		self.heuristics = {
			heuristic.totHoles: -81,
			heuristic.totalblockAboveHoles: 556,
			heuristic.gaps: -629,
			heuristic.height: -802,
			heuristic.avgHeight: 993,
			heuristic.numBlock: 281,
		}
		self.instant_play = True

	def boardwithStone(self, x, y, stone):
		return join_matrices(self.tetris.board, stone, (x, y))

	def intersection_point(self, x, stone):
		y = 0
		while not CollisionCheck(self.tetris.board, stone, (x, y)):
			y += 1
		return y - 1

	@staticmethod
	def MaxXposition(stone):
		return COLS - len(stone[0])

	@staticmethod
	def totalRotation(stone):
		stones = [stone]
		while True:
			stone = rotate(stone)
			if stone in stones:
				return len(stones)
			stones.append(stone)

	def utility(self, board):
		return sum([rand(board)*weight for (rand, weight) in self.heuristics.items()])

	def possibleMove(self):
		moves = []
		stone = self.tetris.stone
		for r in range(AI.totalRotation(stone)):
			for x in range(self.MaxXposition(stone)+1):
				y = self.intersection_point(x, stone)
				board = self.boardwithStone(x, y, stone)
				moves.append(Move(x, r, board))
			stone = rotate(stone)
		return moves		

	def bestMove(self):
		return max(self.possibleMove(), key=lambda m: self.utility(m.result))		

	def AIMove(self):
		tetris = self.tetris

		move = self.bestMove()

		tetris.lock.acquire()
		for _ in range(move.rotation):
			tetris.stone = rotate(tetris.stone)
		tetris.move_to(move.x_pos)		
		if self.instant_play:
			tetris.stone_y = self.intersection_point(move.x_pos, tetris.stone)
		tetris.lock.release()
