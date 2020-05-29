from tetris import TetrisApp
from ai import AI
from random import randrange, randint
import random
import sys
from enum import Enum

# Config
populasi = 20
GAMES_TO_AVG = 2
survive = 5
kelahirantiapgenerasil = populasi - survive
skipMutation = 3
rateforMutation = 20 
CONVERGED_THRESHOLD = 15

def __generate_name():
	current_name = 1
	while True:
		yield current_name
		current_name += 1

_generate_name = __generate_name()

class Chromosome(object):
	def __init__(self, heuristics):
		self.name = next(_generate_name)
		self.heuristics = heuristics
		self.total_fitness = 0
		self.games = 0

	def avgFitness(self):
		return self.total_fitness / self.games

class GeneticAlgorithms(object):
	def __init__(self):
		self.app = TetrisApp(self)
		self.ai = AI(self.app)
		self.app.ai = self.ai
		self.population = [self.randChromosome() for _ in range(populasi)]
		self.current_chromosome = 0
		self.current_generation = 1
		self.ai.heuristics = self.population[self.current_chromosome].heuristics

	def run(self):
		self.app.run()

	def population_has_converged(self):
		t = CONVERGED_THRESHOLD
		pop = self.population
		return all(all(pop[0].heuristics[f]-t < w < pop[0].heuristics[f]+t for f, w in c.heuristics.items()) for c in pop)

	def nextGen(self):
		print("__________________\n")
		if self.population_has_converged():
			print("Population has converged on generation %s.\n values: %s" 
				% (self.current_generation, [(f.__name__, w) for f, w in self.population[0].heuristics.items()]))
			sys.exit()
		print("generasi %s selesai\n" % self.current_generation)
		print("Rata-rata fitness", sum([c.avgFitness() for c in self.population]) / populasi)
		self.current_generation += 1
		for c in self.population:
			print("chromosome", c.name, "fitness", c.avgFitness())
		best_chromosome = max(self.population, key=lambda c: c.avgFitness())
		print("Fittest chromosome:", best_chromosome.name, "fitness", best_chromosome.avgFitness(), "\n%s" % [(f.__name__, w) for f, w in best_chromosome.heuristics.items()])

		print("\nEvolusi:\n")
		newPopulation = self.selection(survive)
		for c in newPopulation:
			print("chromosome", c.name, "fitness", c.avgFitness(), "selamat")
		for _ in range(kelahirantiapgenerasil):
			parents = self.selection(2)
			newPopulation.append(self.crossover(parents[0], parents[1]))
			print(parents[0].name, "dan", parents[1].name, "menghasilkan", newPopulation[-1].name)
		for _ in range(skipMutation):
			for chromosome in newPopulation:
				self.mutation(chromosome, rateforMutation / skipMutation)
		print("__________________\n")
		assert len(newPopulation) == len(self.population), "survive + kelahirantiapgenerasil != populasi"
		self.population = newPopulation
	
	def NextAIinit(self):
		self.current_chromosome += 1
		if self.current_chromosome >= populasi:
			self.current_chromosome = 0
			self.nextGen()
		self.ai.heuristics = self.population[self.current_chromosome].heuristics

	def gameover(self, score):
		chromosome = self.population[self.current_chromosome]
		chromosome.games += 1
		chromosome.total_fitness += score
		if chromosome.games % GAMES_TO_AVG == 0:
			self.NextAIinit()
		self.app.start_game()
	
	def selection(self, num_selected):
		def roulette(population):
			total_fitness = sum([c.avgFitness() for c in population])
			winner = randrange(int(total_fitness))
			currenFitness = 0
			for chromosome in population:
				currenFitness += chromosome.avgFitness()
				if currenFitness > winner:
					return chromosome
		
		survivors = []
		for _ in range(num_selected):
			survivors.append(roulette([c for c in self.population if c not in survivors]))
		return survivors


	def crossover(self, c1, c2):
		def randomAttr():
			heuristics = {}
			for rand, _ in c1.heuristics.items():
				heuristics[rand] = random.choice((c1, c2)).heuristics[rand]
			return Chromosome(heuristics)
	
		return randomAttr()

	def mutation(self, chromosome, rateforMutation):
		if randint(0, int(rateforMutation)) == 0:
			h = chromosome.heuristics
			h[random.choice(list(h.keys()))] = randrange(-1000, 1000)
			print(chromosome.name, "bermutasi")

	def randChromosome(self):
		return Chromosome({rand: randrange(-1000, 1000) for rand, weight in self.ai.heuristics.items()})

if __name__ == "__main__":
	GeneticAlgorithms().run()
	