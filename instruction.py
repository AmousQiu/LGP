import numpy as np
import random
import math
from LGP.configuration import Configuration

class Instruction:

    def __init__(self, instruction : list = None):
        self.op_map = {
            0: self.plus,
            1: self.minus,
            2: self.divide,
            3: self.mult
    }
        if instruction == None:
            self.randomize_instruction()
        else:
            self.instruction = instruction

    def duplicate(self):
        return Instruction([i for i in self.instruction])

    def randomize_instruction(self):
        source_limit = max(Configuration.register_num,Configuration.input_feature_num)
        self.instruction = [
            np.random.randint(0, 2),
            np.random.randint(0, source_limit),
            np.random.randint(0, Configuration.op_num),
            np.random.randint(0, Configuration.register_num)
        ]

    def plus(self, a, b):
        result = a+b
        return result
    
    def minus(self, a, b):
        result = a-b
        return result
    
    def divide(self, a, b):
        b[(b >= -1) & (b <= 1)] = 1
        result = (a / b)/ 2 
        return result
    
    def mult(self, a, b):
        result = (a * b) *2
        return result
    
    def execute_instruction(self, registers, input):
        mode = self.instruction[0]
        source_register = self.instruction[1]
        operation = self.instruction[2]
        dest_register = self.instruction[3]
        
        if mode == 0:
            #registers[dest_register] = input[source_register % Configuration.input_feature_num]
            registers[dest_register] = self.op_map[operation](input[source_register%Configuration.input_feature_num], registers[dest_register])
        elif mode == 1:
            registers[dest_register] = self.op_map[operation](registers[source_register%Configuration.register_num], registers[dest_register])
    

    def execute_instruction_matrix(self,register_matrix,input):
        mode = self.instruction[0]
        source_register = self.instruction[1]
        operation = self.instruction[2]
        dest_register = self.instruction[3]

        if mode == 0:
            register_matrix[:,dest_register] = self.op_map[operation](input[:,(source_register%Configuration.input_feature_num)],register_matrix[:,dest_register]) 
        elif mode == 1:
            register_matrix[:,dest_register] = self.op_map[operation](register_matrix[:,(source_register%Configuration.register_num)],register_matrix[:,dest_register]) 
        
        return register_matrix


    def get_operator_symbol(self, op_code):
        return ['+', '-', '/2', '*2'][op_code]

    def print_instruction(self):
        operator_symbol = self.get_operator_symbol(self.instruction[2])
        source_register = self.instruction[1]
        if self.instruction[0] == 0:
            if (self.instruction[2] in [0,1]):
                return 'R[' + str(self.instruction[3]) + '] = IP[' + str(source_register%Configuration.input_feature_num) + '] ' + operator_symbol + ' R[' + str(self.instruction[3]) + ']\n'
            else:
                return 'R[' + str(self.instruction[3]) +'] = IP[' + str(source_register%Configuration.input_feature_num)+'] ' + operator_symbol + ' R[' + str(self.instruction[3]) + '] ' ' \n'
        else:
            if (self.instruction[2] in [0,1]):
                return 'R[' + str(self.instruction[3]) +'] = R[' + str(source_register%Configuration.register_num) + '] ' + operator_symbol + ' R[' + str(self.instruction[3]) + ']\n'
            else:
                return 'R[' + str(self.instruction[3]) +'] = R[' + str(source_register%Configuration.register_num)+'] ' + operator_symbol + ' R[' + str(self.instruction[3]) + '] ' ' \n'
        
    def print_num_instruction(self):
        return str(self.instruction)
    
    def mutate_instruction(self,threshold):
        source_limit = max(Configuration.register_num,Configuration.input_feature_num)
        if random.random() < threshold / 4:
            self.instruction[0] = np.random.randint(0, 2)
        if random.random() < threshold / 4:
            self.instruction[1] = np.random.randint(0, source_limit)
        if random.random() < threshold / 4:
            self.instruction[2] = np.random.randint(0, Configuration.op_num)
        if random.random() < threshold / 4:
            self.instruction[3] = np.random.randint(0, Configuration.register_num)