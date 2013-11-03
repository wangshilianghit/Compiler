#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
## Factory.py - This module is used for storing all the factory class 
##             
#########################################################################



from Ast import AstNumber
from Ast import AstVariable
from Ast import AstBinary
from Ast import AstIndex
from Ast import AstField
from Ast import Read
from Ast import Write
from Ast import Assign
from Ast import If
from Ast import Repeat
from Ast import Condition
from Ast import FunctionCall
from Ast import ProcedureCall
from SymbolTable import Scope
from SymbolTable import Type
from SymbolTable import Integer
from SymbolTable import Constant
from SymbolTable import Array
from SymbolTable import Record
import copy

#########################################################################
## AbstractFactory - This class is the base class of factory that does nothing
##             
#########################################################################
class AbstractFactory( object ):
    def __init__(self, output):
        pass
    
    def create_scope(self):
        pass
    
    def get_current_scope(self):
        pass
    
    def get_global_scope(self):
        pass
    
    def is_global_scope(self):
        return True
    
    def get_type_object(self, value):
        pass
    
    def delete_scope(self):
        pass
    
    def add_entry(self, entry_token, entry_type):
        return ""
    
    def create_ast(self, root_node):
        pass
    
    def create_node(self, current_token):
        pass
    
    def produce_binary_node(self, operator, last_node, current_node):
        pass
    
    def reverse_condition(self, condition_node):
        pass
    
    def judge_type(self, entry_token, type_object):
        pass
        
    def produce_number_node(self, number_entry):
        pass
    
    def produce_index_node(self, root_node, expression_node):
        pass
    
    def produce_field_node(self, root_node, current_token):
        pass
    
    def produce_read_node(self, location_node):
        pass
    
    def produce_write_node(self, expression_node):
        pass
    
    def produce_assign_node(self, location_node, expression_node):
        pass
    
    def produce_if_node(self, condition_node, repeat_node):
        pass
    
    def produce_repeat_node(self, condition_node, instruction_node):
        pass
    
    def produce_condition_node(self, relation_token, left_expression_node, right_expression_node):
        pass
    
    def get_error_message(self):
        return ""
    
    
    
    
#########################################################################
## ParserFactory - This class is the factory class that does nothing
##             
#########################################################################

class ParserFactory( AbstractFactory ):
    pass


#########################################################################
## SemanticFactory - This class is the factory class that builds the symbol
## table and checks context conditions. . 
##             
## ######################################################################

