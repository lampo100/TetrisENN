from random import shuffle
from functools import reduce
from threading import Thread
import random
from nn.neuralnetwork import NeuralNetwork
from evolution.genome import Genome
import math


class Evaluate(Thread):
    def __init__(self, nn):
        Thread.__init__(self)
        self._neural_network = nn
        self._fitness = None

    def run(self):
        self._fitness = 0
        self._fitness += 5*math.exp(-(self._neural_network.forward([1, 1])[0] - 0)**2)
        self._fitness += 5*math.exp(-(self._neural_network.forward([1, 0])[0] - 1)**2)
        self._fitness += 5*math.exp(-(self._neural_network.forward([0, 0])[0] - 0)**2)
        self._fitness += 5*math.exp(-(self._neural_network.forward([0, 1])[0] - 1)**2)

    def join(self):
        Thread.join(self)
        return self._fitness


class Generation:
    _specie_number = 0

    def __init__(self, mutation_coefficients=None, compatibility_coefficients=None, compatibility_threshold=6.0):
        self.species = {}
        self.fitness = None

        if mutation_coefficients is None:
            self.mutation_coefficients = {
                'add_connection': 0.1,
                'split_connection': 0.3,
                'change_weight': 0.5,
                'new_connection_abs_max_weight': 1.0,
                'max_weight_mutation': 0.5
            }
        if compatibility_coefficients is None:
            self.compatibility_coefficients = {
                'excess_factor': 2.0,
                'disjoint_factor': 2.0,
                'weight_difference_factor': 1.0
            }
        self.compatibility_threshold = compatibility_threshold
        self.r_factor = 0.2

    def create_new_generation(self):
        """
        Creates and returns new Generation of species based on current generation.
        """

        # get phenotype for each genome
        phenotypes = [phenotype for specie in self.species.values() for phenotype in specie.get_phenotypes()]

        # create thread to calculate fitness for each neural network
        threads = [Evaluate(phenotype) for phenotype in phenotypes]

        for thread in threads:
            thread.start()

        # wait for all networks to end their tasks
        phenotypes_fitness = []

        for thread in threads:
            phenotypes_fitness.append(thread.join())

        for fit in phenotypes_fitness:
            if fit is None:
                print("reiklfdfsmkdfsidfsu")

        number_of_genomes = 0
        for species in self.species.values():
            number_of_genomes += len(species.genomes)
        if(number_of_genomes != len(phenotypes_fitness)):
            print("INNAAAAA ILOOOOOOSC")
        print(phenotypes_fitness)

        # each genome gets fitness of it's phenotype
        for (phenotype, fitness) in zip(phenotypes, phenotypes_fitness):
            if(fitness is None):
                print("FITNESS IS NONE, ABORT")
            phenotype.get_genome().fitness = fitness

        # divide each fitness in specie by specie size
        total = 0
        for specie in self.species.values():
            specie.adjust_fitness()
            spiecies_adjusted_fitness = specie.get_adjusted_fitness()
            total = total + spiecies_adjusted_fitness

        # calculate mean adjusted generation fitness

        self.fitness = total

        # create place for new species
        new_species = {k: Specie() for k in self.species.keys()}

        for (key, specie) in self.species.items():
            for species in self.species.values():
                if species.get_fitness() is None:
                    print("FIT NONE AAA2222222") #TODO TUTAJ BREAKA, TUTAJ WYWALA
            specie_offspring_len = round((specie.get_adjusted_fitness() / self.fitness) * 5)
            parents = specie.get_parents(self.r_factor)

            # create specie_offspring_len children
            for i in range(specie_offspring_len):
                # create child
                offspring = Specie.get_offspring(parents)
                # mutate it
                offspring.mutate(self.mutation_coefficients)

                # select species for the child


                fitting_specie_found = False
                # favor parents' species
                if self._is_specie_fitting_for_offspring(specie, offspring):
                    new_species[key].add_genome(offspring)
                    continue
                # child does not fit in parents' specie
                # check if it does in some other specie
                else:
                    for (key, specie) in self.species.items():
                        if self._is_specie_fitting_for_offspring(specie, offspring):
                            new_species[key].add_genome(offspring)
                            fitting_specie_found = True
                            break
                # child does not fit in any of the current species
                # create new species and add child as it's representative
                if not fitting_specie_found:
                    # create new specie with offspring as it's representative
                    fresh_spiecies = Specie()
                    fresh_spiecies.add_genome(offspring)
                    new_species[Generation._get_new_specie_number()] = fresh_spiecies

        non_empty_species = {}
        for key, species in new_species.items():
            if species.genomes:
                non_empty_species[key] = species

        self.species = non_empty_species

    def _is_specie_fitting_for_offspring(self, specie, offspring):
        is_fitting = False
        compatibility_distance = offspring.compatibility_distance(specie.get_representative(), self.compatibility_coefficients)

        if compatibility_distance < self.compatibility_threshold:
            specie.add_genome(offspring)
            is_fitting = True

        return is_fitting

    @staticmethod
    def _get_new_specie_number():
        Generation._specie_number += 1
        return Generation._specie_number - 1

class Specie:

    def __init__(self):
        self.genomes = {}
        self.fitness = None
        self.adjusted_fitness = None
        self.genome_number = 0

    def add_genome(self, genome):
        self.genomes[self.get_new_genome_number()] = genome

    def adjust_fitness(self):
        """
        Adjusts fitness score of every genome in the species.
        """
        for genome in self.genomes.values():
            genome.adjusted_fitness = genome.fitness/float(len(self.genomes))

        self.adjusted_fitness = sum(genome.adjusted_fitness for genome in self.genomes.values())

    def get_fitness(self):
        return self.fitness

    def get_adjusted_fitness(self):
        return self.adjusted_fitness

    def get_phenotypes(self):
        return [NeuralNetwork(genome) for genome in self.genomes.values()]

    def get_representative(self):
        return random.choice(list(self.genomes.values()))

    def get_parents(self, r):
        """
        Returns parents that will reproduce.
        """
        # sort genomes by adjusted_fitness
        try:
            genomes = sorted([genome for genome in self.genomes.values()], key=lambda x: x.adjusted_fitness, reverse=True)
        except:
            print("dssssssssddsds")
        # get r% of best-performing genomes ( minimum 2 )
        count_to_return = math.ceil(r*len(genomes))
        genomes = genomes[:count_to_return]
        if not genomes:
            print("aAASDASDASDASDWA")
        shuffle(genomes)
        return genomes

    @staticmethod
    def get_offspring(parents):
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)

        offspring = Genome.reproduce(parent1, parent2)

        return offspring

    def get_new_genome_number(self):
        self.genome_number += 1
        return self.genome_number - 1