#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
# ImprovedCodeGenerator.py  - This module will performs storage allocation for 
#                  all variables in the ST and generates instructions 
#                  during a post-order-style traversal of the AST.
#########################################################################

from SymbolTable import Variable
from collections import deque
 
class RegisterPool:
    def __init__(self):
        self.__used_register = deque([])
        self.__free_register = deque(['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6'])
    
    def alloc_register(self):
        if len(self.__free_register) > 0:
            register = self.__free_register.popleft()
            self.__used_register.append(register)
            return register
        else:
            print 'error: run out of registers'
            exit()
    
    def free_register(self, register):
        if register in self.__used_register:
            self.__used_register.remove(register)
            self.__free_register.append(register)
        else:
            print 'error: no such register in used'
            exit()
            
    def use_register(self, register):
        self.__free_register.append(register)
        self.__used_register.remove(register)
        
    def is_free_register(self, register):
        if register in self.__free_register:
            return True
        return False
    
class ImprovedCodeGenerator:
    def __init__(self, symbol_table, ast_root):
        self.__symbol_table = symbol_table
        self.__ast_root = ast_root
        self.__register_pool = RegisterPool()
        self.__output_code = ''
        self.__main_output_code = ''
        self.__function_output_code = []
        self.__false_label_number = 0
        self.__end_label_number = 0
        self.__repeat_label_number = 0
        self.__print_label_number = 0
        self.__scan_label_number = 0
        self.__div_error_label_number = 0
        self.__mod_error_label_number = 0
        self.__index_error_label_number = 0
        self.__function_label_number = 0
        self.__in_function = False
        self.__ltorg_number = 0
        self.__ltorg_distance = 0
        
    """
        This function is called by the generate_code function 
        It will perform storage allocation for all variables 
        in the ST
    """
    def __storage_allocation(self):
        offset = 0
        for key, value in sorted(self.__symbol_table.items()):
            #it will perform storage allocation for all variables in the ST
            if isinstance(value, Variable):
                #print 'perform storage allocation for the ' + str(key)
                #set the address offset for each variable
                value.set_address_offset(offset)
                
                variable_type = value.get_type()
                variable_type.accept(self)
                variable_type.to_storage_allocation()
                size = variable_type.get_size()
                offset += size
                
                #print 'storage allocation for the ' + str(key) + ' completed. size = ' + str(variable_type.get_size()) \
                #+ ' start address = ' + str(value.get_address_offset())
                
        self.add_code('.data\n')
        self.add_code('variable:\n')
        self.add_code('\t.space\t' + str(offset) + ', ' + str(0) + '\n')
        self.add_code('\t.align\t' + str(2) + '\n')
        
        
    """
        This function is called by the driver program
        It will perform storage allocation for all variables in the ST and 
        generates instructions during a post-order-style traversal of the 
        AST
    """
    def generate_code(self):
        #print 'start perform storage allocation'
        self.__storage_allocation()
        #print 'storage allocation success'
        #print 'start generates improved instructions of this program'
        
        if self.__ast_root:
            #r7 is used to store the base address
            self.__ast_root.accept(self)
            self.__ast_root.to_improved_code_generation()
            
        if self.__print_label_number > 0:
            self.add_code('printformat:\n')
            self.add_code('\t.ascii\t\"%d\\n\\000\"\n')
            self.add_code('\t.text\n')
            self.add_code('\t.align\t2\n')
            
        if self.__scan_label_number > 0:
            self.add_code('scanformat:\n')
            self.add_code('\t.ascii\t\"%d\\000\"\n')
            self.add_code('\t.text\n')
            self.add_code('\t.align\t2\n')
        
        if self.__div_error_label_number > 0:
            self.add_code('diverrorformat:\n')
            self.add_code('\t.ascii\t\"error: the expression on the right-hand side of the DIV cannot evaluate to zero at line %d, position: (\
%d, %d)\\n\\000\"\n')
            self.add_code('\t.text\n')
            self.add_code('\t.align\t2\n')
            
        if self.__mod_error_label_number > 0:
            self.add_code('moderrorformat:\n')
            self.add_code('\t.ascii\t\"error: the expression on the right-hand side of the MOD cannot evaluate to zero at line %d, position: (\
%d, %d)\\n\\000\"\n')
            self.add_code('\t.text\n')
            self.add_code('\t.align\t2\n')
            
        if self.__index_error_label_number > 0:
            self.add_code('indexerrorformat:\n')
            self.add_code('\t.ascii\t\"error: the index value %d is out of bounds at line %d, position: (\
%d, %d)\\n\\000\"\n')
            self.add_code('\t.text\n')
            self.add_code('\t.align\t2\n')
        
        index = 0
        while index < self.__function_label_number:
            self.add_code(self.__function_output_code[index])
            index += 1
        self.add_code('\tsub\tsp, fp, #4\n')
        self.add_code('\tldmfd\tsp!, {fp, lr}\n')
        self.add_code('\tbx\tlr\n')
        self.add_code('\t.global\tmain\n')
        
        self.add_code('main:\n')
        self.add_code('\tstmfd\tsp!, {fp, lr}\n')
        self.add_code('\tadd\tfp, sp, #4\n')
        self.add_code('\tldr\tr7, variablepointer\n')
        
        self.add_code(self.__main_output_code)
        self.add_code('\tsub\tsp, fp, #4\n')
        self.add_code('\tldmfd\tsp!, {fp, lr}\n')
        self.add_code('\tbx\tlr\n')
        
        self.add_ltorg_must()
        
        self.add_code('variablepointer:\n')
        self.add_code('\t.word\tvariable\n')
        
        if self.__print_label_number > 0:
            self.add_code('printformatpointer:\n')
            self.add_code('\t.word\tprintformat\n')
            
        if self.__scan_label_number > 0:
            self.add_code('scanformatpointer:\n')
            self.add_code('\t.word\tscanformat\n')
            
        if self.__div_error_label_number > 0:
            self.add_code('diverrorformatpointer:\n')
            self.add_code('\t.word\tdiverrorformat\n')
        
        if self.__mod_error_label_number > 0:
            self.add_code('moderrorformatpointer:\n')
            self.add_code('\t.word\tmoderrorformat\n')
            
        if self.__index_error_label_number > 0:
            self.add_code('indexerrorformatpointer:\n')
            self.add_code('\t.word\tindexerrorformat\n')
            
        #print 'Generate the instructions of the program finished'
        
    def add_code(self, code):
        self.__output_code += code
        
    def add_main_code(self, code):
        if self.__in_function == False:
            self.__main_output_code += code
            self.__ltorg_distance += 1
        else:
            self.__function_output_code[self.__function_label_number-1] += code
            
    def set_in_function(self):
        self.__in_function = True
        
    def set_out_function(self):
        self.__in_function = False
        
    def is_in_function(self):
        return self.__in_function
    
    def add_function_code(self, code):
        self.__function_output_code[self.__function_label_number-1] += code
        
    def add_ltorg_must(self):
        self.__ltorg_number += 1
        self.__output_code += '\tb\tL' + str(self.__ltorg_number) + '\n'
        self.__output_code += '\t.ltorg\n'
        self.__output_code += 'L' + str(self.__ltorg_number) + ':\n'
        
    def add_ltorg(self):
        if self.__ltorg_distance >= 800:
            self.__ltorg_number += 1
            self.__main_output_code += '\tb\tL' + str(self.__ltorg_number) + '\n'
            self.__main_output_code += '\t.ltorg\n'
            self.__main_output_code += 'L' + str(self.__ltorg_number) + ':\n'
            self.__ltorg_distance = 0
        
    def generate_false_label(self):
        self.__false_label_number += 1
        label_name = '.false' + str(self.__false_label_number)
        return label_name
    
    def generate_end_label(self):
        self.__end_label_number += 1
        label_name = '.end' + str(self.__end_label_number)
        return label_name
    
    def generate_repeat_label(self):
        self.__repeat_label_number += 1
        label_name = '.repeat' + str(self.__repeat_label_number)
        return label_name
    
    def generate_print_label(self):
        self.__print_label_number = 1
    
    def generate_scan_label(self):
        self.__scan_label_number = 1
        
    def generate_div_error_label(self):
        self.__div_error_label_number = 1
        
    def generate_mod_error_label(self):
        self.__mod_error_label_number = 1
        
    def generate_index_error_label(self):
        self.__index_error_label_number = 1
        
    def generate_function_label(self):
        if self.__function_label_number > 0:
            self.__function_output_code[self.__function_label_number-1] += '\tsub\tsp, fp, #4\n'
            self.__function_output_code[self.__function_label_number-1] += '\tldmfd\tsp!, {fp, lr}\n'
            self.__function_output_code[self.__function_label_number-1] += '\tbx\tlr\n'
        self.__function_label_number += 1
        self.__function_output_code.append('')
        
        
    def alloc_register(self):
        return self.__register_pool.alloc_register()
    
    def free_register(self, register):
        self.__register_pool.free_register(register)
        
    def is_free_register(self, register):
        return self.__register_pool.is_free_register(register)
        
    def print_code(self):
        print self.__output_code
        
        