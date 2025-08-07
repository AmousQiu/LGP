import numpy as np
import random
from LGP.instruction import Instruction
from LGP.configuration import Configuration
from sklearn.metrics import f1_score

class Program:
    def __init__(self, type = 0, p1_age=0, p2_age=0, age = 0, instruction_sets : list = None):
        #self.registers = np.zeros(Configuration.register_num)
        self.type = type
        self.age = age
        self.p1_age = p1_age
        self.p2_age = p2_age
        if (instruction_sets == None):
            self.instruction_sets = []
            self.add_random_instructions()
        else:
            self.instruction_sets = [instruction.duplicate() for instruction in instruction_sets]
        self.fitness = 0
        
    def duplicate(self):
        return Program(self.type,self.p1_age,self.p2_age,self.age, self.instruction_sets)

    def reset(self):
        self.registers = np.zeros(Configuration.register_num)
        self.fitness = 0
        
        
    def add_random_instructions(self):
        num_lines = np.random.randint(Configuration.min_instruction_lines, Configuration.max_instruction_lines + 1)
        for _ in range(num_lines):
            self.instruction_sets.append(Instruction())
            
    def execute_program(self, input_data):
        self.reset()
        for instruction in self.instruction_sets:
            instruction.execute_instruction(self.registers, input_data)
        return np.argmax(self.registers[:Configuration.num_classes])


    def mutate(self, base_rate=0.7,probability_mutate=True):
        if not probability_mutate:
            action = random.randint(0,3)
            if action == 0 and len(self.instruction_sets)>1:
                self.instruction_sets.remove(random.choice(self.instruction_sets))
            elif action == 1:
                instruction = random.choice(self.instruction_sets)
                instruction.mutate_instruction(1)
            elif action == 2:
                self.instruction_sets.append(Instruction())
        else:
            for idx, instruction in enumerate(self.instruction_sets):
                pos_weight = ((len(self.instruction_sets) - idx) / len(self.instruction_sets))
                mutation_prob = base_rate * pos_weight
                
                if random.random() < mutation_prob:
                    # Aggressive mutation options
                    action = random.choices(
                        [0, 1, 2],  # Modify, Insert, Delete
                        weights=[0.6, 0.2, 0.2],  # 60% modify, 20% insert, etc.
                        k=1
                    )[0]
                    
                    if action == 0:  # Modify instruction
                        instruction.mutate_instruction(1.0)
                        
                    elif action == 1:  # Insert new instruction
                        if len(self.instruction_sets) < Configuration.max_instruction_lines:
                            self.instruction_sets.insert(idx, Instruction())
                            
                    elif action == 2:  # Delete instruction
                        if len(self.instruction_sets) > Configuration.min_instruction_lines:
                            del self.instruction_sets[idx]

    
    def evaluation_matrix(self,X,y):
        register_matrix = np.zeros((len(X),Configuration.register_num))
        for instruction in self.instruction_sets:
            register_matrix = instruction.execute_instruction_matrix(register_matrix,X)
        
        y_pred = register_matrix[:,:Configuration.num_classes].argmax(1)
        self.fitness = f1_score(y,y_pred,average='macro')
        return y_pred

    def print(self):
        whole_thing = ''
        for instruction in self.instruction_sets:
            whole_thing= whole_thing+(instruction.print_instruction())
        return whole_thing
    
    def __str__(self) -> str:
        return self.print()[0]
    
    def __repr__(self) -> str:
        return self.print()[0]
    
    def detect_intron(self):
        program_length = len(self.instruction_sets)
        program_without_intron = []
        used_register = set()
        
        #hard code here since it's binary problem
        used_register.add(0)
        used_register.add(1)
        
        intron_index = [] 
        # Traverse instructions in reverse
        
        for i,instruction in enumerate(reversed(self.instruction_sets)):
   
            dest_reg = instruction.instruction[3]
            src_reg = instruction.instruction[1]
            mode = instruction.instruction[0]
            if dest_reg in used_register:
                program_without_intron.append(instruction.duplicate())
                
                if mode == 1:
                    src_reg = src_reg%Configuration.register_num
                    if src_reg not in used_register:
                        print(src_reg, "added to the used register set")
                        used_register.add(src_reg)
            else:
                intron_index.append(len(self.instruction_sets) - i - 1)
                        
                        
        program_without_intron.reverse()

        return intron_index,Program(instruction_sets=program_without_intron)