class SemanticFactory( AbstractFactory ):
    def __init__(self, output):
        #this list is used as a program stack
        self._scope_array = []
        self._scope_num = -1
        self.__output = output
        self.__symbol_table = None
        self._error_message = ''
    
    """
        This function will create a new scope, and set the current scope as the outer scope for the new scope
        The universe scope's scope number is 0, the global scope's scope number is 1
    """
    def create_scope(self):
        self._scope_num += 1
        if self._scope_num == 0:
            scope = Scope(self._scope_num, None)
        else:
            scope = Scope(self._scope_num, self._scope_array[self._scope_num-1])
        self._scope_array.append(scope)
        
    def get_outer_scope(self):
        assert self._scope_num > 0
        return self._scope_array[self._scope_num-1]
    
    def get_global_scope(self):
        assert self._scope_num > 0
        return self._scope_array[1]
        
    def is_global_scope(self):
        if self._scope_num == 1:
            return True
        return False
    
    """
        This function will get the current scope
    """
    def get_current_scope(self):
        assert self._scope_num >= 0
        return self._scope_array[self._scope_num]
    
    def get_type_object(self, value):
        current_scope = self.get_current_scope()
        type_object = current_scope.find(value)
        return type_object
        
    def get_symbol_table(self):
        return self.__symbol_table
    
    def delete_scope(self):
        #sort the variables in the current scope and pop up the stack
        assert self._scope_num >= 0
        if self._scope_num == 1:
            #print 'symbol table build finished'
            self.__output.get_table(self._scope_array[1].get_table())
            self.__symbol_table = self._scope_array[1].get_table()
        self._scope_num -= 1
        self._scope_array.pop()
        
    def add_entry(self, entry_token, entry_type):
        assert self._scope_num >= 0
        #judge whether the new entry has existed in the local scope's symbol table
        if self.get_current_scope().local(entry_token.get_token_value()):
            last_entry = self.get_type_object(entry_token.get_token_value())
            self._error_message =  'error: duplicate declaration of \"' + entry_token.get_token_value() + '\" at Line: ' + str(entry_token.get_line_number()) + \
                             ', Position: (' + str(entry_token.get_token_start_index()) +  + ', ' + str(entry_token.get_token_end_index()) + ') conflicts with \"' + \
                            entry_token.get_token_value()  + '\" at Line: ' + \
                             str(last_entry.get_line()) + ', Position: (' + str(last_entry.get_start_position()) + ', ' + str(last_entry.get_end_position()) + ')'
            return None
        else:
            entry_type.set_start_position(entry_token.get_token_start_index())
            entry_type.set_end_position(entry_token.get_token_end_index())
            entry_type.set_line(entry_token.get_line_number())
            self._scope_array[self._scope_num].insert(entry_token.get_token_value(), entry_type)
            return True
    
    """
        This function is called when creating a new procedure entry in the outer scope
    
    """
    def add_outer_entry(self, entry_token, entry_type):
        assert self._scope_num > 0
        #judge whether the new entry has existed in the outer scope's symbol table
        if self.get_outer_scope().local(entry_token.get_token_value()):
            last_entry = self.get_type_object(entry_token.get_token_value())
            self._error_message =  'error: duplicate declaration of \"' + entry_token.get_token_value() + '\" at Line: ' + str(entry_token.get_line_number()) + \
                             ', Position: (' + str(entry_token.get_token_start_index()) +  + ', ' + str(entry_token.get_token_end_index()) + ') conflicts with \"' + \
                            entry_token.get_token_value()  + '\" at Line: ' + \
                             str(last_entry.get_line()) + ', Position: (' + str(last_entry.get_start_position()) + ', ' + str(last_entry.get_end_position()) + ')'
            return None
        else:
            entry_type.set_start_position(entry_token.get_token_start_index())
            entry_type.set_end_position(entry_token.get_token_end_index())
            entry_type.set_line(entry_token.get_line_number())
            self._scope_array[self._scope_num-1].insert(entry_token.get_token_value(), entry_type)
            return True
        
        
    def judge_type(self, entry_token, type_object):
        if isinstance(type_object, Type):
            return True
        else:
            self._error_message = 'error: The identifier \"' + entry_token.get_token_value() + '\" in the Type production must denote a type at Line: ' + str(entry_token.get_line_number()) + \
                             ', Position: (' + str(entry_token.get_token_end_index()) + ', ' + str(entry_token.get_token_end_index()) + ')'
            return None
                             
    def get_error_message(self):
        return self._error_message   
    
    
#########################################################################
## AstFactory - This class is the factory class that builds abstract
## syntax tree and checks context conditions. . 
##             
#########################################################################

