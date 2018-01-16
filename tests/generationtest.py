import unittest

from evolution.generation import Generation, Specie
from evolution.genome import *

class TestGenerationCase(unittest.TestCase):

    # def test_next_generation_the_same(self):
    #     mutation_coefficients = {
    #         'add_connection': 1.0,
    #         'split_connection': 0.0,
    #         'change_weight': 0.0,
    #         'new_connection_abs_max_weight': 5.0,
    #         'max_weight_mutation': 2.5
    #     }
    #     compatibility_coefficients = {
    #         'excess_factor': 2.0,
    #         'disjoint_factor': 2.0,
    #         'weight_difference_factor': 1.0
    #     }
    #
    #     generation = Generation()
    #
    #     specie = Specie()
    #
    #     for i in range(10):
    #         specie.add_genome(Genome([[1, 2, 0, True, 0], [1, 3, 0, True, 1]], 1, 1))
    #
    #     generation.species[0] = specie
    #
    #     generation.create_new_generation(mutation_coefficients, compatibility_coefficients)
    #     print(generation.species[0].genomes)
    #     print(specie.genomes)
    #     #self.assertEqual(generation.species)

    def test_evolve_xor(self):

        generation = Generation()

        specie = Specie()

        c1 = ConnectionGene(1, 3, enabled=True)
        c2 = ConnectionGene(2, 3, enabled=True)

        for i in range(100):
            specie.add_genome(Genome([[1, 3, random.random(), True, 0], [2, 3, random.random(), True, 1]], 2, 1))

        generation.species[0] = specie

        generation.create_new_generation()

        i = 1
        while i < 100:
            generation.create_new_generation()
            i += 1
        print(generation.fitness)


if __name__ == '__main__':
    firstSuite = unittest.TestLoader().loadTestsFromTestCase(TestSpecieCase)
    secondSuite = unittest.TestLoader().loadTestsFromTestCase(TestGenerationCase)
    unittest.TextTestRunner(verbosity=2).run(firstSuite)
    unittest.TextTestRunner(verbosity=2).run(secondSuite)
