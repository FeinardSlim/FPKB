import time
import pygame,sys
from tetris import ROWS,COLS,CELL_SIZE,TetrisApp
from genetic_algorithms import GeneticAlgorithms

class tetrisStart:
    def run(self):
        pygame.init()
        done = False
        self.width = CELL_SIZE * (COLS+18)
        self.height = CELL_SIZE * ROWS
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.fontMain = pygame.font.SysFont("Comic Sans MS",20)
        text = self.fontMain.render("Welcome to tetris", True, (255, 255, 255))
        startParam  = self.fontMain.render("Press anything to start",True,(255,255,255))
        clock = pygame.time.Clock()
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = False
                if event.type == pygame.KEYDOWN:
                    done = True
            self.screen.fill((0, 0, 0))
            self.screen.blit(text,(self.width // 3 + 15,self.height // 2 - 20))
            self.screen.blit(startParam,(self.width // 3 + 15,self.height //2 + 10))
            pygame.display.flip()
            clock.tick(60)
        gametype = False
        typeScreen = self.fontMain.render("Press F1 to get tetris and space for Genetic algorithm",True,(255,255,255))
        while gametype == 0:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F1:  
                        app = TetrisApp(__name__)
                        app.run()
                        gametype = True
                    if event.key == pygame.K_SPACE:
                        gametype = True
                        GeneticAlgorithms().run()
                self.screen.fill((0, 0, 0))
                self.screen.blit(typeScreen,(15,self.height // 2 - 20))
                pygame.display.flip()
                clock.tick(60) 
        

if __name__ == "__main__":
    tetrisStart().run()
    pass