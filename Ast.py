#!/usr/bin/python

#########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
## Ast.py - This module is used for producing AST 
##
#########################################################################

#########################################################################
## Node - This class is the base class for AST node
##
#########################################################################

from Environment import IntegerBox
from Environment import DereferenceBox
from SymbolTable import Integer
from SymbolTable import Array
from SymbolTable import Record
from SymbolTable import Variable
from SymbolTable import LocalVariable
from SymbolTable import GlobalVariable
from SymbolTable import FormalVariable
import copy

class Node( object ):
    def __init__(self):
        self._visitor = None
        self._start_position = 0
        self._end_position = 0
        self._line = 0
        
    def accept(self, visitor):
        self._visitor = visitor
        
    def to_asc_output(self):
        pass
    
    def to_dot_output(self):
        pass
    
    def print_string(self):
        pass
        
    def get_start_position(self):
        return self._start_position
    
    def set_start_position(self, start_position):
        self._start_position = start_position
        
    def get_end_position(self):
        return self._end_position
    
    def set_end_position(self, end_position):
        self._end_position = end_position
        
    def get_line(self):
        return self._line
    
    def set_line(self, line):
        self._line = line
        
        
#########################################################################
## Instruction - This class is a derived class from Node to represent the 
##            instruction categories.
##             
#########################################################################

class Instruction( Node ):
    def __init__(self):
        self.__next_instruction = None
        super(Instruction, self).__init__()
    
    def get_next_instruction(self):
        return self.__next_instruction
    
    def set_next_instruction(self, next_instruction):
        self.__next_instruction = next_instruction
        
    def print_string(self):
        pass
        
        
#########################################################################
## Assign - This class is a derived class for Instruction to represent the 
##            assign instruction.
##             
#########################################################################

