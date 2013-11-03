#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
## SymbolTable.py - This module is used for producing symbol table 
##
## ######################################################################

from Environment import IntegerBox
from Environment import ArrayBox
from Environment import RecordBox
import copy

class Entry( object ):
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
    
    def to_environment(self):
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
## Constant - This class is a derived class for Entry to represent the 
##            constant type of token
##             
## ######################################################################

class Constant( Entry ):
    def __init__(self, const_type, value):
        self.__const_type = const_type
        self.__value = value
        
    def get_type(self):
        return self.__const_type
    
    def get_value(self):
        return self.__value
    
    def set_value(self, value):
        self.__value = value
    
    def to_asc_output(self):
        #print 'welcome const'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'CONST BEGIN\n')
        self._visitor.set_indentation(indentation)
        self.__const_type.accept(self._visitor)
        self.__const_type.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'value:\n')
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + str(self.__value) + '\n')
        indentation -= 2
        self._visitor.add_semantic_output('  ' * indentation + 'END CONST\n')
        #print 'const end'
        
    def to_dot_output(self):
        #print 'welcome const'
        if self._visitor.is_idnumber_exist(id(self)):
            return
        self.__const_type.accept(self._visitor)
        self.__const_type.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"' + str(self.__value) + '\",shape=diamond]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__const_type)) + '\n')
        self._visitor.add_idnumber(id(self))
        #print 'const end'
        
    
#########################################################################
## Variable - This class is a derived class for Entry to represent the 
##            Variable type of token
##             
#########################################################################

class Variable( Entry ):
    def __init__(self, var_type):
        pass
        
    def get_type(self):
        pass
    
    def get_address_offset(self):
        pass
    
    def set_address_offset(self, address_offset):
        pass
    
    def to_asc_output(self):
        pass
        
    def to_dot_output(self):
        pass
    
    
#########################################################################
## GlobalVariable - This class is a derived class for Variable to represent the 
##            Global variable type of token
##             
#########################################################################

class GlobalVariable( Variable ):
    def __init__(self, var_type):
        self.__var_type = var_type
        self.__address_offset = None
        super(GlobalVariable, self).__init__(self.__var_type)
        
    def get_type(self):
        return self.__var_type
    
    def get_address_offset(self):
        return self.__address_offset
    
    def set_address_offset(self, address_offset):
        self.__address_offset = address_offset
    
    def to_asc_output(self):
        #print 'welcome GlobalVariable'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'VAR BEGIN\n')
        self._visitor.set_indentation(indentation)
        self.__var_type.accept(self._visitor)
        self.__var_type.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'END VAR\n')
        #print 'GlobalVariable end'
        
    def to_dot_output(self):
        #print 'welcome GlobalVariable'
        if self._visitor.is_idnumber_exist(id(self)):
            return
        self.__var_type.accept(self._visitor)
        self.__var_type.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"\",shape=circle]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__var_type)) + '\n')
        self._visitor.add_idnumber(id(self))
        #print 'GlobalVariable end'
    
#########################################################################
## LocalVariable - This class is a derived class for Variable to represent the 
##            Global variable type of token
##             
#########################################################################

class LocalVariable( Variable ):
    def __init__(self, var_type):
        self.__var_type = var_type
        self.__address_offset = None
        super(LocalVariable, self).__init__(self.__var_type)
        
    def get_type(self):
        return self.__var_type
    
    def get_address_offset(self):
        return self.__address_offset
    
    def set_address_offset(self, address_offset):
        self.__address_offset = address_offset
    
    def to_asc_output(self):
        #print 'welcome LocalVariable'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'VAR BEGIN\n')
        self._visitor.set_indentation(indentation)
        self.__var_type.accept(self._visitor)
        self.__var_type.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'END VAR\n')
        #print 'LocalVariable end'
        
    def to_dot_output(self):
        #print 'welcome LocalVariable'
        if self._visitor.is_idnumber_exist(id(self)):
            return
        self.__var_type.accept(self._visitor)
        self.__var_type.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"\",shape=circle]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__var_type)) + '\n')
        self._visitor.add_idnumber(id(self))
        #print 'LocalVariable end'
    

#########################################################################
## FormalVariable - This class is a derived class for Variable to represent the 
##            Global variable type of token
##             
#########################################################################

class FormalVariable( Variable ):
    def __init__(self, var_type):
        self.__var_type = var_type
        self.__address_offset = None
        super(FormalVariable, self).__init__(self.__var_type)
        
    def get_type(self):
        return self.__var_type
    
    def get_address_offset(self):
        return self.__address_offset
    
    def set_address_offset(self, address_offset):
        self.__address_offset = address_offset
    
    def to_asc_output(self):
        #print 'welcome FormalVariable'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'VAR BEGIN\n')
        self._visitor.set_indentation(indentation)
        self.__var_type.accept(self._visitor)
        self.__var_type.to_asc_output()
        self._visitor.add_semantic_output('  ' * indentation + 'END VAR\n')
        #print 'FormalVariable end'
        
    def to_dot_output(self):
        #print 'welcome FormalVariable'
        if self._visitor.is_idnumber_exist(id(self)):
            return
        self.__var_type.accept(self._visitor)
        self.__var_type.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"\",shape=circle]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__var_type)) + '\n')
        self._visitor.add_idnumber(id(self))
        #print 'FormalVariable end'
        
        