class AstFactory( SemanticFactory ):
    def __init__(self, output):
        self.__output = output
        self.__ast_root = None
        super(AstFactory, self).__init__(self.__output)
        
    def create_ast(self, root_node):
        #print 'create ast'
        self.__ast_root = root_node
        self.__output.set_root(root_node)
    
    def get_ast_root(self):
        return self.__ast_root
        
    def create_node(self, current_token):
        node = None
        if current_token.get_token_name() == 'integer':
            #create a number node in AST
            node = AstNumber(Constant(Integer.get_instance(), current_token.get_token_value()), current_token.get_token_value())
            node.set_type(Integer.get_instance())
            node.set_start_position(current_token.get_token_start_index())
            node.set_end_position(current_token.get_token_end_index())
            node.set_line(current_token.get_line_number())
            
        elif current_token.get_token_name() == 'identifier':
            #judge whether this identifier exists in symbol table
            if self.get_current_scope().find(current_token.get_token_value()):
                #judge whether this identifier is a constant type
                value_entry = self.get_type_object(current_token.get_token_value())
                if type(value_entry) is Constant:
                    node = AstNumber(value_entry, value_entry.get_value())
                    node.set_type(Integer.get_instance())
                    node.set_start_position(current_token.get_token_start_index())
                    node.set_end_position(current_token.get_token_end_index())
                    node.set_line(current_token.get_line_number())
                else:
                    node = AstVariable(value_entry, current_token.get_token_value())
                    node.set_type(value_entry.get_type())
                    node.set_start_position(current_token.get_token_start_index())
                    node.set_end_position(current_token.get_token_end_index())
                    node.set_line(current_token.get_line_number())
            #if this identifier doesn't exist in symbol table, error handling
            else:
                self._error_message = 'error: the identifier \"' + current_token.get_token_value() + '\" hasn\'t been declared yet at Line: ' + str(current_token.get_line_number()) + \
                    ', Position: (' + str(current_token.get_token_start_index()) + ', ' + str(current_token.get_token_end_index()) + ')'
                return None
        return node
    
    
    def produce_number_node(self, number_entry):
        node = AstNumber(number_entry, number_entry.get_value())
        node.set_type(Integer.get_instance())
        return node
        
    def produce_binary_node(self, operator_token, last_node, current_node):
        node = None
        #we will do the constant folding for the adjacent nodes
        operator = operator_token.get_token_name()
        if type(last_node) is AstNumber and type(current_node) is AstNumber:
            node = copy.copy(last_node)
            if operator == '+':
                node.set_constant_value(last_node.get_constant_value() + current_node.get_constant_value())
            elif operator == '-':
                node.set_constant_value(last_node.get_constant_value() - current_node.get_constant_value())
            elif operator == '*':
                node.set_constant_value(last_node.get_constant_value() * current_node.get_constant_value())
            elif operator == 'DIV':
                node.set_constant_value(last_node.get_constant_value() / current_node.get_constant_value())
            elif operator == 'MOD':
                node.set_constant_value(last_node.get_constant_value() % current_node.get_constant_value())
                
        #otherwise, we will produce a binary node
        #we also need to make sure both of the operands are type integer
        else:
            if type(last_node.get_type()) is Integer and type(current_node.get_type()) is Integer: 
                node = AstBinary(operator, last_node, current_node)
                node.set_start_position(operator_token.get_token_start_index())
                node.set_end_position(operator_token.get_token_end_index())
                node.set_line(current_node.get_line())
                node.set_type(last_node.get_type())
            else:
                if type(last_node.get_type()) is not Integer:
                    self._error_message = 'error: arithmetic operators are only applicable to operands of type integer at Line: ' + str(last_node.get_line()) + \
                        ', Position: (' + str(last_node.get_start_position()) + ', ' + str(last_node.get_end_position()) + ')'
                elif type(current_node.get_type()) is not Integer:
                    self._error_message = 'error: arithmetic operators are only applicable to operands of type integer at Line: ' + str(current_node.get_line()) + \
                        ', Position: (' + str(current_node.get_start_position()) + ', ' + str(current_node.get_end_position()) + ')'
        return node
    
    def produce_index_node(self, root_node, expression_node):
        current_entry = root_node.get_type()
        if type(current_entry) is Array:
            type_pointer = current_entry.get_array_type()
            new_root_node = AstIndex(root_node, expression_node)
            new_root_node.set_type(type_pointer)
            new_root_node.set_start_position(root_node.get_start_position())
            new_root_node.set_end_position(expression_node.get_end_position())
            new_root_node.set_line(root_node.get_line())
            return new_root_node
        
        else:
            self._error_message = 'error: Selector "[]" are only applicable to variables of array type at Line: ' + str(root_node.get_line()) + \
            ', Position: (' + str(root_node.get_start_position()) + ', ' + str(root_node.get_end_position()) + ')'
            return None
    
    def produce_field_node(self, root_node, current_token):
        current_entry = root_node.get_type()
        if type(current_entry) is Record:
            record_value_entry = current_entry.get_scope().find(current_token.get_token_value())
            if record_value_entry == False:
                self._error_message = 'error: the identifier \"' + current_token.get_token_value() + '\" hasn\'t been declared in this record at Line: ' + str(current_token.get_line_number()) + \
                    ', Position: (' + str(current_token.get_token_start_index()) + ', ' + str(current_token.get_token_end_index()) + ')'
                return None
            variable_node = AstVariable(record_value_entry, current_token.get_token_value())
            variable_node.set_line(current_token.get_line_number())
            variable_node.set_start_position(current_token.get_token_start_index())
            variable_node.set_end_position(current_token.get_token_end_index())
            
            new_root_node = AstField(root_node, variable_node)
            new_root_node.set_type(record_value_entry.get_type())
            new_root_node.set_start_position(root_node.get_start_position())
            new_root_node.set_end_position(variable_node.get_end_position())
            new_root_node.set_line(root_node.get_line())
            return new_root_node
        else:
            self._error_message = 'error: Selector "." are only applicable to variables of record type at Line: ' + str(root_node.get_line()) + \
            ', Position: (' + str(root_node.get_start_position()) + ', ' + str(root_node.get_end_position()) + ')'
            return None
        
        
    def produce_read_node(self, location_node):
        if type(location_node.get_type()) is Integer:
            read_node = Read(location_node)
            read_node.set_start_position(location_node.get_start_position())
            read_node.set_end_position(location_node.get_end_position())
            read_node.set_line(location_node.get_line())
            return read_node
        else:
            self._error_message = 'error: The designator in the Read production must denote a variable of type integer at Line: ' + str(location_node.get_line()) + \
            ', Position: (' + str(location_node.get_start_position()) + ', ' + str(location_node.get_end_position()) + ')'
            return None
        
        
    def produce_write_node(self, expression_node):
        if type(expression_node.get_type()) is Integer:
            write_node = Write(expression_node)
            write_node.set_start_position(expression_node.get_start_position())
            write_node.set_end_position(expression_node.get_end_position())
            write_node.set_line(expression_node.get_line())
            return write_node
        else:
            self._error_message = 'error: The expression in the Write production must be of type integer at Line: ' + str(expression_node.get_line()) + \
            ', Position: (' + str(expression_node.get_start_position()) + ', ' + str(expression_node.get_end_position()) + ')'
            return None
        
    def produce_assign_node(self, location_node, expression_node):
        instruction_node = Assign(location_node, expression_node)
        instruction_node.set_start_position(location_node.get_start_position())
        instruction_node.set_end_position(expression_node.get_end_position())
        instruction_node.set_line(location_node.get_line())
        return instruction_node
        
    def produce_if_node(self, condition_node, true_instruction_node, false_instruction_node):
        if false_instruction_node == None:
            if_node = If(condition_node, true_instruction_node)
            if_node.set_start_position(condition_node.get_start_position())
            if_node.set_end_position(true_instruction_node.get_end_position())
            if_node.set_line(condition_node.get_line())
        else:
            if_node = If(condition_node, true_instruction_node, false_instruction_node)
            if_node.set_start_position(condition_node.get_start_position())
            if_node.set_end_position(false_instruction_node.get_end_position())
            if_node.set_line(condition_node.get_line())
        return if_node
        
    def produce_repeat_node(self, condition_node, instruction_node):
        repeat_node = Repeat(condition_node, instruction_node)
        repeat_node.set_start_position(condition_node.get_start_position())
        repeat_node.set_end_position(instruction_node.get_end_position())
        repeat_node.set_line(condition_node.get_line())
        return repeat_node
        
    def produce_condition_node(self, relation_token, left_expression_node, right_expression_node):
        relation = relation_token.get_token_name()
        condition_node = Condition(relation, left_expression_node, right_expression_node)
        condition_node.set_start_position(relation_token.get_token_start_index())
        condition_node.set_end_position(relation_token.get_token_end_index())
        condition_node.set_line(relation_token.get_line_number())
        return condition_node
    
    def produce_function_call_node(self, current_token, formal_node_array, table_entry):
        function_call_node = FunctionCall(formal_node_array, table_entry, current_token.get_token_value())
        function_call_node.set_start_position(current_token.get_token_start_index())
        function_call_node.set_end_position(formal_node_array[len(formal_node_array)-1].get_end_position())
        function_call_node.set_line(current_token.get_line_number())
        function_call_node.set_type(Integer.get_instance())
        return function_call_node
    
    def produce_procedure_call_node(self, current_token, formal_node_array, table_entry):
        procedure_call_node = ProcedureCall(formal_node_array, table_entry, current_token.get_token_value())
        procedure_call_node.set_start_position(current_token.get_token_start_index())
        procedure_call_node.set_end_position(formal_node_array[len(formal_node_array)-1].get_end_position())
        procedure_call_node.set_line(current_token.get_line_number())
        return procedure_call_node
        
    def reverse_condition(self, condition_node):
        new_condition_node = copy.copy(condition_node)
        if new_condition_node.get_relation() == '=':
            new_condition_node.set_relation('#')
        elif new_condition_node.get_relation() == '#':
            new_condition_node.set_relation('=')
        elif new_condition_node.get_relation() == '<':
            new_condition_node.set_relation('>=')
        elif new_condition_node.get_relation() == '>':
            new_condition_node.set_relation('<=')    
        elif new_condition_node.get_relation() == '<=':
            new_condition_node.set_relation('>')
        elif new_condition_node.get_relation() == '>=':
            new_condition_node.set_relation('<')
        return new_condition_node
    
    