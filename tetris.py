from random import randrange
import pygame, sys
from copy import deepcopy
from threading import Lock
import getpass

# Config
CELL_SIZE =	20
COLS = 11
ROWS = 19
MAX_FPS = 60
DROP_TIME = 150
DRAW = True

COLORS = [
	(0,   0, 0  ),
	(255, 85,  85),
	(100, 200, 115),
	(120, 108, 245),
	(255, 140, 50 ),
	(50,  120, 52 ),
	(146, 202, 73 ),
	(150, 161, 218 ),
	(35,  35, 35)
]

Tetris_shape = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]

def rotate(shape):
	return [ [ shape[y][x] for y in range(len(shape)) ] for x in range(len(shape[0])-1, -1, -1) ]

def CollisionCheck(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[cy + off_y][cx + off_x]:
					return True
			except IndexError:
				return True
	return False

def removeLine(board, row):
	del board[row]
	return [[0 for i in range(COLS)]] + board
	
def join_matrices(mat1, mat2, mat2_off):
	mat3 = deepcopy(mat1)
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat3[cy+off_y-1][cx+off_x] += val
	return mat3



def new_board():
	board = [[0 for x in range(COLS)] for y in range(ROWS)]
	board += [[1 for x in range(COLS)]]
	return board

class TetrisApp(object):
	def __init__(self, runner=None):
		self.DROPEVENT = pygame.USEREVENT + 1
		pygame.init()
		pygame.display.set_caption("Tetris")
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		pygame.key.set_repeat(150,150)
		self.width = CELL_SIZE * (COLS+18)
		self.height = CELL_SIZE * ROWS
		self.rlim = CELL_SIZE * COLS
		self.bground_grid = [[ 8 if x%2==y%2 else 0 for x in range(COLS)] for y in range(ROWS)]
		self.font = pygame.font.SysFont("Times New Roman", 18)
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.next_stone = Tetris_shape[randrange(len(Tetris_shape))]

		#initStartPage
		# done = False
		# self.fontMain = pygame.font.SysFont("Comic Sans MS",20)
		# text = self.fontMain.render("Welcome to tetris", True, (255, 255, 255))
		# startParam  = self.fontMain.render("Press anyting to start",True,(255,255,255))
		# clock = pygame.time.Clock()
		# while not done:
		# 	for event in pygame.event.get():
		# 		if event.type == pygame.QUIT:
		# 			done = False
		# 		if event.type == pygame.KEYDOWN:
		# 			done = True
		# 		self.screen.fill((0, 0, 0))
		# 		self.screen.blit(text,(self.width // 3 + 15,self.height // 2 - 20))
		# 		self.screen.blit(startParam,(self.width // 3 + 15,self.height //2 + 10))
		# 		pygame.display.flip()
		# 		clock.tick(60)

		self.gameover = False
		self.runner = runner
		self.ai = None
		self.lock = Lock()
		self.lock.locked
		self.init_game()

	def new_stone(self):
		self.stone = self.next_stone
		self.next_stone = Tetris_shape[randrange(len(Tetris_shape))]
		self.stone_x = COLS//2 - len(self.stone[0])//2
		self.stone_y = 0
		self.score += 1
		
		if CollisionCheck(self.board, self.stone, (self.stone_x, self.stone_y)):
			self.gameover = True
			if self.runner:
				self.runner.gameover(self.score)

	def init_game(self):
		self.board = new_board()
		self.score = 0
		self.new_stone()
		pygame.time.set_timer(self.DROPEVENT, DROP_TIME)
	
	def message(self, msg, input):
		x,y = input
		for line in msg.splitlines():
			self.screen.blit(self.font.render(line, False, (255,255,255), (0,0,0)), (x,y))
			y+=14
	
	def cntMessage(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  self.fontMain.render(line, False,(255,255,255), (0,0,0))
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (self.width // 2-msgim_center_x,self.height // 2-msgim_center_y+i*27))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					try:
						pygame.draw.rect(self.screen, COLORS[val],pygame.Rect((off_x+x)*CELL_SIZE, (off_y+y)*CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
					except IndexError:
						return False
	
	def clearlines(self, n):
		linescores = 10*n
		self.score += linescores

	def move_to(self, x):
		self.move(x - self.stone_x)

	def move(self,delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > COLS - len(self.stone[0]):
				new_x = COLS - len(self.stone[0])
			if not CollisionCheck(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	
	def drop(self):
		self.lock.acquire()
		if not self.gameover and not self.paused:
			self.stone_y += 1
			if CollisionCheck(self.board, self.stone, (self.stone_x, self.stone_y)):
				self.board = join_matrices(self.board, self.stone, (self.stone_x, self.stone_y))
				self.new_stone()
				cleared_rows = 0

				for i, row in enumerate(self.board[:-1]):
					if 0 not in row:
						j = i
						for j, row in enumerate(self.board[:-1]):
							if 0 in row:
								while(j > i):
									self.board = removeLine(self.board, j)
									cleared_rows += 1
									j-=1
									if j == 0:
										break

				self.clearlines(cleared_rows)

				self.lock.release()				
				if self.ai:
					self.ai.AIMove()
				return True
		self.lock.release()
		return False

	def insta_drop(self):
		if not self.gameover:
			while not self.drop():
				pass


	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate(self.stone)
			if not CollisionCheck(self.board, new_stone, (self.stone_x, self.stone_y)):
				self.stone = new_stone

	def start_game(self):
		self.init_game()
		self.gameover = False
	
	def toggleInstaPlay(self):
		if not self.ai:
			from ai import AI
			app.ai = AI(app)
		if self.ai:
			self.ai.instant_play = not self.ai.instant_play
			
	def toogle_pause(self):
		self.paused = not self.paused


	def run(self):
		key_actions = {
			'ESCAPE': sys.exit,
			'LEFT': lambda: self.move(-1),
			'RIGHT': lambda: self.move(+1),
			'DOWN': self.drop,
			'UP': self.rotate_stone,
			'b': self.insta_drop,
			'SPACE': self.start_game,
			'q': self.toggleInstaPlay,
			'p': self.toogle_pause,
		}

		self.gameover = False
		self.paused = False
		
		clock = pygame.time.Clock()
		while True:
			if DRAW:
				self.screen.fill((0,0,0))
				if self.gameover:
					self.cntMessage("Game Over!\nYour score: %d\nPress space to continue\nEsc for exit" % self.score)
				else:
					pygame.draw.line(self.screen, (255,255,255),(self.rlim+1, 0), (self.rlim+1, self.height))
					self.message("Next:", (self.rlim+CELL_SIZE, 2))
					self.message("Score: %d" % self.score, (self.rlim+CELL_SIZE, CELL_SIZE*5))
					self.message("Left Right for movement\n\nUP for rotate\n\nDown for faster drop\n\nP for Pause\n\nSpace for reset",
						(self.rlim+CELL_SIZE+20,CELL_SIZE*7))
					if self.ai and self.runner:
						chromosome = self.runner.population[self.runner.current_chromosome]
						self.message("Generation: %s" % self.runner.current_generation, (self.rlim+CELL_SIZE, CELL_SIZE*16))
						self.message("Chromosome: %d" % chromosome.name, (self.rlim+CELL_SIZE, CELL_SIZE*17))

					self.draw_matrix(self.bground_grid, (0,0))
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
					self.draw_matrix(self.next_stone, (COLS+1,2))
				pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == self.DROPEVENT:
					self.drop()
				elif event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_" + key):
							key_actions[key]()

			clock.tick(MAX_FPS)

if __name__ == "__main__":
	app = TetrisApp()
	app.run()