class Assign( Instruction ):
    def __init__(self, location_node, expression_node):
        self.__location = location_node
        self.__expression = expression_node
        super(Assign, self).__init__()
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Assign:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'location =>\n')
        self.__location.accept(self._visitor)
        self.__location.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'expression =>\n')
        self.__expression.accept(self._visitor)
        self.__expression.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_asc_output()
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\":=\",shape=box]\n')
        self.__location.accept(self._visitor)
        self.__location.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__location)) + ' [label=\"location\"]\n')
        self.__expression.accept(self._visitor)
        self.__expression.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression)) + ' [label=\"expression\"]\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_dot_output()
            self._visitor.add_semantic_output('{rank=same;_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.get_next_instruction())) + \
            ' [label=\"next\"]}\n')
    
    def to_interpret(self):
        #print 'interpret assign starts'
        self.__location.accept(self._visitor)
        self.__location.to_interpret()
        location_box = self._visitor.pop_stack()
        while type(location_box) == DereferenceBox:
            location_box = location_box.get_reference_box()
            
        self._visitor.reset_environment()
        self.__expression.accept(self._visitor)
        self.__expression.to_interpret()
        value_box = self._visitor.pop_stack()
        while type(value_box) == DereferenceBox:
            value_box = value_box.get_reference_box()
        
        if type(value_box) == int:
            location_box.set_value(value_box)
        else:
            location_box.copy(value_box)
                    
        self._visitor.reset_environment()
        #print 'interpret assign ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_interpret()
     
    """
        This function will generate the code for Assign node in AST
        r7 is used to store the base address
        r1 is used to store the start address offset of the variable in location
        r2 is used to store the value of expression or the start address offset of the variable 
        in expression
        
    """
    def to_code_generation(self):
        #print 'generate assign starts'
        #Integer type to Integer type
        if type(self.__location.get_type()) == Integer:
            self.__location.accept(self._visitor)
            self.__location.to_code_generation()
            self._visitor.add_code('\tpop\t{r1}\n')
            self._visitor.add_code('\tpush\t{r1}\n')
            
            self.__expression.accept(self._visitor)
            self.__expression.to_code_generation()
            if type(self.__expression) == AstNumber or type(self.__expression) == AstBinary:
                self._visitor.add_code('\tpop\t{r2}\n')
            else:
                self._visitor.add_code('\tpop\t{r3}\n')
                self._visitor.add_code('\tldr\tr2, [r7, r3]\n')
                
            self._visitor.add_code('\tpop\t{r1}\n')
            self._visitor.add_code('\tstr\tr2, [r7, r1]\n')
            
        #Array type to Array type
        elif type(self.__location.get_type()) == Array or type(self.__location.get_type()) == Record:
            self.__location.accept(self._visitor)
            self.__location.to_code_generation()
            self._visitor.add_code('\tpop\t{r1}\n')
            self._visitor.add_code('\tpush\t{r1}\n')
            
            self.__expression.accept(self._visitor)
            self.__expression.to_code_generation()
            self._visitor.add_code('\tpop\t{r2}\n')
            
            self._visitor.add_code('\tpop\t{r1}\n')
            size = self.__location.get_type().get_size()
            index = 0
            while index < size:
                self._visitor.add_code('\tadd\tr3, r1, #' + str(index) + '\n')
                self._visitor.add_code('\tadd\tr4, r2, #' + str(index) + '\n')
                self._visitor.add_code('\tldr\tr5, [r7, r4]\n')
                self._visitor.add_code('\tstr\tr5, [r7, r3]\n')
                index += 4
            
        #print 'generate assign ends'
        self._visitor.add_code('\t.ltorg\n')
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_code_generation()
    
    """
        This function will generate the code for Assign node in AST
        r7 is used to store the base address
        location_address_register is used to store the start address offset of the variable in location
        expression_value_register is used to store the value of expression or the start address offset of the variable 
        temporary_register is used to store the temporary variable in expression
        
    """
    def to_improved_code_generation(self):
        #print 'generate assign starts'
        #Integer type to Integer type
        if type(self.__location.get_type()) == Integer:
            self.__location.accept(self._visitor)
            location_address = self.__location.to_improved_code_generation()
            location_address_register = self._visitor.alloc_register()
            if location_address < 0:
                self._visitor.add_main_code('\tpop\t{' + location_address_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + location_address_register + ', =' + str(location_address) + '\n')
                
            self.__expression.accept(self._visitor)
            
            if type(self.__expression) == AstNumber:
                const_value = self.__expression.to_improved_code_generation()
                expression_value_register = self._visitor.alloc_register()
                self._visitor.add_main_code('\tldr\t' + expression_value_register + ', =' + str(const_value) + '\n')
            elif type(self.__expression) == AstBinary:
                self.__expression.to_improved_code_generation()
                expression_value_register = self._visitor.alloc_register()
                self._visitor.add_main_code('\tpop\t{' + expression_value_register + '}\n')
            else:
                temporary_register = self._visitor.alloc_register()
                expression_address = self.__expression.to_improved_code_generation()
                expression_value_register = self._visitor.alloc_register()
                if expression_address < 0:
                    self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
                 
                variable_type = self.__expression
                if type(variable_type) == FunctionCall:
                    self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [r7, ' + temporary_register + ']\n') 
                else:
                    while type(variable_type) != AstVariable:
                        variable_type = variable_type.get_location()
                    if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                        self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [fp, -' + temporary_register + ']\n')
                    else:
                        self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [r7, ' + temporary_register + ']\n') 
                self._visitor.free_register(temporary_register)
                
            self._visitor.add_main_code('\tstr\t' + expression_value_register + ', [r7, ' + location_address_register + ']\n')
            self._visitor.free_register(expression_value_register)
            self._visitor.free_register(location_address_register)
            
        #Array type to Array type or Record to Record type
        elif type(self.__location.get_type()) == Array or type(self.__location.get_type()) == Record:
            self.__location.accept(self._visitor)
            location_address = self.__location.to_improved_code_generation()
            location_address_register = self._visitor.alloc_register()
            if location_address < 0:
                self._visitor.add_main_code('\tpop\t{' + location_address_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + location_address_register + ', =' + str(location_address) + '\n')
                
            self.__expression.accept(self._visitor)
            
            if type(self.__expression) == AstNumber:
                const_value = self.__expression.to_improved_code_generation()
                expression_value_register = self._visitor.alloc_register()
                self._visitor.add_main_code('\tldr\t' + expression_value_register + ', =' + str(const_value) + '\n')
            elif type(self.__expression) == AstBinary:
                self.__expression.to_improved_code_generation()
                expression_value_register = self._visitor.alloc_register()
                self._visitor.add_main_code('\tpop\t{' + expression_value_register + '}\n')
            else:
                temporary_register = self._visitor.alloc_register()
                expression_value_register = self._visitor.alloc_register()
                expression_address = self.__expression.to_improved_code_generation()
                if expression_address < 0:
                    self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
                 
                variable_type = self.__expression
                while type(variable_type) != AstVariable:
                    variable_type = variable_type.get_location()
                if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                    self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [fp, -' + temporary_register + ']\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [r7, ' + temporary_register + ']\n') 
                self._visitor.free_register(temporary_register)
            
            size = self.__location.get_type().get_size()
            index = 0
            while index < size:
                temporary_register1 = self._visitor.alloc_register()
                temporary_register2 = self._visitor.alloc_register()
                self._visitor.add_main_code('\tadd\t' + temporary_register1 + ',' + location_address_register + ', #' + str(index) + '\n')
                self._visitor.add_main_code('\tadd\t' + temporary_register2 + ',' + expression_value_register + ', #' + str(index) + '\n')
                self._visitor.add_main_code('\tldr\t' + temporary_register2 + ', [r7, ' + temporary_register2 + ']\n')
                self._visitor.add_main_code('\tldr\t' + temporary_register2 + ', [r7, ' + temporary_register1 + ']\n')
                self._visitor.free_register(temporary_register1)
                self._visitor.free_register(temporary_register2)
                index += 4
            self._visitor.free_register(expression_value_register)
            self._visitor.free_register(location_address_register)
            
        #print 'generate assign ends'
        self._visitor.add_ltorg()
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_improved_code_generation()
            
    def print_string(self):
        print 'assign'
      
      
#########################################################################
## Read - This class is a derived class from Instruction to represent the 
##            read instruction.
##             
#########################################################################

class Read( Instruction ):
    def __init__(self, location):
        self.__location = location
        super(Read, self).__init__()
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Read:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'location =>\n')
        self.__location.accept(self._visitor)
        self.__location.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_asc_output()
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Read\",shape=box]\n')
        self.__location.accept(self._visitor)
        self.__location.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__location)) + ' [label=\"location\"]\n')
            
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_dot_output()
            self._visitor.add_semantic_output('{rank=same;_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.get_next_instruction())) + \
            ' [label=\"next\"]}\n')
        
    def to_interpret(self):
        #print 'interpret read starts'
        try:
            value = int(raw_input())
        except Exception:
            print 'error: you need to input an integer'
            exit()
        self.__location.accept(self._visitor)
        self.__location.to_interpret()
        variable_box = self._visitor.pop_stack()
        variable_box.set_value(value)
        self._visitor.reset_environment()
        #print 'interpret read ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_interpret()
        
    """
        This function will generate the code for Read node in AST
        r2 is used to store the location address offset
        r0 is used to set the first argument of scanf
        r1 is used to set the second argument of scanf 
        
    """
    def to_code_generation(self):
        #print 'generate read starts'
        self.__location.accept(self._visitor)
        self.__location.to_code_generation()
        self._visitor.add_code('\tpop\t{r2}\n')
        self._visitor.add_code('\tadd\tr1, r7, r2\n')
        self._visitor.add_code('\tldr\tr0, scanformatpointer\n')
        self._visitor.add_code('\tbl\tscanf\n')
        #print 'generate read ends'
        self._visitor.add_code('\t.ltorg\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_code_generation()
    
    """
        This function will generate the code for Read node in AST
        r7 is used to store the base address
        location_address_register is used to store the start address offset of the variable in location
        
    """
    def to_improved_code_generation(self):
        #print 'generate read starts'
        self.__location.accept(self._visitor)
        location_address = self.__location.to_improved_code_generation()
        location_address_register = self._visitor.alloc_register()
        if location_address < 0:
            self._visitor.add_main_code('\tldr\t' + location_address_register + ', =' + str(location_address) + '\n')
        else:
            self._visitor.add_main_code('\tpop\t{' + location_address_register + '}\n')
        self._visitor.add_main_code('\tadd\tr1, r7, ' + location_address_register + '\n')
        
        self._visitor.generate_scan_label()
        self._visitor.add_main_code('\tldr\tr0, scanformatpointer\n')
        self._visitor.add_main_code('\tbl\tscanf\n')
        #print 'generate read ends'
        self._visitor.free_register(location_address_register)
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_improved_code_generation()
           
    def print_string(self):
        print 'read'
        
        
#########################################################################
## If - This class is a derived class for Instruction to represent the 
##            if instruction.
##             
#########################################################################

class If( Instruction ):
    def __init__(self, condition, true_instruction, false_instruction = None):
        self.__condition = condition
        self.__true_instruction = true_instruction
        self.__false_instruction = false_instruction
        super(If, self).__init__()
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'If:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation  + 'condition =>\n')
        self.__condition.accept(self._visitor)
        self.__condition.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation  + 'instructions =>\n')
        self.__true_instruction.accept(self._visitor)
        self.__true_instruction.to_asc_output()
        if self.__false_instruction != None:
            self._visitor.add_semantic_output('  ' * indentation  + 'instructions =>\n')
            self.__false_instruction.accept(self._visitor)
            self.__false_instruction.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_asc_output()
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"If\",shape=box]\n')
        self.__condition.accept(self._visitor)
        self.__condition.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__condition)) + ' [label=\"condition\"]\n')
        self.__true_instruction.accept(self._visitor)
        self.__true_instruction.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__true_instruction)) + ' [label=\"true\"]\n')
        if self.__false_instruction != None:
            self.__false_instruction.accept(self._visitor)
            self.__false_instruction.to_dot_output()
            self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__false_instruction)) + ' [label=\"false\"]\n')
            
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_dot_output()
            self._visitor.add_semantic_output('{rank=same;_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.get_next_instruction())) + \
            ' [label=\"next\"]}\n')
            
    def to_interpret(self):
        #print 'interpret if starts'
        self.__condition.accept(self._visitor)
        self.__condition.to_interpret()
        #get the condition value from the stack
        condition_value = self._visitor.pop_stack()
        
        if condition_value == 1:
            self.__true_instruction.accept(self._visitor)
            self.__true_instruction.to_interpret()
        else:
            if self.__false_instruction != None:
                self.__false_instruction.accept(self._visitor)
                self.__false_instruction.to_interpret()
        #print 'interpret if ends'
            
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_interpret()
        
    """
        This function will generate the code for If object in AST
        r2 is used to store the condition value
        
    """
    def to_code_generation(self):
        #print 'generate If starts'
        self.__condition.accept(self._visitor)
        self.__condition.to_code_generation()
        #we load the value of the condition to r2
        self._visitor.add_code('\tpop\t{r2}\n')
        self._visitor.add_code('\tcmp\tr2, #0\n')
        #generate a new end label
        end_label = self._visitor.generate_end_label()
        
        #if the false instruction exists, we need to generate a new false label
        if self.__false_instruction != None:
            false_label = self._visitor.generate_false_label()
            self._visitor.add_code('\tbeq\t' + false_label + '\n')
        
        else:
            self._visitor.add_code('\tbeq\t' + end_label + '\n')
            
        self.__true_instruction.accept(self._visitor)
        self.__true_instruction.to_code_generation()
        self._visitor.add_code('\tb\t' + end_label + '\n')
        
        #if the false instruction exists, we need to generate the code for the false instruction
        if self.__false_instruction != None:
            self._visitor.add_code(false_label + ':\n')
            self.__false_instruction.accept(self._visitor)
            self.__false_instruction.to_code_generation()
        
        self._visitor.add_code(end_label + ':\n')
        #print 'generate If ends'
        self._visitor.add_code('\t.ltorg\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_code_generation()
            
    """
        This function will generate the code for If object in AST
        condition_register is used to store the condition value
        
    """
    def to_improved_code_generation(self):
        #print 'generate If starts'
        self.__condition.accept(self._visitor)
        condition_register = self.__condition.to_improved_code_generation()
        #we load the value of the condition to r2
        self._visitor.add_main_code('\tcmp\t' + condition_register + ', #0\n')
        self._visitor.free_register(condition_register)
        #generate a new end label
        end_label = self._visitor.generate_end_label()
        
        #if the false instruction exists, we need to generate a new false label
        if self.__false_instruction != None:
            false_label = self._visitor.generate_false_label()
            self._visitor.add_main_code('\tbeq\t' + false_label + '\n')
        
        else:
            self._visitor.add_main_code('\tbeq\t' + end_label + '\n')
            
        self.__true_instruction.accept(self._visitor)
        self.__true_instruction.to_improved_code_generation()
        self._visitor.add_main_code('\tb\t' + end_label + '\n')
        
        #if the false instruction exists, we need to generate the code for the false instruction
        if self.__false_instruction != None:
            self._visitor.add_main_code(false_label + ':\n')
            self.__false_instruction.accept(self._visitor)
            self.__false_instruction.to_improved_code_generation()
            self._visitor.add_main_code('\tb\t' + end_label + '\n')
        
        self._visitor.add_main_code(end_label + ':\n')
        #print 'generate If ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_improved_code_generation()
    
    def print_string(self):
        print 'if'
        
        
#########################################################################
## Repeat - This class is a derived class for Instruction to represent the 
##            repeat instruction.
##             
#########################################################################

class Repeat( Instruction ):
    def __init__(self, condition, instruction):
        self.__condition = condition
        self.__instruction = instruction
        super(Repeat, self).__init__()
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Repeat:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'condition =>\n')
        self.__condition.accept(self._visitor)
        self.__condition.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'instructions =>\n')
        self.__instruction.accept(self._visitor)
        self.__instruction.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_asc_output()
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Repeat\",shape=box]\n')
        self.__condition.accept(self._visitor)
        self.__condition.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__condition)) + ' [label=\"condition\"]\n')
        self.__instruction.accept(self._visitor)
        self.__instruction.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__instruction)) + ' [label=\"instructions\"]\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_dot_output()
            self._visitor.add_semantic_output('{rank=same;_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.get_next_instruction())) + \
            ' [label=\"next\"]}\n')
        
    def to_interpret(self):
        #print 'interpret Repeat starts'
        condition_value = 0
        while not condition_value:
            self.__instruction.accept(self._visitor)
            self.__instruction.to_interpret()
            self.__condition.accept(self._visitor)
            self.__condition.to_interpret()
            #get the condition value from the stack
            condition_value = self._visitor.pop_stack()
        #print 'interpret Repeat ends'
            
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_interpret()
    
    """
        This function will generate the code for Repeat object in AST
        r2 is used to store the condition value
        
    """
    def to_code_generation(self):
        #print 'generate repeat starts'
        #generate a new repeat label
        repeat_label = self._visitor.generate_repeat_label()
        self._visitor.add_code(repeat_label + ':\n')
        self.__instruction.accept(self._visitor)
        self.__instruction.to_code_generation()
        self.__condition.accept(self._visitor)
        self.__condition.to_code_generation()
        
        #we load the value of the condition to r1
        self._visitor.add_code('\tpop\t{r2}\n')
        self._visitor.add_code('\tcmp\tr2, #0\n')
        self._visitor.add_code('\tbeq\t' + repeat_label + '\n')
        #print 'generate repeat ends'
        self._visitor.add_code('\t.ltorg\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_code_generation()
            
    """
        This function will generate the code for Repeat object in AST
        r2 is used to store the condition value
        
    """
    def to_improved_code_generation(self):
        #print 'generate repeat starts'
        
        #generate a new repeat label
        repeat_label = self._visitor.generate_repeat_label()
        self._visitor.add_main_code(repeat_label + ':\n')
        self.__instruction.accept(self._visitor)
        self.__instruction.to_improved_code_generation()
        self.__condition.accept(self._visitor)
        condition_register = self.__condition.to_improved_code_generation()
        
        #we load the value of the condition to r1
        self._visitor.add_main_code('\tcmp\t' + condition_register + ', #0\n')
        self._visitor.add_main_code('\tbeq\t' + repeat_label + '\n')
        #print 'generate repeat ends'
        self._visitor.free_register(condition_register)
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_improved_code_generation()
    
    def print_string(self):
        print 'repeat'
        
 
#########################################################################
## Write - This class is a derived class from Instruction to represent the 
##            write instruction.
##             
#########################################################################

class Write( Instruction ):
    def __init__(self, expression):
        self.__expression = expression
        super(Write, self).__init__()
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Write:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'expression =>\n')
        self.__expression.accept(self._visitor)
        self.__expression.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_asc_output()
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Write\",shape=box]\n')
        self.__expression.accept(self._visitor)
        self.__expression.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression)) + ' [label=\"expression\"]\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_dot_output()
            self._visitor.add_semantic_output('{rank=same;_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.get_next_instruction())) + \
            ' [label=\"next\"]}\n')
    
    def to_interpret(self):
        #print 'interpret write starts'
        self.__expression.accept(self._visitor)
        self.__expression.to_interpret()
        expression_box = self._visitor.pop_stack()
        if type(expression_box) == IntegerBox:
            write_value = expression_box.get_value()
        else:
            write_value = expression_box
        print write_value
        self._visitor.reset_environment()
        #print 'interpret write ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_interpret()
    
    """
        This function will generate the code for Write object in AST
        r2 is used to store the expression value
        r0 is used to set the first argument of printf
        r1 is used to set the second argument of printf 
        
    """
    def to_code_generation(self):
        #print 'generate write starts'
        self.__expression.accept(self._visitor)
        self.__expression.to_code_generation()
        if type(self.__expression) == AstNumber or type(self.__expression) == AstBinary:
            self._visitor.add_code('\tpop\t{r2}\n')
        else:
            self._visitor.add_code('\tpop\t{r3}\n')
            self._visitor.add_code('\tldr\tr2, [r7, r3]\n')
        self._visitor.add_code('\tmov\tr1, r2\n')
        self._visitor.add_code('\tldr\tr0, printformatpointer\n')
        self._visitor.add_code('\tbl\tprintf\n')
        #print 'generate write ends'
        self._visitor.add_code('\t.ltorg\n')
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_code_generation()
            
    """
        This function will generate the code for Write object in AST
        expression_value_register is used to store the expression value
        
    """
    def to_improved_code_generation(self):
        #print 'generate write starts'
        self.__expression.accept(self._visitor)
        
        if type(self.__expression) == AstNumber:
            const_value = self.__expression.to_improved_code_generation()
            expression_value_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tldr\t' + expression_value_register + ', =' + str(const_value) + '\n')
        elif type(self.__expression) == AstBinary:
            self.__expression.to_improved_code_generation()
            expression_value_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tpop\t{' + expression_value_register + '}\n')
        else:   
            expression_address = self.__expression.to_improved_code_generation()
            temporary_register = self._visitor.alloc_register()
            expression_value_register = self._visitor.alloc_register()
            if expression_address < 0:
                self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
             
            variable_type = self.__expression
            while type(variable_type) != AstVariable:
                variable_type = variable_type.get_location()
            if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [fp, -' + temporary_register + ']\n')
            else:
                self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [r7, ' + temporary_register + ']\n') 
            self._visitor.free_register(temporary_register)
        
        self._visitor.generate_print_label()
        self._visitor.add_main_code('\tmov\tr1, ' + expression_value_register + '\n')
        self._visitor.add_main_code('\tldr\tr0, printformatpointer\n')
        self._visitor.add_main_code('\tbl\tprintf\n')
        
        self._visitor.free_register(expression_value_register)
        
        #print 'generate write ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_improved_code_generation()
            
    def print_string(self):
        print 'write'
        

#########################################################################
## ProcedureCall - This class is a derived class from Instruction to represent the 
##            function call instruction.
##             
#########################################################################
class ProcedureCall( Instruction ):
    def __init__(self, formal_node_array, table_entry, procedure_name):
        self.__formal_node_array = formal_node_array
        self.__table_entry = table_entry
        self.__procedure_name = procedure_name
        super(ProcedureCall, self).__init__()
    
    def get_table_entry(self):
        return self.__table_entry
        
    def to_asc_output(self):
        pass
    
    def to_dot_output(self):
        pass
    
    def get_parameter_name(self, parameter_number):
        index = parameter_number - 1
        if type(self.__formal_node_array[index]) == AstVariable:
            return self.__formal_node_array[index].get_variable_name()
        else:
            variable_type = self.__formal_node_array[index]
            while type(variable_type) != AstVariable:
                variable_type = variable_type.get_location()
            return variable_type.get_variable_name()
        
    #TODO:
    def to_interpret(self):
        #print 'interpret ProcedureCall starts'
        
        #create a new environment first
        current_environment = {}
        dictionary = self.__table_entry.get_scope().get_table()
        parameter_number = 0
        for key, value in dictionary.items():
            #we need to build the environment for the variable entry
            if type(value) == FormalVariable:
                parameter_number += 1
            if isinstance(value, Variable):
                variable_type = value.get_type()
                variable_type.accept(self._visitor)
                #if it is a local variable, we just need to initialize it 
                if type(value) == LocalVariable:
                    current_environment[key] = variable_type.to_environment()
                
                #if it is a global variable, we need to set the global environemt box to the new environment
                elif type(value) == GlobalVariable:
                    current_environment[key] = self._visitor.get_global_environment_box(key)
                    
                #if it is a formal variable, if the type of the variable is an integer, we need to copy it
                #if the type of the variable is a Record or Array, it is passed by reference
                elif type(value) == FormalVariable:
                    if type(value.get_type()) == Integer:
                        if type(self.__formal_node_array[parameter_number-1]) == AstNumber:
                            value = self.__formal_node_array[parameter_number-1].get_constant_value()
                            current_environment[key] = variable_type.to_environment()
                            current_environment[key].set_value(value)
                        elif type(self.__formal_node_array[parameter_number-1]) == AstBinary:
                            self.__formal_node_array[parameter_number-1].accept(self._visitor)
                            self.__formal_node_array[parameter_number-1].to_interpret()
                            value = self._visitor.pop_stack()
                            current_environment[key] = variable_type.to_environment()
                            current_environment[key].set_value(value)
                        else:
                            variable_name = self.get_parameter_name(parameter_number)
                            current_environment[key] = copy.copy(self._visitor.get_global_environment_box(variable_name))
                    else:
                        #find the reference box in global scope
                        variable_name = self.get_parameter_name(parameter_number)
                        reference_box = self._visitor.get_global_environment_box(variable_name)
                        current_environment[key] = DereferenceBox(reference_box)

        self._visitor.create_environment(current_environment)
        
        #start interpret the body of the function
        self.__table_entry.get_body_ast().accept(self._visitor)
        self.__table_entry.get_body_ast().to_interpret()
        
        self._visitor.delete_environmnet()
        #print 'interpret ProcedureCall ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_interpret()
    
    def to_code_generation(self):
        pass
    
    def to_improved_code_generation(self):
        #print 'improved code generation ProcedureCall starts'
        
        #we need to store the formal parameters and the return address first
        parameter_number = 0
        for formal_node in self.__formal_node_array:
            formal_node.accept(self._visitor)
            parameter_number += 1
            #push the register on stack to protect the value if it is not used now
            if self._visitor.is_free_register('r' + str(parameter_number - 1)) == False:
                self._visitor.add_main_code('\tpush\t{r' + str(parameter_number - 1) + '}\n')
            
            if type(formal_node) == AstNumber:
                formal_value = formal_node.to_improved_code_generation()
                self._visitor.add_main_code('\tmov\tr' + str(parameter_number - 1) + ', #' + str(formal_value) + '\n')
            elif type(formal_node) == AstBinary:
                formal_node.to_improved_code_generation()
                self._visitor.add_main_code('\tpop\t{r' + str(parameter_number - 1) + '}\n')
            else:
                temporary_register = self._visitor.alloc_register()
                expression_address = formal_node.to_improved_code_generation()
                if expression_address < 0:
                    self._visitor.add_main_code('\tpop\t{r' + str(parameter_number - 1) + '}\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
                    self._visitor.add_main_code('\tldr\tr' + str(parameter_number - 1) + ', [r7, ' + temporary_register + ']\n')
                    self._visitor.free_register(temporary_register)
        
        self._visitor.add_main_code('\tbl\t' + self.__procedure_name + '\n')
        
        #pop the stack to get the register 
        register_number = len(self.__formal_node_array) - 1
        while register_number >= 0: 
            if self._visitor.is_free_register('r' + str(register_number)) == False:
                self._visitor.add_main_code('\tpop\t{r' + str(register_number) + '}\n')
            register_number -= 1
        
        #generate a label for Procedure
        self._visitor.generate_function_label()
        label_name = self.__procedure_name
        self._visitor.add_function_code(label_name + ':\n')
        self._visitor.add_function_code('\tstmfd\tsp!, {fp, lr}\n')
        self._visitor.add_function_code('\tadd\tfp, sp, #4\n')
        
        #get the total space to allocate in stack first
        dictionary = self.__table_entry.get_scope().get_table()
        parameter_number = 0
        local_variable_number = 0
        for key, value in dictionary.items():
            if type(value) == FormalVariable:
                parameter_number += 1
            elif type(value) == LocalVariable:
                local_variable_number += 1
        
        space = 4 + (parameter_number + local_variable_number) * 4
        self._visitor.add_function_code('\tsub\tsp, sp, #' + str(space) + '\n')
        
        #we need to set the address for local variable and formal variable respectively    
        current_parameter_number = 0
        current_local_variable_number = 0
        for key, value in dictionary.items():
            #if it is a local variable, we just need to initialize it and set the address offset from the frame pointer
            if type(value) == LocalVariable:
                current_local_variable_number += 1
                offset = 4 + parameter_number * 4 + current_local_variable_number * 4
                value.set_address_offset(offset)
            
            #if it is a formal variable, if the type of the variable is an integer, we need to copy it
            #if the type of the variable is a Record or Array, it is passed by reference
            elif type(value) == FormalVariable:
                current_parameter_number += 1
                
                if type(value.get_type()) == Integer:
                    offset = 4 + current_parameter_number * 4
                    value.set_address_offset(offset)
                    self._visitor.add_function_code('\tstr\tr' + str(current_parameter_number -1) + ', [fp, #-' + str(offset) + ']\n')
                        
                else:
                    pass
                
        self._visitor.set_in_function()
        
        #start interpret the body of the function
        self.__table_entry.get_body_ast().accept(self._visitor)
        self.__table_entry.get_body_ast().to_improved_code_generation()
        
        self._visitor.set_out_function()
        
        #print 'improved code generation ProcedureCall ends'
        
        if self.get_next_instruction() != None:
            self.get_next_instruction().accept(self._visitor)
            self.get_next_instruction().to_improved_code_generation()
     
    
#########################################################################
## Expression - This class is a derived class from Node to represent the 
##            expression categories.
##             
#########################################################################

class Expression( Node ):
    def __init__(self):
        self.__type_pointer = None
        super(Expression, self).__init__()
        
    def set_type(self, type_pointer):
        self.__type_pointer = type_pointer
    
    def get_type(self):
        return self.__type_pointer   
    
       
#########################################################################
## AstNumber - This class is a derived class from expression to represent 
## an constant number node in the abstract syntax tree
##             
#########################################################################

class AstNumber( Expression ):
    def __init__(self, table_entry, number_value):
        self.__table_entry = table_entry
        self.__number_value = number_value
        super(AstNumber, self).__init__()
        
    def get_table_entry(self):
        return self.__table_entry
    
    def get_constant_value(self):
        return self.__table_entry.get_value()
    
    def set_constant_value(self, value):
        self.__table_entry.set_value(value)
        self.__number_value = value
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Number:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'value =>\n')
        self.__table_entry.accept(self._visitor)
        self.__table_entry.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Number\",shape=box]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)+id(self.__table_entry)) + ' [label=\"' + str(self.__number_value) + '\",shape=diamond]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self)+id(self.__table_entry)) + ' [label=\"ST\"]\n')
        
    def to_interpret(self):
        #print 'interpret number ' + str(self.get_constant_value()) + ' starts'
        self._visitor.push_stack(self.get_constant_value())
        #print 'interpret number ' + str(self.get_constant_value()) + ' ends'
    
    """
        This function will generate the code for Number node in AST
        r2 is used to store the number value
        
    """
    def to_code_generation(self):
        #print 'generate number ' + str(self.get_constant_value()) + ' starts'
        #overflow is handled as modulo of the 2^32
        new_value = self.get_constant_value() % 4294967296;
        self._visitor.add_code('\tldr\tr2, =' + str(new_value) + '\n')
        self._visitor.add_code('\tpush\t{r2}\n')
        #print 'generate number ' + str(self.get_constant_value()) + ' ends'
        
    """
        This function will generate the code for Number node in AST
        r2 is used to store the number value
        
    """
    def to_improved_code_generation(self):
        #print 'generate number ' + str(self.get_constant_value()) + ' starts'
        #overflow is handled as modulo of the 2^32
        new_value = self.get_constant_value() % 4294967296;
        #print 'generate number ' + str(self.get_constant_value()) + ' ends'
        return new_value;
        
        
    def print_string(self):
        print 'ast number'
        
          
#########################################################################
## AstBinary - This class is a derived class from expression to represent 
## the binary expression node in the abstract syntax tree
##             
#########################################################################

class AstBinary( Expression ):
    def __init__(self, operator, expression_left, expression_right):
        self.__operator = operator
        self.__expression_left = expression_left
        self.__expression_right = expression_right
        super(AstBinary, self).__init__()
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Binary:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'Binary (' + self.__operator + '):\n')
        self._visitor.add_semantic_output('  ' * indentation + 'left =>\n')
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'right =>\n')
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"' + self.__operator + '\",shape=box]\n')
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression_left)) + ' [label=\"left\"]\n')
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression_right)) + ' [label=\"right\"]\n')

    def to_interpret(self):
        #print 'interpret binary starts'
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_interpret()
        expression_left_box = self._visitor.pop_stack()
        if type(expression_left_box) == IntegerBox:
            value_left = expression_left_box.get_value()
        else:
            value_left = expression_left_box
        self._visitor.reset_environment()
        
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_interpret()
        expression_right_box = self._visitor.pop_stack()
        if type(expression_right_box) == IntegerBox:
            value_right = expression_right_box.get_value()
        else:
            value_right = expression_right_box
        
        binary_value = None
        if self.__operator == '+':
            binary_value = value_left + value_right
        elif self.__operator == '-':
            binary_value = value_left - value_right 
        elif self.__operator == '*':
            binary_value = value_left * value_right 
        elif self.__operator == 'DIV':
            if value_right == 0:
                print 'error: the expression on the right-hand side of the DIV cannot evaluate to zero at line: ' + str(self.__expression_right.get_line()) + ' position: (' \
                + str(self.__expression_right.get_start_position()) + ', ' + str(self.__expression_right.get_end_position()) + ')'
                exit()
            binary_value = value_left / value_right 
        elif self.__operator == 'MOD':
            if value_right == 0:
                print 'error: the expression on the right-hand side of the MOD cannot evaluate to zero at line: ' + str(self.__expression_right.get_line()) + ' position: (' \
                + str(self.__expression_right.get_start_position()) + ', ' + str(self.__expression_right.get_end_position()) + ')'
                exit()
            binary_value = value_left % value_right 
            
        self._visitor.push_stack(binary_value)
        self._visitor.reset_environment()
        #print 'interpret binary ends'
    
    """
        This function will generate the code for Binary node in AST
        r1 is used to store the left expression value
        r2 is used to store the right expression value
        r3 is used to store the final result value
    """
    def to_code_generation(self):
        #print 'generate binary starts'
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_code_generation()
        #we load the value of the left expression to r1, and push this value to stack
        if type(self.__expression_left) == AstNumber or type(self.__expression_left) == AstBinary:
            self._visitor.add_code('\tpop\t{r1}\n')
        else:
            self._visitor.add_code('\tpop\t{r2}\n')
            self._visitor.add_code('\tldr\tr1, [r7, r2]\n')
        self._visitor.add_code('\tpush\t{r1}\n')
            
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_code_generation()
        #we load the value of the right expression to r2
        if type(self.__expression_right) == AstNumber or type(self.__expression_right) == AstBinary:
            self._visitor.add_code('\tpop\t{r2}\n')
        else:
            self._visitor.add_code('\tpop\t{r3}\n')
            self._visitor.add_code('\tldr\tr2, [r7, r3]\n')
        
        self._visitor.add_code('\tpop\t{r1}\n')
        #generate the code to perform the operation and set the result to r3
        if self.__operator == '+':
            self._visitor.add_code('\tadd\tr3, r1, r2\n')
        elif self.__operator == '-':
            self._visitor.add_code('\tsub\tr3, r1, r2\n')
        elif self.__operator == '*':
            self._visitor.add_code('\tmul\tr3, r1, r2\n')
        elif self.__operator == 'DIV':
            self._visitor.add_code('\tmov\tr0, r1\n')
            self._visitor.add_code('\tmov\tr1, r2\n')
            self._visitor.add_code('\tcmp\tr2, #0\n')
            self._visitor.add_code('\tblne\t__aeabi_idiv\n')
            
            #if the right expression value is 0, print the error and exist the program
            line = self.__expression_right.get_line()
            start_position = self.__expression_right.get_start_position()
            end_position = self.__expression_right.get_end_position()
            self._visitor.add_code('\tldreq\tr1, =' + str(line) + '\n')
            self._visitor.add_code('\tldreq\tr2, =' + str(start_position) + '\n')
            self._visitor.add_code('\tldreq\tr3, =' + str(end_position) + '\n')
            self._visitor.add_code('\tldreq\tr0, diverrorformatpointer\n')
            self._visitor.add_code('\tbleq\tprintf\n')
            self._visitor.add_code('\tmoveq\tr0, #' + str(1) + '\n')
            self._visitor.add_code('\tbleq\texit\n')
        
            self._visitor.add_code('\tmov\tr3, r0\n')
        elif self.__operator == 'MOD':
            self._visitor.add_code('\tmov\tr0, r1\n')
            self._visitor.add_code('\tmov\tr1, r2\n')
            self._visitor.add_code('\tcmp\tr2, #0\n')
            self._visitor.add_code('\tblne\t__aeabi_idivmod\n')
            
            #if the right expression value is 0, print the error and exist the program
            line = self.__expression_right.get_line()
            start_position = self.__expression_right.get_start_position()
            end_position = self.__expression_right.get_end_position()
            self._visitor.add_code('\tldreq\tr1, =' + str(line) + '\n')
            self._visitor.add_code('\tldreq\tr2, =' + str(start_position) + '\n')
            self._visitor.add_code('\tldreq\tr3, =' + str(end_position) + '\n')
            self._visitor.add_code('\tldreq\tr0, moderrorformatpointer\n')
            self._visitor.add_code('\tbleq\tprintf\n')
            self._visitor.add_code('\tmoveq\tr0, #' + str(1) + '\n')
            self._visitor.add_code('\tbleq\texit\n')
            
            self._visitor.add_code('\tmov\tr3, r1\n')
        
        #push the result value on the stack
        self._visitor.add_code('\tpush\t{r3}\n')
        #print 'generate binary ends'
    
    """
        This function will generate the improved code for Binary node in AST
        expression_value_left_register is used to store the left expression value
        expression_value_right_register is used to store the right expression value
        result_value_register is used to store the final result value
    """    
    def to_improved_code_generation(self):
        #print 'generate binary starts'
        
        self.__expression_left.accept(self._visitor)
        if type(self.__expression_left) == AstNumber:
            left_value = self.__expression_left.to_improved_code_generation()
            expression_value_left_register = self._visitor.alloc_register()
        elif type(self.__expression_left) == AstBinary:
            self.__expression_left.to_improved_code_generation()
            expression_value_left_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tpop\t{' + expression_value_left_register + '}\n')
        else:
            temporary_register = self._visitor.alloc_register()
            expression_address = self.__expression_left.to_improved_code_generation()
            expression_value_left_register = self._visitor.alloc_register()
            if expression_address < 0:
                self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
             
            variable_type = self.__expression
            if type(variable_type) == FunctionCall:
                self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [r7, ' + temporary_register + ']\n') 
            else:
                while type(variable_type) != AstVariable:
                    variable_type = variable_type.get_location()
                if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                    self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [fp, -' + temporary_register + ']\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [r7, ' + temporary_register + ']\n') 
            self._visitor.free_register(temporary_register)
        
        self.__expression_right.accept(self._visitor)
        if type(self.__expression_right) == AstNumber:
            right_value = self.__expression_right.to_improved_code_generation()
            expression_value_right_register = self._visitor.alloc_register()
        elif type(self.__expression_right) == AstBinary:
            self.__expression_right.to_improved_code_generation()
            expression_value_right_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tpop\t{' + expression_value_right_register + '}\n')
        else:
            temporary_register = self._visitor.alloc_register()
            expression_address = self.__expression_right.to_improved_code_generation()
            expression_value_right_register = self._visitor.alloc_register()
            if expression_address < 0:
                self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
             
            variable_type = self.__expression
            if type(variable_type) == FunctionCall:
                self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', [r7, ' + temporary_register + ']\n') 
            else:
                while type(variable_type) != AstVariable:
                    variable_type = variable_type.get_location()
                if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                    self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', [fp, -' + temporary_register + ']\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', [r7, ' + temporary_register + ']\n') 
            self._visitor.free_register(temporary_register)
        
        #generate the code to perform the operation and set the result to r3
        result_value_register = self._visitor.alloc_register()
        if self.__operator == '+':
            if type(self.__expression_left) == AstNumber:
                self._visitor.add_main_code('\tadd\t' + result_value_register + ', ' + expression_value_right_register + ', #' + str(left_value) + '\n')
            elif type(self.__expression_right) == AstNumber:
                self._visitor.add_main_code('\tadd\t' + result_value_register + ', ' + expression_value_left_register + ', #' + str(right_value) + '\n')
            else:
                self._visitor.add_main_code('\tadd\t' + result_value_register + ', ' + expression_value_left_register + ',' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tpush\t{' + result_value_register + '}\n')
        
        elif self.__operator == '-':
            if type(self.__expression_left) == AstNumber:
                self._visitor.add_main_code('\trsb\t' + result_value_register + ', ' + expression_value_right_register + ', #' + str(left_value) + '\n')
            elif type(self.__expression_right) == AstNumber:
                self._visitor.add_main_code('\tsub\t' + result_value_register + ', ' + expression_value_left_register + ', #' + str(right_value) + '\n')
            else:
                self._visitor.add_main_code('\tsub\t' + result_value_register + ', ' + expression_value_left_register + ',' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tpush\t{' + result_value_register + '}\n')
        
        elif self.__operator == '*':
            if type(self.__expression_left) == AstNumber:
                self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', =' + str(left_value) + '\n')
            elif type(self.__expression_right) == AstNumber:
                self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', =' + str(right_value) + '\n')
            self._visitor.add_main_code('\tmul\t' + result_value_register + ', ' + expression_value_left_register + ',' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tpush\t{' + result_value_register + '}\n')
        
        
        #before calling the function aeabi_idiv, we need to store the numerator in register r0, 
        #store the denumerator in register r1. Thus, we need to move the value of r0 and r1 to another new two registers
        elif self.__operator == 'DIV':
            self._visitor.generate_div_error_label()
            
            #we need to move the value of r0 and r1 to another two new registers
            if self._visitor.is_free_register('r0') and self._visitor.is_free_register('r1'):
                pass
            elif self._visitor.is_free_register('r0') and not self._visitor.is_free_register('r1'):
                temp_register1 = self._visitor.alloc_register()
                if temp_register1 == 'r0':
                    temp_register1 = self._visitor.alloc_register()
                    self._visitor.free_register('r0')
                self._visitor.add_main_code('\tmov\t' + temp_register1 + ', r1\n')
            elif self._visitor.is_free_register('r1') and not self._visitor.is_free_register('r0'):
                temp_register0 = self._visitor.alloc_register()
                if temp_register0 == 'r1':
                    temp_register0 = self._visitor.alloc_register()
                    self._visitor.free_register('r1')
                self._visitor.add_main_code('\tmov\t' + temp_register0 + ', r0\n')
            else:
                temp_register0 = self._visitor.alloc_register()
                temp_register1 = self._visitor.alloc_register()
                self._visitor.add_main_code('\tmov\t' + temp_register0 + ', r0\n')
                self._visitor.add_main_code('\tmov\t' + temp_register1 + ', r1\n')

            if type(self.__expression_left) == AstNumber:
                self._visitor.add_main_code('\tmov\tr0, #' + str(left_value) + '\n')
                self._visitor.add_main_code('\tmov\tr1, ' + expression_value_right_register + '\n')
            elif type(self.__expression_right) == AstNumber:
                self._visitor.add_main_code('\tmov\tr0, ' + expression_value_left_register + '\n')
                self._visitor.add_main_code('\tmov\tr1, #' + str(right_value) + '\n')
                if right_value == 0:
                    print 'error: the expression on the right-hand side of the DIV cannot evaluate to zero at line: ' + str(self.__expression_right.get_line()) + ' position: (' \
                    + str(self.__expression_right.get_start_position()) + ', ' + str(self.__expression_right.get_end_position()) + ')'
                    exit()
            else:
                self._visitor.add_main_code('\tmov\tr0, ' + expression_value_left_register + '\n')
                self._visitor.add_main_code('\tmov\tr1, ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tcmp\tr1, #0\n')
            self._visitor.add_main_code('\tblne\t__aeabi_idiv\n')
            
            #if the right expression value is 0, print the error and exist the program
            line = self.__expression_right.get_line()
            start_position = self.__expression_right.get_start_position()
            end_position = self.__expression_right.get_end_position()
            self._visitor.add_main_code('\tldreq\tr1, =' + str(line) + '\n')
            self._visitor.add_main_code('\tldreq\tr2, =' + str(start_position) + '\n')
            self._visitor.add_main_code('\tldreq\tr3, =' + str(end_position) + '\n')
            self._visitor.add_main_code('\tldreq\tr0, diverrorformatpointer\n')
            self._visitor.add_main_code('\tbleq\tprintf\n')
            self._visitor.add_main_code('\tmoveq\tr0, #' + str(1) + '\n')
            self._visitor.add_main_code('\tbleq\texit\n')
            
            self._visitor.add_main_code('\tmov\t' + result_value_register + ', r0\n')
            self._visitor.add_main_code('\tpush\t{' + result_value_register + '}\n')
            
            #move the value back from temporary registers to r0 and r1
            if self._visitor.is_free_register('r0') and self._visitor.is_free_register('r1'):
                pass
            elif self._visitor.is_free_register('r0') and not self._visitor.is_free_register('r1'):
                self._visitor.add_main_code('\tmov\tr1, ' + temp_register1 + '\n')
                self._visitor.free_register(temp_register1)
            elif self._visitor.is_free_register('r1') and not self._visitor.is_free_register('r0'):
                self._visitor.add_main_code('\tmov\tr0, ' + temp_register0 + '\n')
                self._visitor.free_register(temp_register0)
            else:
                self._visitor.add_main_code('\tmov\tr0, ' + temp_register0 + '\n')
                self._visitor.add_main_code('\tmov\tr1, ' + temp_register1 + '\n')
                self._visitor.free_register(temp_register0)
                self._visitor.free_register(temp_register1)
            
        #before calling the function aeabi_idivmod, we need to store the numerator in register r0, 
        #store the denumerator in register r1. Thus, we need to move the value of r0 and r1 to another new two registers
        elif self.__operator == 'MOD':
            self._visitor.generate_mod_error_label()
            
            #we need to move the value of r0 and r1 to another two new registers
            if self._visitor.is_free_register('r0') and self._visitor.is_free_register('r1'):
                pass
            elif self._visitor.is_free_register('r0') and not self._visitor.is_free_register('r1'):
                temp_register1 = self._visitor.alloc_register()
                if temp_register1 == 'r0':
                    temp_register1 = self._visitor.alloc_register()
                    self._visitor.free_register('r0')
                self._visitor.add_main_code('\tmov\t' + temp_register1 + ', r1\n')
            elif self._visitor.is_free_register('r1') and not self._visitor.is_free_register('r0'):
                temp_register0 = self._visitor.alloc_register()
                if temp_register0 == 'r1':
                    temp_register0 = self._visitor.alloc_register()
                    self._visitor.free_register('r1')
                self._visitor.add_main_code('\tmov\t' + temp_register0 + ', r0\n')
            else:
                temp_register0 = self._visitor.alloc_register()
                temp_register1 = self._visitor.alloc_register()
                self._visitor.add_main_code('\tmov\t' + temp_register0 + ', r0\n')
                self._visitor.add_main_code('\tmov\t' + temp_register1 + ', r1\n')
            if not self._visitor.is_free_register('r2'):
                self._visitor.add_main_code('\tpush\t{r2}\n')
            
            if type(self.__expression_left) == AstNumber:
                self._visitor.add_main_code('\tmov\tr0, #' + str(left_value) + '\n')
                self._visitor.add_main_code('\tmov\tr1, ' + expression_value_right_register + '\n')
            elif type(self.__expression_right) == AstNumber:
                self._visitor.add_main_code('\tmov\tr0, ' + expression_value_left_register + '\n')
                self._visitor.add_main_code('\tmov\tr1, #' + str(right_value) + '\n')
                if right_value == 0:
                    print 'error: the expression on the right-hand side of the MOD cannot evaluate to zero at line: ' + str(self.__expression_right.get_line()) + ' position: (' \
                    + str(self.__expression_right.get_start_position()) + ', ' + str(self.__expression_right.get_end_position()) + ')'
                    exit()
            else:
                self._visitor.add_main_code('\tmov\tr0, ' + expression_value_left_register + '\n')
                self._visitor.add_main_code('\tmov\tr1, ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tcmp\tr1, #0\n')
            self._visitor.add_main_code('\tblne\t__aeabi_idivmod\n')
            
            #if the right expression value is 0, print the error and exist the program
            line = self.__expression_right.get_line()
            start_position = self.__expression_right.get_start_position()
            end_position = self.__expression_right.get_end_position()
            self._visitor.add_main_code('\tldreq\tr1, =' + str(line) + '\n')
            self._visitor.add_main_code('\tldreq\tr2, =' + str(start_position) + '\n')
            self._visitor.add_main_code('\tldreq\tr3, =' + str(end_position) + '\n')
            self._visitor.add_main_code('\tldreq\tr0, moderrorformatpointer\n')
            self._visitor.add_main_code('\tbleq\tprintf\n')
            self._visitor.add_main_code('\tmoveq\tr0, #' + str(1) + '\n')
            self._visitor.add_main_code('\tbleq\texit\n')
            
            if not self._visitor.is_free_register('r2'):
                self._visitor.add_main_code('\tpop\t{r2}\n')
            
            self._visitor.add_main_code('\tmov\t' + result_value_register + ', r1\n')
            self._visitor.add_main_code('\tpush\t{' + result_value_register + '}\n')
            
            #move the value back from temporary registers to r0 and r1
            if self._visitor.is_free_register('r0') and self._visitor.is_free_register('r1'):
                pass
            elif self._visitor.is_free_register('r0') and not self._visitor.is_free_register('r1'):
                self._visitor.add_main_code('\tmov\tr1, ' + temp_register1 + '\n')
                self._visitor.free_register(temp_register1)
            elif self._visitor.is_free_register('r1') and not self._visitor.is_free_register('r0'):
                self._visitor.add_main_code('\tmov\tr0, ' + temp_register0 + '\n')
                self._visitor.free_register(temp_register0)
            else:
                self._visitor.add_main_code('\tmov\tr0, ' + temp_register0 + '\n')
                self._visitor.add_main_code('\tmov\tr1, ' + temp_register1 + '\n')
                self._visitor.free_register(temp_register0)
                self._visitor.free_register(temp_register1)
                
            
        
        #push the result value on the stack
        self._visitor.free_register(expression_value_left_register)
        self._visitor.free_register(expression_value_right_register)
        self._visitor.free_register(result_value_register)
        #print 'generate binary ends'
        return -1;
    
    def print_string(self):
        print 'ast binary'  
        
        
#########################################################################
## FunctionCall - This class is a derived class from Expression to represent the 
##            function call instruction.
##             
#########################################################################

class FunctionCall( Expression ):
    def __init__(self, formal_node_array, table_entry, function_name):
        self.__formal_node_array = formal_node_array
        self.__table_entry = table_entry
        self.__function_name = function_name
        super(FunctionCall, self).__init__()
    
    def get_table_entry(self):
        return self.__table_entry
        
    def to_asc_output(self):
        pass
    
    def to_dot_output(self):
        pass
    
    def get_parameter_name(self, parameter_number):
        index = parameter_number - 1
        if type(self.__formal_node_array[index]) == AstVariable:
            return self.__formal_node_array[index].get_variable_name()
        else:
            variable_type = self.__formal_node_array[index]
            while type(variable_type) != AstVariable:
                variable_type = self.__formal_node_array[index].get_location()
            return variable_type.get_variable_name()
        
    #TODO:
    def to_interpret(self):
        #print 'interpret Function Call starts'
        
        #create a new environment first
        current_environment = {}
        dictionary = self.__table_entry.get_scope().get_table()
        parameter_number = 0
        for key, value in dictionary.items():
            #we need to build the environment for the variable entry
            if type(value) == FormalVariable:
                parameter_number += 1
            if isinstance(value, Variable):
                variable_type = value.get_type()
                variable_type.accept(self._visitor)
                #if it is a local variable, we just need to initialize it 
                if type(value) == LocalVariable:
                    current_environment[key] = variable_type.to_environment()
                
                #if it is a global variable, we need to set the global environemt box to the new environment
                elif type(value) == GlobalVariable:
                    current_environment[key] = self._visitor.get_global_environment_box(key)
                    
                #if it is a formal variable, if the type of the variable is an integer, we need to copy it
                #if the type of the variable is a Record or Array, it is passed by reference
                elif type(value) == FormalVariable:
                    if type(value.get_type()) == Integer:
                        if type(self.__formal_node_array[parameter_number-1]) == AstNumber:
                            value = self.__formal_node_array[parameter_number-1].get_constant_value()
                            current_environment[key] = variable_type.to_environment()
                            current_environment[key].set_value(value)
                        elif type(self.__formal_node_array[parameter_number-1]) == AstBinary:
                            self.__formal_node_array[parameter_number-1].accept(self._visitor)
                            self.__formal_node_array[parameter_number-1].to_interpret()
                            value = self._visitor.pop_stack()
                            current_environment[key] = variable_type.to_environment()
                            current_environment[key].set_value(value)
                        else:
                            variable_name = self.get_parameter_name(parameter_number)
                            current_environment[key] = copy.copy(self._visitor.get_global_environment_box(variable_name))
                    else:
                        #find the reference box in global scope
                        variable_name = self.get_parameter_name(parameter_number)
                        reference_box = self._visitor.get_global_environment_box(variable_name)
                        current_environment[key] = DereferenceBox(reference_box)

        self._visitor.create_environment(current_environment)
        
        #start interpret the body of the Procedure
        self.__table_entry.get_body_ast().accept(self._visitor)
        self.__table_entry.get_body_ast().to_interpret()
        
        #start interpret the return expression of the Procedure
        if self.__table_entry.get_return_ast() != None:
            if type(self.__table_entry.get_return_ast().get_type()) != Integer:
                print 'the return type of a procedure must be INTEGER at Line: ' + str(self.get_line()) + ' position: (' + str(self.get_start_position()) \
                + ', ' + str(self.get_end_position()) + ')'
                exit()
            self.__table_entry.get_return_ast().accept(self._visitor)
            self.__table_entry.get_return_ast().to_interpret()
        else:
            print 'function procedures must have a RETURN clause at Line: ' + str(self.get_line()) + ' position: (' + str(self.get_start_position()) \
             + ', ' + str(self.get_end_position()) + ')'
            exit()
        self._visitor.delete_environmnet()
        #print 'interpret Function Call ends'
    
    def to_code_generation(self):
        pass
    
    def to_improved_code_generation(self):
        #print 'improved code generation FunctionCall starts'
        
        #we need to store the formal parameters and the return address first
        parameter_number = 0
        for formal_node in self.__formal_node_array:
            formal_node.accept(self._visitor)
            parameter_number += 1
            #push the register on stack to protect the value if it is on used now
            if self._visitor.is_free_register('r' + str(parameter_number - 1)) == False:
                self._visitor.add_main_code('\tpush\t{r' + str(parameter_number - 1) + '}\n')
            
            if type(formal_node) == AstNumber:
                formal_value = formal_node.to_improved_code_generation()
                self._visitor.add_main_code('\tmov\tr' + str(parameter_number - 1) + ', #' + str(formal_value) + '\n')
            elif type(formal_node) == AstBinary:
                formal_node.to_improved_code_generation()
                self._visitor.add_main_code('\tpop\t{r' + str(parameter_number - 1) + '}\n')
            else:
                temporary_register = self._visitor.alloc_register()
                expression_address = formal_node.to_improved_code_generation()
                if expression_address < 0:
                    self._visitor.add_main_code('\tpop\t{r' + str(parameter_number - 1) + '}\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
                    self._visitor.add_main_code('\tldr\tr' + str(parameter_number - 1) + ', [r7, ' + temporary_register + ']\n')
                    self._visitor.free_register(temporary_register)
        
        self._visitor.add_main_code('\tbl\t' + self.__function_name + '\n')
        
        #pop the stack to get the register 
        register_number = len(self.__formal_node_array) - 1
        while register_number >= 0: 
            if self._visitor.is_free_register('r' + str(register_number)) == False:
                self._visitor.add_main_code('\tpop\t{r' + str(register_number) + '}\n')
            register_number -= 1
        
        #generate a label for Procedure
        self._visitor.generate_function_label()
        label_name = self.__function_name
        self._visitor.add_function_code(label_name + ':\n')
        self._visitor.add_function_code('\tstmfd\tsp!, {fp, lr}\n')
        self._visitor.add_function_code('\tadd\tfp, sp, #4\n')
        
        #get the total space to allocate in stack first
        dictionary = self.__table_entry.get_scope().get_table()
        parameter_number = 0
        local_variable_number = 0
        for key, value in dictionary.items():
            if type(value) == FormalVariable:
                parameter_number += 1
            elif type(value) == LocalVariable:
                local_variable_number += 1
        
        space = 4 + (parameter_number + local_variable_number) * 4
        self._visitor.add_function_code('\tsub\tsp, sp, #' + str(space) + '\n')
        
        #we need to set the address for local variable and formal variable respectively    
        current_parameter_number = 0
        current_local_variable_number = 0
        for key, value in dictionary.items():
            #if it is a local variable, we just need to initialize it and set the address offset from the frame pointer
            if type(value) == LocalVariable:
                current_local_variable_number += 1
                offset = 4 + parameter_number * 4 + current_local_variable_number * 4
                value.set_address_offset(offset)
            
            #if it is a formal variable, if the type of the variable is an integer, we need to copy it
            #if the type of the variable is a Record or Array, it is passed by reference
            elif type(value) == FormalVariable:
                current_parameter_number += 1
                
                if type(value.get_type()) == Integer:
                    offset = 4 + current_parameter_number * 4
                    value.set_address_offset(offset)
                    self._visitor.add_function_code('\tstr\tr' + str(current_parameter_number -1) + ', [fp, #-' + str(offset) + ']\n')
                        
                else:
                    pass
                
        self._visitor.set_in_function()
        
        #start interpret the body of the function
        self.__table_entry.get_body_ast().accept(self._visitor)
        self.__table_entry.get_body_ast().to_improved_code_generation()
        
        #start interpret the return expression of the Procedure
        if self.__table_entry.get_return_ast() != None:
            if type(self.__table_entry.get_return_ast().get_type()) != Integer:
                self._visitor.add_function_code('\tbl\texit\n')
            else:
                self.__table_entry.get_return_ast().accept(self._visitor)
                return self.__table_entry.get_return_ast().to_improved_code_generation()
        else:
            self._visitor.add_function_code('\tbl\texit\n')
            
        self._visitor.set_out_function()
        
        #print 'improved code generation FunctionCall ends'
       
#########################################################################
## Location - This class is a derived class from Node to represent the 
##            location.
##             
#########################################################################

class Location( Expression ):
    def __init__(self):
        super(Location, self).__init__()
    
    def print_string(self):
        pass
    
    
#########################################################################
## AstVariable - This class is a derived class from Location to represent the 
##            Variable node in the abstract syntax tree
##             
## ######################################################################

class AstVariable( Location ):
    def __init__(self, table_entry, variable_name):
        self.__table_entry = table_entry
        self.__variable_name = variable_name
        super(AstVariable, self).__init__()
        
    def get_variable_name(self):
        return self.__variable_name
        
    def get_location_entry(self):
        return self.__table_entry
    
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Variable:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'variable =>\n')
        self.__table_entry.accept(self._visitor)
        self.__table_entry.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Variable\",shape=box]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)+id(self.__table_entry)+id(self.__table_entry.get_type())) + ' [label=\"' + self.__variable_name + '\",shape=circle]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self)+id(self.__table_entry)+id(self.__table_entry.get_type())) + ' [label=\"ST\"]\n')
        
    def to_interpret(self):
        #print 'interpret variable ' + str(self.__variable_name) + ' starts'
        self._visitor.push_stack(self._visitor.get_environment_box(self.__variable_name))
        #print 'interpret variable ' + str(self.__variable_name) + ' ends'
        
    """
        This function will generate the code for Variable node in AST
        r2 is used to store the address offset of that variable

    """
    def to_code_generation(self):
        #print 'generate variable ' + str(self.__variable_name) + ' starts'
        self._visitor.add_code('\tldr\tr2, =' + str(self.__table_entry.get_address_offset()) + '\n')
        self._visitor.add_code('\tpush\t{r2}\n')
        #print 'generate variable ' + str(self.__variable_name) + ' ends'
        
    """
        This function will generate the code for Variable node in AST
        r2 is used to store the address offset of that variable

    """
    def to_improved_code_generation(self):
        #print 'generate variable ' + str(self.__variable_name) + ' starts'
        #print 'generate variable ' + str(self.__variable_name) + ' ends'
        return self.__table_entry.get_address_offset();
        
        
    def print_string(self):
        print 'ast variable'
        

#########################################################################
## AstIndex - This class is a derived class from Location to represent 
## an array variable node in the abstract syntax tree
##             
#########################################################################

class AstIndex( Location ):
    def __init__(self, location_node, expression_node):
        self.__location = location_node
        self.__expression_node = expression_node
        super(AstIndex, self).__init__()
        
    def get_location(self):
        return self.__location
    
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Index:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'location =>\n')
        self.__location.accept(self._visitor)
        self.__location.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'expression =>\n')
        self.__expression_node.accept(self._visitor)
        self.__expression_node.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Index\",shape=box]\n')
        self.__location.accept(self._visitor)
        self.__location.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__location)) + ' [label=\"location\"]\n')
        self.__expression_node.accept(self._visitor)
        self.__expression_node.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression_node)) + ' [label=\"expression\"]\n')
        
    def to_interpret(self):
        #print 'interpret Index starts'
        self.__location.accept(self._visitor)
        self.__location.to_interpret()
        current_box = self._visitor.pop_stack()
        while type(current_box) == DereferenceBox:
            current_box = current_box.get_reference_box()
        
        self.__expression_node.accept(self._visitor)
        self.__expression_node.to_interpret()
        index_box = self._visitor.pop_stack()
        if type(index_box) == IntegerBox:
            index = index_box.get_value()
        else:
            index = index_box
        
        if current_box.is_valid_index(index) == False:
            print 'error: the index value ' + str(index) + ' is out of bounds at Line: ' + str(self.__expression_node.get_line()) + ' position: (' + str(self.__expression_node.get_start_position()) \
             + ', ' + str(self.__expression_node.get_end_position()) + ')'
            exit()
            
        new_box = current_box.get_element(index)
        self._visitor.push_stack(new_box)
        #print 'interpret Index ends'
    
    """
        This function will generate the code for Index object in AST
        r1 is used to store the starting address offset of the array
        r2 is used to store the value of expression in array
        r3 is used to store the resulting address
        r4 is used to store the size of the element
    """
    def to_code_generation(self):
        #print 'generate index starts'
        #get the starting address offset from the location
        self.__location.accept(self._visitor)
        self.__location.to_code_generation()
        self._visitor.add_code('\tpop\t{r1}\n')
        self._visitor.add_code('\tpush\t{r1}\n')
        
        #get the value of expression in array
        if type(self.__expression_node) == AstNumber or type(self.__expression_node) == AstBinary:
            self.__expression_node.accept(self._visitor)
            self.__expression_node.to_code_generation()
            self._visitor.add_code('\tpop\t{r2}\n')
            
        #In this case, we need to get the address of that value first, and then dereference the value
        else:
            self.__expression_node.accept(self._visitor)
            self.__expression_node.to_code_generation()
            self._visitor.add_code('\tpop\t{r3}\n')
            self._visitor.add_code('\tldr\tr2, [r7, r3]\n')
            
        #get the size of the element
        element_size = self.get_type().get_size()
        self._visitor.add_code('\tldr\tr5, =' + str(element_size) + '\n')
        #get the element number this array contains
        element_number = self.__location.get_type().get_length()
        
        #if the index is smaller than zero
        line = self.__expression_node.get_line()
        start_position = self.__expression_node.get_start_position()
        end_position = self.__expression_node.get_end_position()
        self._visitor.add_code('\tcmp\tr2, #0\n')
        self._visitor.add_code('\tmovlt\tr1, r2\n')
        self._visitor.add_code('\tldrlt\tr2, =' + str(line) + '\n')
        self._visitor.add_code('\tldrlt\tr3, =' + str(start_position) + '\n')
        self._visitor.add_code('\tldrlt\tip, =' + str(end_position) + '\n')
        self._visitor.add_code('\tstrlt\tip, [sp, #0]\n')
        self._visitor.add_code('\tldrlt\tr0, indexerrorformatpointer\n')
        self._visitor.add_code('\tbllt\tprintf\n')
        self._visitor.add_code('\tmovlt\tr0, #' + str(1) + '\n')
        self._visitor.add_code('\tbllt\texit\n')
        
        #if the index is larger or equal to the total element number
        self._visitor.add_code('\tcmp\tr2, #' + str(element_number) + '\n')
        self._visitor.add_code('\tmovge\tr1, r2\n')
        self._visitor.add_code('\tldrge\tr2, =' + str(line) + '\n')
        self._visitor.add_code('\tldrge\tr3, =' + str(start_position) + '\n')
        self._visitor.add_code('\tldrge\tip, =' + str(end_position) + '\n')
        self._visitor.add_code('\tstrge\tip, [sp, #0]\n')
        self._visitor.add_code('\tldrge\tr0, indexerrorformatpointer\n')
        self._visitor.add_code('\tblge\tprintf\n')
        self._visitor.add_code('\tmovge\tr0, #' + str(1) + '\n')
        self._visitor.add_code('\tblge\texit\n')
        
        self._visitor.add_code('\tpop\t{r1}\n')
        #get the resulting address and push the resulting address on the stack.
        self._visitor.add_code('\tmul\tr3, r2, r5\n')
        self._visitor.add_code('\tadd\tr3, r1, r3\n')
        self._visitor.add_code('\tpush\t{r3}\n')
        #print 'generate index ends'
        
    """
        This function will generate the code for Index object in AST
        start_address_register is used to store the starting address offset of the array
        expression_value_register is used to store the value of expression in array
        result_register is used to store the result address
        element_size_register is used to store the size of the element
        
    """
    def to_improved_code_generation(self):
        #print 'generate Index starts'
        #get the address offset of the location
        address_offset = 0
        self.__location.accept(self._visitor)
        location_address_offset = self.__location.to_improved_code_generation()
        start_address_register = self._visitor.alloc_register()
        if location_address_offset < 0:
            self._visitor.add_main_code('\tpop\t{' + start_address_register + '}\n')
        else:
            address_offset += location_address_offset
        
        #if the expression is a constant, we can get that constant at compile time and get all relevant offsets.
        if location_address_offset >= 0 and type(self.__expression_node) == AstNumber:
            self.__expression_node.accept(self._visitor)
            index_value = self.__expression_node.to_improved_code_generation()
            max_num = self.__location.get_type().get_length()
            element_size = self.get_type().get_size()
            if index_value < 0 or index_value >= max_num:
                print 'error: the index value ' + str(index_value) + ' is out of bounds at Line: ' + str(self.__expression_node.get_line()) + ' position: (' + str(self.__expression_node.get_start_position()) \
                + ', ' + str(self.__expression_node.get_end_position()) + ')'
                exit()
            address_offset += element_size * index_value;
            self._visitor.free_register(start_address_register)
            #print 'generate Index ends'
            return address_offset;
            
        #In this case, we need to get the address of that value first, and then dereference the value
        else:
            self._visitor.generate_index_error_label()
            
            if location_address_offset >= 0:
                self._visitor.add_main_code('\tldr\t' + start_address_register + ', =' + str(address_offset) + '\n')
            self.__expression_node.accept(self._visitor)
            expression_value_register = self._visitor.alloc_register()
            
            if type(self.__expression_node) == AstNumber:
                const_value = self.__expression_node.to_improved_code_generation()
                self._visitor.add_main_code('\tldr\t' + expression_value_register + ', =' + str(const_value) + '\n')
            elif type(self.__expression_node) == AstBinary:
                self.__expression_node.to_improved_code_generation()
                self._visitor.add_main_code('\tpop\t{' + expression_value_register + '}\n')
            else:
                temporary_register = self._visitor.alloc_register()
                expression_address = self.__expression_node.to_improved_code_generation()
                if expression_address < 0:
                    self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
                 
                variable_type = self.__expression
                if type(variable_type) == FunctionCall:
                    self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [r7, ' + temporary_register + ']\n') 
                else:
                    while type(variable_type) != AstVariable:
                        variable_type = variable_type.get_location()
                    if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                        self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [fp, -' + temporary_register + ']\n')
                    else:
                        self._visitor.add_main_code('\tldr\t' + expression_value_register + ', [r7, ' + temporary_register + ']\n') 
                self._visitor.free_register(temporary_register)
                
            #get the size of the element
            element_size = self.get_type().get_size()
            element_size_register = self._visitor.alloc_register()
            
            self._visitor.add_main_code('\tldr\t' + element_size_register + ', =' + str(element_size) + '\n')
            #get the element number this array contains
            element_number = self.__location.get_type().get_length()
            
            #if the index is smaller than zero
            line = self.__expression_node.get_line()
            start_position = self.__expression_node.get_start_position()
            end_position = self.__expression_node.get_end_position()
            self._visitor.add_main_code('\tcmp\t' + expression_value_register + ', #0\n')
            self._visitor.add_main_code('\tmovlt\tr1, ' + expression_value_register + '\n')
            self._visitor.add_main_code('\tldrlt\tr2, =' + str(line) + '\n')
            self._visitor.add_main_code('\tldrlt\tr3, =' + str(start_position) + '\n')
            self._visitor.add_main_code('\tldrlt\tip, =' + str(end_position) + '\n')
            self._visitor.add_main_code('\tstrlt\tip, [sp, #0]\n')
            self._visitor.add_main_code('\tldrlt\tr0, indexerrorformatpointer\n')
            self._visitor.add_main_code('\tbllt\tprintf\n')
            self._visitor.add_main_code('\tmovlt\tr0, #' + str(1) + '\n')
            self._visitor.add_main_code('\tbllt\texit\n')
            
            #if the index is larger or equal to the total element number
            self._visitor.add_main_code('\tcmp\t' + expression_value_register + ', #' + str(element_number) + '\n')
            self._visitor.add_main_code('\tmovge\tr1, r2\n')
            self._visitor.add_main_code('\tldrge\tr2, =' + str(line) + '\n')
            self._visitor.add_main_code('\tldrge\tr3, =' + str(start_position) + '\n')
            self._visitor.add_main_code('\tldrge\tip, =' + str(end_position) + '\n')
            self._visitor.add_main_code('\tstrge\tip, [sp, #0]\n')
            self._visitor.add_main_code('\tldrge\tr0, indexerrorformatpointer\n')
            self._visitor.add_main_code('\tblge\tprintf\n')
            self._visitor.add_main_code('\tmovge\tr0, #' + str(1) + '\n')
            self._visitor.add_main_code('\tblge\texit\n')
            
            #get the resulting address and push the resulting address on the stack.
            result_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tmul\t' + result_register + ', ' + expression_value_register + ', ' + element_size_register + '\n')
            self._visitor.add_main_code('\tadd\t' + result_register + ', ' + start_address_register + ', ' + result_register + '\n')
            self._visitor.add_main_code('\tpush\t{' + result_register + '}\n')
            #print 'generate Index ends'
            self._visitor.free_register(start_address_register)
            self._visitor.free_register(expression_value_register)
            self._visitor.free_register(result_register)
            self._visitor.free_register(element_size_register)
            return -1;
            
    def print_string(self):
        print 'ast index'
        
        
