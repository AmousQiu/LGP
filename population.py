from LGP.program import Program  # Import the Program class
from LGP.configuration import Configuration  # Import the Configuration class
import numpy as np
import random
import bz2 

class Population:
    def __init__(self):
        self.population = []
        #print("Initializing population")
        for _ in range(Configuration.population_size):
            p = Program()
            self.population.append(p)

    def evaluate_fitness(self, X, y):
        for program in self.population:
            program.evaluation_matrix(X,y)


#    def evalute_fitness_length(self):
#        for program in self.population:

    def two_point_crossover(self, parent1, parent2):
        # Calculate the maximum program length
        max_program_length = Configuration.max_instruction_lines
        
        # Choose random indices for crossover, ensuring the child's length doesn't exceed the maximum
        crossover_index1 = np.random.randint(0, min(len(parent1.instruction_sets), len(parent2.instruction_sets), max_program_length))
        crossover_index2 = np.random.randint(crossover_index1, min(len(parent1.instruction_sets), len(parent2.instruction_sets), max_program_length))

        # Create an empty child program
        child1 = Program()
        child2 = Program()
        child1.instruction_sets = parent1.instruction_sets[:crossover_index1] + parent2.instruction_sets[crossover_index1:crossover_index2] +parent1.instruction_sets[crossover_index1:]
        child2.instruction_sets = parent2.instruction_sets[:crossover_index2] + parent1.instruction_sets[crossover_index1:crossover_index2] +parent2.instruction_sets[crossover_index2:]
        # Ensure the child's length doesn't exceed the maximum program length
        if len(child1.instruction_sets) > max_program_length:
            child1.instruction_sets = child1.instruction_sets[:max_program_length]
            
        if len(child2.instruction_sets) > max_program_length:
            child2.instruction_sets = child2.instruction_sets[:max_program_length]   

        return child1,child2
    
     
    def one_point_crossover(self,parent1,parent2):
        max_program_length = Configuration.max_instruction_lines
        crossover_index1 = np.random.randint(0,len(parent1.instruction_sets))
        crossover_index2 = np.random.randint(0,len(parent2.instruction_sets))
        child1 = Program()
        child1.instruction_sets = parent1.instruction_sets[:crossover_index1] + parent2.instruction_sets[crossover_index2:]

        child2 = Program()
        child2.instruction_sets = parent2.instruction_sets[:crossover_index2] + parent1.instruction_sets[crossover_index1:]
        
        if len(child1.instruction_sets) > max_program_length:
            child1.instruction_sets = child1.instruction_sets[:max_program_length]
       
        if len(child2.instruction_sets) > max_program_length:
            child2.instruction_sets = child2.instruction_sets[:max_program_length]
        return child1,child2


    def length_bidding_selection(self):
        for p in self.population:
            if len(p.instruction_sets)<Configuration.min_instruction_lines:
                self.population.remove(p)
                
        ranked_programs = sorted(self.population, 
                            key=lambda p: (p.fitness,-len(p.instruction_sets)), 
                            reverse=True)  
         
        unique_fitness = set()
        filtered_programs = []
        
        for program in ranked_programs:
            if program.fitness not in unique_fitness:
                filtered_programs.append(program)
                unique_fitness.add(program.fitness)
        save_num = int(Configuration.population_size * Configuration.keep_rate)
        i = 0
        while len(filtered_programs)<save_num:
            filtered_programs.append(ranked_programs[i])
            i = i+1
        return filtered_programs
    
    def normal_selection(self):
        ranked_programs = sorted(self.population, key=lambda p: p.fitness, reverse=True)   
        save_num = int(Configuration.population_size *  Configuration.keep_rate)
        return ranked_programs[:save_num]
        
    def generation(self, X, y, gen, crossover=True, probability_mutate=True):
        # Evaluation and parent selection (unchanged)
        self.evaluate_fitness(X,y)
        for program in self.population:
            program.age = program.age + 1
        ranked_programs = sorted(self.population, key=lambda p: p.fitness, reverse=True)
        
        save_num = int(Configuration.population_size * Configuration.keep_rate)
        best_program = ranked_programs[0].duplicate()
        best_program.reset()
        
        fitness_arr = [p.fitness for p in ranked_programs]
        length_arr = [len(p.instruction_sets) for p in ranked_programs]
        
        # Parent selection (unchanged)
        #parent_pool = self.normal_selection()
        parent_pool = self.length_bidding_selection()
        if len(parent_pool) > save_num:
            parent_pool = parent_pool[:save_num]
            
        num_offspring = Configuration.population_size - len(parent_pool)
        offspring = []

        for _ in range(num_offspring):
            if crossover and random.random() < Configuration.mutation_rate:  
                # Select parents and protect originals
                p1, p2 = np.random.choice(parent_pool, 2, replace=False)
                parent1, parent2 = p1.duplicate(), p2.duplicate()
                
                # Perform crossover (50/50 one-point vs two-point)
                if random.random() < 0.5:
                    child1, child2 = self.two_point_crossover(parent1, parent2)
                else:
                    child1, child2 = self.one_point_crossover(parent1, parent2)
                
                # Select one child randomly to maintain population size
                child = random.choice([child1, child2])
                if gen > 100:
                    child.mutate(base_rate=0.5,probability_mutate=probability_mutate)
                else:
                    child.mutate(base_rate=0.99,probability_mutate=probability_mutate)
            else:
                parent = np.random.choice(parent_pool)
                child = parent.duplicate()
                for i in range(5):
                    child.mutate(probability_mutate=probability_mutate)  # Always mutate mutation-only children
            
            offspring.append(child)

        # Final population update (unchanged)
        self.population = parent_pool + offspring
        return fitness_arr, length_arr, best_program
    
    def compress_bzip2_string(self,s):
        data = s.encode('utf-8')  # Convert string to bytes
        compressed = bz2.compress(data)
        return len(compressed)
    
    def diversity(self,best_program):
        sum = 0 
        for p in self.population:
            Cx = self.compress_bzip2_string(p.print())
            Cy = self.compress_bzip2_string(best_program.print())
            Cxy = self.compress_bzip2_string(p.print() + best_program.print())
            diff = (Cxy - min(Cx,Cy)) / max(Cx,Cy)
            sum += diff
        
        sum = sum / len(self.population)
        return sum