#########################################################################
## Type - This class is a derived class for Entry to represent the 
##            Type declarations of token
##             
## ######################################################################

class Type( Entry ):
    def __init__(self):
        self.__size = 0
        
    def get_size(self):
        return self.__size
    
    def set_size(self, size):
        self.__size = size
    
    def get_type(self):
        pass
    
    
#########################################################################
## Integer - This class is a derived class for Type to represent the 
##           Integer. I use the Singleton design method to implement it.
##           it make sure that you never create more than one instance
##           of Integer class.
##             
## ######################################################################

## Singleton class
class Integer( Type ):
    ## Stores the unique Singleton instance-
    _instance = None

    ## The constructor
    #  @param self The object pointer.
    def __init__( self ):
        super(Integer, self).__init__()
    
    @staticmethod
    def get_instance():
        if Integer._instance == None:
            Integer._instance = Integer()
        return Integer._instance

    
    def to_asc_output(self):
        #print 'welcome Integer'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'type:\n')
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'INTEGER\n')
        #print 'Integer ends'
        
    def to_dot_output(self):
        #print 'welcome Integer'
        if self._visitor.is_idnumber_exist(id(self)):
            return  
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Integer\", shape=box, style=rounded]\n')
        self._visitor.add_idnumber(id(self))
        #print 'Integer ends'
        
    def to_environment(self):
        #print 'build IntegerBox starts'
        integer_box = IntegerBox()
        #print 'build IntegerBox ends'
        return integer_box
    
    def to_storage_allocation(self):
        #print 'allocate integer starts'
        self.set_size(4)
        #print 'allocate integer ends'
        
        
#########################################################################
## Array   - This class is a derived class for Type to represent the 
##           Array. 
##             
## ######################################################################

class Array( Type ):
    def __init__(self, array_type, length):
        self.__array_type = array_type
        self.__length = length
        super(Array, self).__init__()
        
    def get_array_type(self):
        return self.__array_type
    
    def get_length(self):
        return self.__length
    
    def to_asc_output(self):
        #print 'welcome array'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'type:\n')
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'ARRAY BEGIN\n')
        self._visitor.set_indentation(indentation)
        self.__array_type.accept(self._visitor)
        self.__array_type.to_asc_output()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'length:\n')
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + str(self.__length) + '\n')
        indentation -= 2
        self._visitor.add_semantic_output('  ' * indentation + 'END ARRAY\n')
        #print 'array end'
        
    def to_dot_output(self):
        #print 'welcome array'
        if self._visitor.is_idnumber_exist(id(self)):
            return
        self.__array_type.accept(self._visitor)
        self.__array_type.to_dot_output()
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"ARRAY\\nlength: ' + str(self.__length) + '\",shape=box,style=rounded]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__array_type)) + '\n')
        self._visitor.add_idnumber(id(self))
        #print 'array end'
        
    def to_environment(self):
        #print 'build ArrayBox starts'
        self.__array_type.accept(self._visitor)
        element_box = copy.copy(self.__array_type.to_environment())
        array_box = ArrayBox(element_box, self.__length)
        #print 'build ArrayBox ends'
        return array_box
    
    def to_storage_allocation(self):
        #print 'allocate array starts'
        self.__array_type.accept(self._visitor)
        self.__array_type.to_storage_allocation()
        element_size = self.__array_type.get_size()
        size = element_size * self.__length
        self.set_size(size)
        #print 'allocate array ends, length is ' + str(length)
        

#########################################################################
## Record  - This class is a derived class for Type to represent the 
##           Record type.
##             
#########################################################################