#########################################################################
## AstField - This class is a derived class from Location to represent a 
##            field within a record variable in the abstract syntax tree
##             
#########################################################################

class AstField( Location ):
    def __init__(self, location_node, variable_node):
        self.__location = location_node
        self.__variable = variable_node
        super(AstField, self).__init__()
    
    def get_location(self):
        return self.__location
    
    def get_variable(self):
        return self.__variable
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Field:\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'location =>\n')
        self.__location.accept(self._visitor)
        self.__location.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'variable =>\n')
        self.__variable.accept(self._visitor)
        self.__variable.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Field\",shape=box]\n')
        self.__location.accept(self._visitor)
        self.__location.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__location)) + ' [label=\"location\"]\n')
        self.__variable.accept(self._visitor)
        self.__variable.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__variable)) + ' [label=\"variable\"]\n')

    def to_interpret(self):
        #print 'interpret Field starts'
        self.__location.accept(self._visitor)
        self.__location.to_interpret()
        location_box = self._visitor.pop_stack()
        while type(location_box) == DereferenceBox:
            location_box = location_box.get_reference_box()
        
        self._visitor.set_current_environment(location_box.get_environment())
        self.__variable.accept(self._visitor)
        self.__variable.to_interpret()
        #print 'interpret Field ends'
        
    """
        This function will generate the code for Field object in AST
        r1 is used to store the starting address offset of the field
        r2 is used to store the offset address of the variable in the field 
        r3 is used to store the resulting address
    """
    def to_code_generation(self):
        #print 'generate Field starts'
        
        #get the starting address offset from the location
        self.__location.accept(self._visitor)
        self.__location.to_code_generation()
        self._visitor.add_code('\tpop\t{r1}\n')
        self._visitor.add_code('\tpush\t{r1}\n')
        
        #get the offset address of the variable in the field
        self.__variable.accept(self._visitor)
        self.__variable.to_code_generation()
        self._visitor.add_code('\tpop\t{r2}\n')
            
        self._visitor.add_code('\tpop\t{r1}\n')
        #get the resulting address and push the resulting address on the stack.
        self._visitor.add_code('\tadd\tr3, r1, r2\n')
        self._visitor.add_code('\tpush\t{r3}\n')
        #print 'generate Field ends'
        
    """
        This function will generate the code for Field object in AST
        
    """
    def to_improved_code_generation(self):
        #print 'generate Field starts'
        #get the address offset of the location
        address_offset = 0
        self.__location.accept(self._visitor)
        address_offset += self.__location.to_improved_code_generation()
        
        #get the offset address of the variable in the field
        variable_offset = self.__variable.get_location_entry().get_address_offset()
        #print 'generate Field ends'
        return address_offset + variable_offset;    
    
    def print_string(self):
        print 'ast field'
        
    
