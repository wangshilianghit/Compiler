#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
##   Interpreter.py  - This module will build the environment and interpret
##                     the actual program
##
#########################################################################

from SymbolTable import Variable

class Interpreter:
    def __init__(self, symbol_table, ast_root):
        self.__symbol_table = symbol_table
        self.__ast_root = ast_root
        self.__environment_array = []
        self.__current_environment = None
        self.__is_record = False
        self.__scope_num = -1
        self.__stack = []
    
    """
        This function is called by interpret 
        It will build the environment based on the symbol table
        
    """
    def __build_environment(self):
        environment = {}
        self.__scope_num += 1
        for key, value in sorted(self.__symbol_table.items()):
            #we just build the environment for the variable entry
            if isinstance(value, Variable):
                variable_type = value.get_type()
                variable_type.accept(self)
                environment[key] = variable_type.to_environment()
                
        self.__environment_array.append(environment)
        self.__current_environment = environment
    
    """
        This function is called by the driver program
        It will interpret the program based on the AST and the environment
        
    """
    def interpret(self):
        #print 'start building the environment'
        self.__build_environment()
        #print 'building the environment success'
        #print 'start interpreting the program'
        self.__ast_root.accept(self)
        self.__ast_root.to_interpret()
        #print 'interpreting the program finished'
        
        
    def push_stack(self, element):
        self.__stack.append(element)
        
    def pop_stack(self):
        return self.__stack.pop()
        
    def get_environment_box(self, name):
        if self.__is_record == True:
            return self.__current_environment[name]
        else:
            if name in self.__current_environment:
                return self.__current_environment[name]
            else:
                return self.__environment_array[0][name]
    
    def get_global_environment_box(self, name):
        if self.__is_record == True:
            return self.__environment_array[0][name]
        else:
            return self.__environment_array[0][name]
        
        
    def get_current_environment(self):
        return self.__current_environment
    
    """
        This function is used in visiting the elements in Record type
    
    """
    def set_current_environment(self, environment):
        self.__current_environment = environment
        self.__is_record = True
        
    """
        This function is used to get out of the scope of Record
        
    """
    def reset_environment(self):
        self.__current_environment = self.__environment_array[self.__scope_num]
        self.__is_record = False   
    
    """
        This function is used in calling a function
        
    """
    def create_environment(self, environment):
        self.__scope_num += 1
        self.__environment_array.append(environment)
        self.__current_environment = environment
        
    """
        This function is used when the function returns
    
    """
    def delete_environmnet(self):
        self.__scope_num -= 1
        self.__environment_array.pop()
        self.__current_environment = self.__environment_array[self.__scope_num]
    
    
        
    def check_stack(self):
        if self.__stack:
            print 'stack is not empty, error may exists in interpreting process'
        

        
    
        