class Record( Type ):
    def __init__(self, scope):
        self.__scope = scope
        super(Record, self).__init__()
        
    def get_scope(self):
        return self.__scope
    
    def to_asc_output(self):
        #print 'welcome record'
        indentation = self._visitor.get_indentation()
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'RECORD BEGIN\n')
        indentation += 1
        self._visitor.add_semantic_output('  ' * indentation + 'SCOPE BEGIN\n')
        dictionary = self.__scope.get_table()
        for key, value in sorted(dictionary.items()):
            #print 'record element start'
            indentation += 1
            self._visitor.add_semantic_output('  ' * indentation + key + ' =>\n')
            self._visitor.set_indentation(indentation)
            value.accept(self._visitor)
            value.to_asc_output()
            indentation -= 1
            #print 'record element end'
        self._visitor.add_semantic_output('  ' * indentation + 'END SCOPE\n')
        indentation -= 1
        self._visitor.add_semantic_output('  ' * indentation + 'END RECORD\n')
        #print 'record end'
        
    def to_dot_output(self):
        #print 'welcome record'
        if self._visitor.is_idnumber_exist(id(self)):
            return
        dictionary = self.__scope.get_table()
        for key, value in sorted(dictionary.items()):
            #print 'record element start'
            value.accept(self._visitor)
            value.to_dot_output()
            #print 'record element end'
        self._visitor.add_semantic_output('subgraph cluster_' + str(id(self.__scope)) + ' {\n')
        for key, value in sorted(dictionary.items()):
            self._visitor.add_semantic_output(key + '_' + str(id(self.__scope)) + ' [label=\"' + key + '\",shape=box,color=white,fontcolor=black]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self.__scope)) + ' [label=\"\",style=invis]\n}\n')

        for key, value in sorted(dictionary.items()):
            self._visitor.add_semantic_output(key + '_' + str(id(self.__scope)) + ' -> _anchor_' + str(id(value)) + '\n') 
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' [label=\"Record",shape=box,style=rounded]\n')
        self._visitor.add_semantic_output('_anchor_' + str(id(self)) + ' -> _anchor_' + str(id(self.__scope)) + '\n')
        self._visitor.add_idnumber(id(self))
        
    def to_environment(self):
        #print 'build RecordBox starts'
        dictionary = self.__scope.get_table()
        record_box = RecordBox()
        
        for key, value in sorted(dictionary.items()):
            #print 'build record element starts'
            #we just build the environment for the variable entry
            if isinstance(value, Variable):
                variable_type = value.get_type()
                variable_type.accept(self._visitor)
                record_box.add_element_box(key, variable_type.to_environment())
            #print 'build record element ends'
        #print 'build RecordBox ends'
        return record_box
    
    def to_storage_allocation(self):
        #print 'allocate Record starts'
        dictionary = self.__scope.get_table()
        record_size = 0
        offset = 0
        for key, value in sorted(dictionary.items()):
            #print 'allocate record element starts'
            #we just build the environment for the variable entry
            if isinstance(value, Variable):
                variable_type = value.get_type()
                variable_type.accept(self._visitor)
                variable_type.to_storage_allocation()
                
                #set the address offset for every element in the record
                value.set_address_offset(offset)
                offset += variable_type.get_size()
                
                record_size += variable_type.get_size()
                
        self.set_size(record_size)
        #print 'allocate record ends, length is ' + str(length)
        
        
#########################################################################
## Procedure  - This class is a derived class for Type to represent the 
##           Record type.
##             
#########################################################################

class Procedure( Entry ):
    def __init__( self, scope, procedure_type, argument_num):
        self.__scope = scope
        self.__procedure_type = procedure_type
        self.__body_ast = None
        self.__return_ast = None
        self.__argument_num = argument_num
    
    def get_scope(self):
        return self.__scope
    
    def get_procedure_type(self):
        return self.__procedure_type
    
    def set_body_ast(self, ast):
        self.__body_ast = ast
        
    def get_body_ast(self):
        return self.__body_ast

    def set_return_ast(self, ast):
        self.__return_ast = ast
        
    def get_return_ast(self):
        return self.__return_ast
    
    def get_argument_num(self):
        return self.__argument_num
        

#########################################################################
## Scope - This class wraps the symbol table and contains all the operations
##         including inserting and finding the entry.
##             
#########################################################################

class Scope:
    def __init__(self, scope_num, outer_scope):
        #the symbol table in the current scope
        self.__dictionary = {}
        #the environment in the current scope
        self.__environment = {}
        self.__scope_num = scope_num
        self.__outer_scope = outer_scope
        
    """
        This function insert an entry to the symbol table
    """
    def insert(self, name, entry):
        self.__dictionary[name] = entry
    
    """
        This function finds the value associated with a given name in the scope or any outer scope
        it may attached to
    """
    def find(self, name):
        current_scope = self
        while current_scope != None:
            if current_scope.__dictionary.has_key(name):
                return current_scope.__dictionary.get(name)
            current_scope = current_scope.__outer_scope
        return False
    
    """
        This function returns true if the given name is in this scope but false if it doesn't exist
        or is an outer scope
    """
    def local(self, name):
        if self.__dictionary.has_key(name):
            return True
        return False
    
    """
        This function will build the environment based on the symbol table
        
    """
    def build_environment(self):
        for key, value in sorted(self.__symbol_table.items()):
            #we just build the environment for the variable entry
            if isinstance(value, Variable):
                if type(value.get_type()) == Integer:
                    self.__environment[key] = IntegerBox()
                elif type(value.get_type()) == Array:
                    array_length = value.get_type().get_length()
                    self.__environment[key] = ArrayBox(array_length)
                elif type(value.get_type()) == Record:
                    self.__environment[key] = RecordBox(value.get_type())
        
    def get_table(self):
        return self.__dictionary
    
    def get_environment(self):
        return self.__environment