#########################################################################
## Condition - This class is a derived class from Node to represent the 
##            condition categories.
##             
#########################################################################

class Condition( Node ):
    def __init__(self, relation, expression_left, expression_right):
        self.__relation = relation
        self.__expression_left = expression_left
        self.__expression_right = expression_right
        super(Condition, self).__init__()
        
    def get_relation(self):
        return self.__relation
    
    def set_relation(self, relation):
        self.__relation = relation
        
    def to_asc_output(self):
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'Condition (' + self.__relation + '):\n')
        self._visitor.set_indentation(indentation)
        self._visitor.add_semantic_output('  ' * indentation + 'left =>\n')
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'right =>\n')
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_asc_output()
        indentation -= 1
        self._visitor.set_indentation(indentation)
    
    def to_dot_output(self):
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"' + self.__relation + '\",shape=box]\n')
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression_left)) + ' [label=\"left\"]\n')
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__expression_right)) + ' [label=\"right\"]\n')
    
    def to_interpret(self):
        #print 'interpret Condition starts'
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_interpret()
        value_left_box = self._visitor.pop_stack()
        if type(value_left_box) == IntegerBox:
            value_left = value_left_box.get_value()
        else:
            value_left = value_left_box
            
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_interpret()
        value_right_box = self._visitor.pop_stack()
        if type(value_right_box) == IntegerBox:
            value_right = value_right_box.get_value()
        else:
            value_right = value_right_box
        
        return_value = 0
        
        if self.__relation == '=':
            if value_left == value_right:
                return_value = 1
        elif self.__relation == '#':
            if value_left != value_right:
                return_value = 1
        elif self.__relation == '<':
            if value_left < value_right:
                return_value = 1
        elif self.__relation == '>':
            if value_left > value_right:
                return_value = 1
        elif self.__relation == '<=':
            if value_left <= value_right:
                return_value = 1
        elif self.__relation == '>=':
            if value_left >= value_right:
                return_value = 1
                
        self._visitor.push_stack(return_value)  
        self._visitor.reset_environment()
        #print 'interpret Condition ends'
    
    """
        This function will generate the code for Condition node in AST
        r1 is used to store the value of the left expression
        r2 is used to store the value of the right expression
        r3 is used to store the final result
        
    """ 
    def to_code_generation(self):
        #print 'generate condition starts'
        self.__expression_left.accept(self._visitor)
        self.__expression_left.to_code_generation()
        #we load the value of the left expression to r1
        if type(self.__expression_left) == AstNumber or type(self.__expression_left) == AstBinary:
            self._visitor.add_code('\tpop\t{r1}\n')
        else:
            self._visitor.add_code('\tpop\t{r2}\n')
            self._visitor.add_code('\tldr\tr1, [r7, r2]\n')
        self._visitor.add_code('\tpush\t{r1}\n')
            
        self.__expression_right.accept(self._visitor)
        self.__expression_right.to_code_generation()
        #we load the value of the right expression to r2
        if type(self.__expression_right) == AstNumber or type(self.__expression_right) == AstBinary:
            self._visitor.add_code('\tpop\t{r2}\n')
        else:
            self._visitor.add_code('\tpop\t{r3}\n')
            self._visitor.add_code('\tldr\tr2, [r7, r3]\n')
            
        self._visitor.add_code('\tpop\t{r1}\n')
        #compare the value between the left and the right, the result is set in r3
        if self.__relation == '=':
            self._visitor.add_code('\tcmp\tr1, r2\n')
            self._visitor.add_code('\tmoveq\tr3, #1\n')
            self._visitor.add_code('\tmovne\tr3, #0\n')
            self._visitor.add_code('\tpush\t{r3}\n')
            
        elif self.__relation == '#':
            self._visitor.add_code('\tcmp\tr1, r2\n')
            self._visitor.add_code('\tmovne\tr3, #1\n')
            self._visitor.add_code('\tmoveq\tr3, #0\n')
            self._visitor.add_code('\tpush\t{r3}\n')
            
        elif self.__relation == '<':
            self._visitor.add_code('\tcmp\tr1, r2\n')
            self._visitor.add_code('\tmovlt\tr3, #1\n')
            self._visitor.add_code('\tmovge\tr3, #0\n')
            self._visitor.add_code('\tpush\t{r3}\n')
            
        elif self.__relation == '>':
            self._visitor.add_code('\tcmp\tr1, r2\n')
            self._visitor.add_code('\tmovgt\tr3, #1\n')
            self._visitor.add_code('\tmovle\tr3, #0\n')
            self._visitor.add_code('\tpush\t{r3}\n')
            
        elif self.__relation == '<=':
            self._visitor.add_code('\tcmp\tr1, r2\n')
            self._visitor.add_code('\tmovle\tr3, #1\n')
            self._visitor.add_code('\tmovgt\tr3, #0\n')
            self._visitor.add_code('\tpush\t{r3}\n')
            
        elif self.__relation == '>=':
            self._visitor.add_code('\tcmp\tr1, r2\n')
            self._visitor.add_code('\tmovge\tr3, #1\n')
            self._visitor.add_code('\tmovlt\tr3, #0\n')
            self._visitor.add_code('\tpush\t{r3}\n')
        
        #print 'generate condition ends'
        
    """
        This function will generate the code for Condition node in AST
        left_expression_register is used to store the value of the left expression
        right_expression_register is used to store the value of the right expression
        result_register is used to store the final result
        r1 is used to store the value of the left expression
        r2 is used to store the value of the right expression
        r3 is used to store the final result
        
    """ 
    def to_improved_code_generation(self):
        #print 'generate condition starts'
        self.__expression_left.accept(self._visitor)
        
        if type(self.__expression_left) == AstNumber:
            const_value = self.__expression_left.to_improved_code_generation()
            expression_value_left_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', =' + str(const_value) + '\n')
        elif type(self.__expression_left) == AstBinary:
            self.__expression_left.to_improved_code_generation()
            expression_value_left_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tpop\t{' + expression_value_left_register + '}\n')
        else:
            temporary_register = self._visitor.alloc_register()
            expression_value_left_register = self._visitor.alloc_register()
            expression_address = self.__expression_left.to_improved_code_generation()
            if expression_address < 0:
                self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
             
            variable_type = self.__expression
            if type(variable_type) == FunctionCall:
                self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [r7, ' + temporary_register + ']\n') 
            else:
                while type(variable_type) != AstVariable:
                    variable_type = variable_type.get_location()
                if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                    self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [fp, -' + temporary_register + ']\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [r7, ' + temporary_register + ']\n') 
            self._visitor.free_register(temporary_register)
        
        if type(self.__expression_right) == AstNumber:
            const_value = self.__expression_right.to_improved_code_generation()
            expression_value_right_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', =' + str(const_value) + '\n')
        elif type(self.__expression_right) == AstBinary:
            self.__expression_right.to_improved_code_generation()
            expression_value_right_register = self._visitor.alloc_register()
            self._visitor.add_main_code('\tpop\t{' + expression_value_right_register + '}\n')
        else:
            temporary_register = self._visitor.alloc_register()
            expression_value_right_register = self._visitor.alloc_register()
            expression_address = self.__expression_right.to_improved_code_generation()
            if expression_address < 0:
                self._visitor.add_main_code('\tpop\t{' + temporary_register + '}\n')
            else:
                self._visitor.add_main_code('\tldr\t' + temporary_register + ', =' + str(expression_address) + '\n')
             
            variable_type = self.__expression
            if type(variable_type) == FunctionCall:
                self._visitor.add_main_code('\tldr\t' + expression_value_left_register + ', [r7, ' + temporary_register + ']\n') 
            else:
                while type(variable_type) != AstVariable:
                    variable_type = variable_type.get_location()
                if (type(variable_type.get_location_entry()) == FormalVariable or type(variable_type.get_location_entry()) == LocalVariable) and self._visitor.is_in_function():
                    self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', [fp, -' + temporary_register + ']\n')
                else:
                    self._visitor.add_main_code('\tldr\t' + expression_value_right_register + ', [r7, ' + temporary_register + ']\n') 
            self._visitor.free_register(temporary_register)
        
        #compare the value between the left and the right, the result is set in result_register
        result_register = self._visitor.alloc_register()
        if self.__relation == '=':
            self._visitor.add_main_code('\tcmp\t' + expression_value_left_register + ', ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tmoveq\t' + result_register + ', #1\n')
            self._visitor.add_main_code('\tmovne\t' + result_register + ', #0\n')
            
        elif self.__relation == '#':
            self._visitor.add_main_code('\tcmp\t' + expression_value_left_register + ', ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tmovne\t' + result_register + ', #1\n')
            self._visitor.add_main_code('\tmoveq\t' + result_register + ', #0\n')
            
        elif self.__relation == '<':
            self._visitor.add_main_code('\tcmp\t' + expression_value_left_register + ', ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tmovlt\t' + result_register + ', #1\n')
            self._visitor.add_main_code('\tmovge\t' + result_register + ', #0\n')
            
        elif self.__relation == '>':
            self._visitor.add_main_code('\tcmp\t' + expression_value_left_register + ', ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tmovge\t' + result_register + ', #1\n')
            self._visitor.add_main_code('\tmovle\t' + result_register + ', #0\n')
            
        elif self.__relation == '<=':
            self._visitor.add_main_code('\tcmp\t' + expression_value_left_register + ', ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tmovle\t' + result_register + ', #1\n')
            self._visitor.add_main_code('\tmovgt\t' + result_register + ', #0\n')
            
        elif self.__relation == '>=':
            self._visitor.add_main_code('\tcmp\t' + expression_value_left_register + ', ' + expression_value_right_register + '\n')
            self._visitor.add_main_code('\tmovge\t' + result_register + ', #1\n')
            self._visitor.add_main_code('\tmovlt\t' + result_register + ', #0\n')
        #print 'generate condition ends'
        self._visitor.free_register(expression_value_left_register)
        self._visitor.free_register(expression_value_right_register)
        return result_register
        
    def print_string(self):
        print 'condition'
    
