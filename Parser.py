#!/usr/bin/python

########################################################################
# author:  Shiliang Wang           
# Email:   wangshiliang@jhu.edu
#########################################################################
##   Parser.py  - This class accepts the list of tokens to the constructor
##   public function:  
##   def parse(self): The driver program should call this method to parse the tokens
##   def get_error_message(self):  The driver program can get all the 
##   error message by calling this function 
## ######################################################################

from Token import Token
from Visitor import AstAscOutput
from Factory import AstFactory
from SymbolTable import Integer
from SymbolTable import Constant
from SymbolTable import Array
from SymbolTable import Record
from SymbolTable import GlobalVariable
from SymbolTable import LocalVariable
from SymbolTable import FormalVariable
from Ast import AstNumber
from SymbolTable import Procedure

import copy
"""
    This exception class is used for returning to declaration  
"""
class FindDeclException: pass

"""
    This exception class is used for returning to begin  
"""
class FindBeginException: pass

"""
    This exception is used for returning to instruction
"""
class FindInstructException: pass

"""
    This exception is used for ending the program
"""
class EndException: pass

#all week symbols
weak_symbol = [';',')',']','END','.']

#all strong symbols
strong_symbol = ['BEGIN', 'CONST','TYPE','VAR','IF','REPEAT','WHLIE','WRTIE','READ']
        
        
class Parser:
    def __init__(self, __token_array, output, factory):
        self.__token_array = __token_array
        self.__current_token_index = -1
        self.__current_level = 0;
        self.__output = output
        self.__error_message = ''
        self.__factory = factory
        self.__program_value = ''
        self.__start_error_index = 0
        self.__is_error_handling = False
        
        
    def __get_current_token(self):
        current_token = self.__token_array[self.__current_token_index]
        return current_token
    
    def __is_next_token(self):
        if self.__current_token_index < len(self.__token_array) - 1:
            return True
        return False
    
    def __is_next_tokens(self, length):
        if self.__current_token_index + length < len(self.__token_array):
            return True
        return False
        
    def __get_next_token(self):
        self.__current_token_index += 1
        current_token = self.__token_array[self.__current_token_index]
        return current_token     
    
    def __match_next_tokens(self, tokens):
        for index in range(len(tokens)):
            if self.__token_array[self.__current_token_index+1+index] != tokens[index]:
                return False
        return True
            
        
    #Program = "PROGRAM" identifier ";" Declarations ["BEGIN" Instructions] "END" identifier "." 
    def parse(self):
        exception_exist = True
        before_declaration = True
        need_begin = True
        need_declaration = True
        need_instruction = False
        
        while exception_exist:
            try:
                if before_declaration:
                    self.__output.add_output('Program', self.__current_level)
                    #create a universe scope before it start parsing, and insert the singleton instance of the Integer class.
                    self.__factory.create_scope()
                    integer_type = Integer.get_instance()
                    token = Token('Integer','INTEGER',0,0,0)
                    self.__factory.add_entry(token, integer_type)
                    self.__current_level += 1;
                    self.__expect('PROGRAM')
                    #create a program scope with the universe as its "outer" scope
                    self.__factory.create_scope()
                    self.__expect('identifier')
                    self.__program_value = self.__get_current_token().get_token_value()
                    self.__expect(';')
                
                if need_declaration:
                    self.__declarations()
                    
                if need_begin:
                    current_token = self.__get_next_token()
                    if current_token.get_token_name() == 'BEGIN':
                        instruction_node = self.__instructions()
                        if type(self.__output) == AstAscOutput:
                            self.__output.add_semantic_output('instructions =>\n')
                        self.__factory.create_ast(instruction_node)
                    else:
                        self.__current_token_index -= 1
                        
                if need_instruction:
                    instruction_node = self.__instructions()
                    if type(self.__output) == AstAscOutput:
                            self.__output.add_semantic_output('instructions =>\n')
                    self.__factory.create_ast(instruction_node)
                self.__expect('END')
                self.__expect('identifier')
                #if the identifier after program and the corresponding identifier after the END is not identical
                if self.__get_current_token().get_token_value() != self.__program_value:
                    self.__error('error: the identifier after PROGRAM and the corresponding identifier after corresponding END is not identical')
                self.__expect('.')
                self.__factory.delete_scope()
                self.__current_level -= 1;
                self.__factory.delete_scope()
                exception_exist = False
            
            except FindDeclException:
                exception_exist = True
                before_declaration = False
                need_declaration = True
                need_begin = True
                need_instruction = False
                self.__current_level = 1
            
            except FindBeginException:
                exception_exist = True
                before_declaration = False
                need_declaration = False
                need_begin = True
                need_instruction = False
                self.__current_level = 1
                
            except FindInstructException:
                before_declaration = False
                need_declaration = False
                need_begin = False
                need_instruction = True
                self.__current_level = 1
                
            except EndException:
                self.__current_level = 0
                return
            
            except Exception:
                print 'exception cased:'
                current_token = self.__get_current_token()
                print 'token_name:' + current_token.get_token_name() + 'token_value:' + current_token.get_token_value()
                print 'Line:' + str(current_token.get_line_number())
    
    """
        This function defines the ways for error handling
    """
    def __error_handling(self, expect_symbol):
        expect_string = ''
        if type(expect_symbol) == type(''):
            expect_string = expect_symbol
        else:
            for i in expect_symbol:
                expect_string += i + ','
        is_report_error = True
        if self.__is_error_handling == False:
            self.__is_error_handling = True
            self.__start_error_index = self.__current_token_index
            is_report_error = True
        else:
            if self.__current_token_index - self.__start_error_index > 8:
                self.__start_error_index = self.__current_token_index
                is_report_error = True
            else:
                is_report_error = False
                
        #if a weak symbol is missing, the parser assumes that the symbol was actually present  
        if expect_symbol in weak_symbol:
            self.__current_token_index -= 1
            if is_report_error == True:
                self.__error('error: ' + 'expect:\'' + expect_string + '\'  Line:' + str(self.__get_current_token().get_line_number()) + ', Position:' + str(self.__get_current_token().get_token_end_index()+1))
            return 
        
        #Other wise, find the strong symbol 
        else:
            current_token = self.__get_current_token()
            current_token_name = current_token.get_token_name()
            while current_token_name not in strong_symbol:
                if self.__is_next_token() :
                    current_token = self.__get_next_token()
                    current_token_name = current_token.get_token_name()
                else :
                    if is_report_error == True:
                        self.__error('error: ' + 'expect:\'' + expect_string + '\'  Line:' + str(self.__token_array[self.__start_error_index].get_line_number()) + \
                                 ', Position:' + str(self.__token_array[self.__start_error_index].get_token_start_index()))
                    raise EndException()

            if current_token_name == 'CONST' or current_token_name == 'TYPE' or current_token_name == 'VAR':
                self.__current_token_index -= 1
                if is_report_error == True:
                    self.__error('error: ' + 'expect:\'' + expect_string + '\'  Line:' + str(self.__token_array[self.__start_error_index].get_line_number()) + \
                                 ', Position:' + str(self.__token_array[self.__start_error_index].get_token_start_index()))
                raise FindDeclException()
            
            elif current_token_name == 'IF' or current_token_name == 'REPEAT' or current_token_name == 'WHILE' or current_token_name == 'WRITE' or current_token_name == 'READ':
                self.__current_token_index -= 1
                if is_report_error == True:
                    self.__error('error: ' + 'expect:\'' + expect_string + '\'  Line:' + str(self.__token_array[self.__start_error_index].get_line_number()) + \
                                 ', Position:' + str(self.__token_array[self.__start_error_index].get_token_start_index()))                
                raise FindInstructException()
            
            elif current_token_name == 'BEGIN':
                self.__current_token_index -= 1
                if is_report_error == True:
                    self.__error('error: ' + 'expect:\'' + expect_string + '\'  Line:' + str(self.__token_array[self.__start_error_index].get_line_number()) + \
                                 ', Position:' + str(self.__token_array[self.__start_error_index].get_token_start_index()))                
                raise FindBeginException()
        
    #match the next token name with the expect_symbol. 
    def __expect(self, expect_symbol):
        current_token = self.__get_next_token()
        if  current_token.get_token_name() == expect_symbol:
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            return True
        else :
            self.__error_handling(expect_symbol);
            
    def __expect_in_array(self, expect_symbol):
        current_token = self.__get_next_token()
        if current_token.get_token_name() in expect_symbol:
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            return True
        else :
            self.__error_handling(expect_symbol);
            
        
    def __error(self, error_message):
        if error_message != '':
            self.__error_message += error_message + '\n'
    
    def get_error_message(self):
        return self.__error_message
        
    #Declarations = {"CONST" ConstDecl | "TYPE" TypeDecl | "VAR" VarDecl | "PROCEDURE" ProcDecl} 
    def __declarations(self):
        #print 'declarations'
        self.__output.add_output('Declarations', self.__current_level)
        self.__current_level += 1
        current_token = self.__get_next_token()
        current_token_name = current_token.get_token_name()
        while current_token_name == 'CONST' or current_token_name == 'TYPE' or current_token_name == 'VAR' or current_token_name == 'PROCEDURE':
            #ConstDecl = {identifier "=" Expression ";"}
            if current_token_name =='CONST':
                self.__output.add_output('ConstDecl', self.__current_level)
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                current_token = self.__get_next_token()
                entry_token = None
                while current_token.get_token_name() =='identifier':
                    entry_token = current_token
                    self.__output.add_output(current_token.get_display_string(), self.__current_level)
                    self.__expect('=')
                    expression_node = self.__expression()
                    self.__expect(';')
                    #create a new entry in the current scope
                    if type(self.__factory) == AstFactory:
                        if type(expression_node) == AstNumber:
                            length = expression_node.get_constant_value()
                        else:
                            self.__error('error: the expression in the constant declaration must be constant at Line: ' + str(entry_token.get_line_number()))
                            length = 0
                    else:
                        length = 5
                    const_entry = Constant(Integer.get_instance(), length)
                    if self.__factory.add_entry(entry_token, const_entry) == None:
                        self.__error(self.__factory.get_error_message())
                    current_token = self.__get_next_token()
                self.__current_token_index -= 1
                self.__current_level -= 1
                
            #TypeDecl = {identifier "=" Type ";"}
            elif current_token_name == 'TYPE':
                self.__output.add_output('TypeDecl', self.__current_level)
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                current_token = self.__get_next_token()
                while current_token.get_token_name() == 'identifier':
                    entry_token = current_token
                    self.__output.add_output(current_token.get_display_string(), self.__current_level)
                    self.__expect('=')
                    type_object = self.__type()
                    if self.__factory.judge_type(entry_token, type_object) == None:
                        self.__error(self.__factory.get_error_message())
                    self.__expect(';')
                    #create a new entry in the current scope
                    if self.__factory.add_entry(entry_token, type_object) == None:
                        self.__error(self.__factory.get_error_message())
                    current_token = self.__get_next_token()
                self.__current_token_index -= 1
                self.__current_level -= 1
                
            #VarDecl = {IdentifierList ":" Type ";"}
            elif current_token_name == 'VAR':
                self.__output.add_output('VarDecl', self.__current_level)
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                #IdentifierList = identifier {"," identifier}
                current_token = self.__get_next_token()
                while current_token.get_token_name() == 'identifier':
                    token_array = []
                    token_array.append(current_token)
                    self.__output.add_output('IdentifierList', self.__current_level)
                    self.__current_level += 1
                    self.__output.add_output(current_token.get_display_string(), self.__current_level)
                    current_token = self.__get_next_token()
                    while current_token.get_token_name() == ',':
                        self.__output.add_output(current_token.get_display_string(), self.__current_level)
                        self.__expect('identifier')
                        current_token = self.__get_current_token()
                        token_array.append(current_token)
                        current_token = self.__get_next_token()
                    self.__current_token_index -= 1
                    self.__current_level -= 1
                    self.__expect(':')
                    type_object = self.__type()
                    self.__expect(';')
                    #put the array of variables to the symbol table
                    for token in token_array:
                        if self.__factory.is_global_scope() == True:
                            var_type = GlobalVariable(type_object)
                        else:
                            var_type = LocalVariable(type_object)
                            
                        if self.__factory.add_entry(token, var_type) == None:
                            self.__error(self.__factory.get_error_message())
                    current_token = self.__get_next_token()
                    
                self.__current_token_index -= 1
                self.__current_level -= 1
                #create a new entry in the current scope
            
            #ProcDecl = "PROCEDURE" identifier "(" [Formals] ")" [":" Type] ";" { VarDecl } 
            #[ "BEGIN" Instructions ] [ "RETURN" Expression ] "END" identifier ";" .
            elif current_token_name == 'PROCEDURE':
                self.__output.add_output('ProcDecl', self.__current_level)
                argument_num = 0
                #create a new scope
                self.__factory.create_scope()
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                self.__expect('identifier')
                entry_token = self.__get_current_token()
                self.__expect('(')
                #Formals = Formal { ";" Formal } .
                #Formal = IdentifierList ":" Type .
                #IdentifierList = identifier {"," identifier} .
                current_token = self.__get_next_token()
                if current_token.get_token_name() == 'identifier':
                    token_array = []
                    token_array.append(current_token)
                    self.__output.add_output('IdentifierList', self.__current_level)
                    self.__current_level += 1
                    self.__output.add_output(current_token.get_display_string(), self.__current_level)
                    current_token = self.__get_next_token()
                    while current_token.get_token_name() == ',':
                        self.__output.add_output(current_token.get_display_string(), self.__current_level)
                        self.__expect('identifier')
                        current_token = self.__get_current_token()
                        token_array.append(current_token)
                        current_token = self.__get_next_token()
                    self.__current_token_index -= 1
                    self.__current_level -= 1
                    self.__expect(':')
                    type_object = self.__type()
                    #put the array of variables to the symbol table
                    for token in token_array:
                        argument_num += 1
                        var_type = FormalVariable(type_object)
                        if self.__factory.add_entry(token, var_type) == None:
                            self.__error(self.__factory.get_error_message())
                            
                    token_array = []
                    current_token = self.__get_next_token()
                    while current_token.get_token_name() == ';':
                        self.__expect('identifier')
                        current_token = self.__get_current_token()
                        token_array.append(current_token)
                        self.__output.add_output('IdentifierList', self.__current_level)
                        self.__current_level += 1
                        self.__output.add_output(current_token.get_display_string(), self.__current_level)
                        current_token = self.__get_next_token()
                        while current_token.get_token_name() == ',':
                            self.__output.add_output(current_token.get_display_string(), self.__current_level)
                            self.__expect('identifier')
                            current_token = self.__get_current_token()
                            token_array.append(current_token)
                            current_token = self.__get_next_token()
                        self.__current_token_index -= 1
                        self.__current_level -= 1
                        self.__expect(':')
                        type_object = self.__type()
                        current_token = self.__get_next_token()
                    self.__current_token_index -= 1
                    self.__current_level -= 1
                    #put the array of variables to the symbol table
                    for token in token_array:
                        argument_num += 1
                        var_type = FormalVariable(type_object)
                        if self.__factory.add_entry(token, var_type) == None:
                            self.__error(self.__factory.get_error_message())
                    
                else:
                    self.__current_token_index -= 1
                    
                    #put the entry of the symbol table from global scope to the current procedure scope
                    global_dictionary = self.__factory.get_global_scope().get_table()
                    for key, value in sorted(global_dictionary.items()):
                        if not self.__factory.get_current_scope().local(key):
                            self.__factory.get_current_scope().get_table().insert(key, value)
                    
                self.__expect(')')
                current_token = self.__get_next_token()
                procedure_type = None
                if current_token.get_token_name() == ':':
                    procedure_type = self.__type()
                    current_token = self.__get_current_token()
                    if type(procedure_type) != Integer:
                        self.__error('the return type of a procedure must be INTEGER at Line: ' + str(current_token.get_line_number()) + ' position: (' + \
                        str(current_token.get_token_start_index()) + ', ' + str(current_token.get_token_end_index()) + ')')
                    
                else:
                    self.__current_token_index -= 1
                self.__expect(';')
                #{ VarDecl }
                self.__declarations()
                
                #create a Procedure object
                procedure_object = Procedure(self.__factory.get_current_scope(), procedure_type, argument_num)
                if self.__factory.add_outer_entry(entry_token, procedure_object) == None:
                    self.__error(self.__factory.get_error_message())
                    
                #[ "BEGIN" Instructions ]
                current_token = self.__get_next_token()
                if current_token.get_token_name() == "BEGIN":
                    procedure_object.set_body_ast(self.__instructions())
                    if type(self.__output) == AstAscOutput:
                        self.__output.add_semantic_output('instructions =>\n')
                else:
                    self.__current_token_index -= 1
                    
                current_token = self.__get_next_token()
                #[ "RETURN" Expression ]
                if current_token.get_token_name() == "RETURN":
                    return_ast = self.__expression()
                    if procedure_type == None:
                        self.__error('the type of the return expression must match the return type declared for the procedure at line: ' + str(return_ast.get_line()) + ' position: (' + \
                        str(return_ast.get_start_position()) + ', ' + str(return_ast.get_end_position()) + ')')
                    elif type(return_ast.get_type()) != Integer:
                        self.__error('the return type of a procedure must be INTEGER at Line: ' + str(return_ast.get_line()) + ' position: (' + \
                        str(return_ast.get_start_position()) + ', ' + str(return_ast.get_end_position()) + ')')
                    else:
                        procedure_object.set_return_ast(return_ast)
                else:
                    self.__current_token_index -= 1
                self.__expect('END')
                self.__expect('identifier')
                
                current_token = self.__get_current_token()
                #if the identifier after the procedure and the corresponding identifier after the END is not identical
                if current_token.get_token_value() != entry_token.get_token_value():
                    self.__error('error: The identifiers after PROCEDURE and the corresponding END must match at line: ' + str(entry_token.get_line_number()) + \
                    ' and Line: ' + str(current_token.get_line_number()) + ', position: (' + str(entry_token.get_token_start_index()) + ', ' + str(entry_token.get_token_end_index()) + ')' + \
                    ' and position: (' + str(current_token.get_token_start_index()) + ', ' + str(current_token.get_token_end_index()) + ')')
                    
                self.__expect(';')
                
                #remove the current scope
                self.__factory.delete_scope()
                    
            current_token = self.__get_next_token()
            current_token_name = current_token.get_token_name()    
        self.__current_token_index -= 1
        self.__current_level -= 1

    
    #Instructions = Instruction {";" Instruction}
    def __instructions(self):
        #print 'instructions'
        self.__output.add_output('Instructions', self.__current_level)
        self.__current_level += 1
        instruction_node = self.__instruction()
        current_instruction_node = instruction_node
        current_token = self.__get_next_token()
        while current_token.get_token_name() == ';':
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            next_instruction_node = self.__instruction()
            if type(self.__factory) == AstFactory:
                current_instruction_node.set_next_instruction(next_instruction_node)
                if instruction_node.get_next_instruction() == None:
                    instruction_node = current_instruction_node
                current_instruction_node = next_instruction_node
            current_token = self.__get_next_token()
        self.__current_token_index -= 1
        self.__current_level -= 1
        return instruction_node
        
    #Expression = ["+"|"-"] Term {("+"|"-") Term}
    def __expression(self):
        #print 'expression'
        self.__output.add_output('Expression', self.__current_level)
        self.__current_level += 1
        current_token = self.__get_next_token()
        negate_expression = False
        if current_token.get_token_name() == '+' or current_token.get_token_name() == '-':
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            if current_token.get_token_name() == '-':
                negate_expression = True
                negate_token = current_token
        else:
            self.__current_token_index -= 1
        last_expression_node = self.__term()
            
        current_token = self.__get_next_token()
        while current_token.get_token_name() == '+' or current_token.get_token_name() == '-':
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            operator_token = current_token
            current_expression_node = self.__term()
            new_expression_node = self.__factory.produce_binary_node(operator_token, last_expression_node, current_expression_node)
            if new_expression_node == None:
                self.__error(self.__factory.get_error_message())
            else:
                last_expression_node = new_expression_node    
            current_token = self.__get_next_token()
        #create the negate expression if needed
        if negate_expression == True:
            number_entry = Constant(Integer.get_instance(), 0)
            new_expression_node = self.__factory.produce_binary_node(negate_token, self.__factory.produce_number_node(number_entry), last_expression_node)
            if new_expression_node == None:
                self.__error(self.__factory.get_error_message())
            else:
                last_expression_node = new_expression_node   
        self.__current_token_index -= 1
        self.__current_level -= 1
        return last_expression_node
        
    #Type = identifier | "ARRAY" Expression "OF" Type | "RECORD" {IdentifierList ":" Type ";"} "END
    def __type(self):
        #print 'type'
        #Type = identifier
        self.__output.add_output('Type', self.__current_level)
        self.__current_level += 1
        expect_array = ['identifier','ARRAY','RECORD']
        self.__expect_in_array(expect_array)
        current_token = self.__get_current_token()
        type_object = None
        if current_token.get_token_name() == 'identifier':
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            #it looks the identifier up in the current scope or the outer scope and returns the associated Type object
            type_object = self.__factory.get_type_object(current_token.get_token_value())
            if type_object == False:
                #print 'error handling'
                self.__error('error: type \"' + current_token.get_token_value() + '\" hasn\'t been declared yet. Line: ' + str(current_token.get_line_number()) + \
                             ', Position:' + str(current_token.get_token_end_index()+1))
                type_object = Integer.get_instance()
            
        #Type = "ARRAY" Expression "OF" Type
        elif current_token.get_token_name() == 'ARRAY':
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            expression_node = self.__expression()
            if type(self.__factory) == AstFactory:
                if type(expression_node) == AstNumber:
                    length = expression_node.get_constant_value()
                    if length <= 0:
                        self.__error('error: The expression in the Type production must be greater than zero, Line: ' + str(current_token.get_line_number()) + \
                             ', Position:' + str(current_token.get_token_end_index()+1))
                        
                else:
                    self.__error('error: The expression in the Type production must be constant, of type integer, Line: ' + str(current_token.get_line_number()) + \
                             ', Position:' + str(current_token.get_token_end_index()+1))
            else:
                length = 5
            
            self.__expect('OF')
            type_object = self.__type()
            type_object = Array(type_object, length)
            
        #Type = "RECORD" {IdentifierList ":" Type ";"} "END
        elif current_token.get_token_name() == 'RECORD':
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            #create a new scope
            self.__factory.create_scope()
            #IdentifierList = identifier {"," identifier}
            current_token = self.__get_next_token()
            while current_token.get_token_name() == 'identifier':
                token_array = []
                token_array.append(current_token)
                self.__output.add_output('IdentifierList', self.__current_level)
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                current_token = self.__get_next_token()
                while current_token.get_token_name() == ',':
                    self.__expect('identifier')
                    current_token = self.__get_current_token()
                    token_array.append(current_token)
                    current_token = self.__get_next_token()  
                self.__current_token_index -= 1
                self.__expect(':')
                type_object = self.__type()
                self.__expect(';')
                self.__current_level -= 1
                #put the array of variables to the symbol table
                for token in token_array:
                    var_type = LocalVariable(type_object)
                    if self.__factory.add_entry(token, var_type) == None:
                        self.__error(self.__factory.get_error_message())
                current_token = self.__get_next_token()
            self.__current_token_index -= 1
            self.__expect('END')
            #create the actual Record type object
            type_object = Record(self.__factory.get_current_scope())
            #remove the current scope
            self.__factory.delete_scope()
        self.__current_level -= 1
        return type_object
    
    #VarDecl = "VAR" {IdentifierList ":" Type ";"}
    def __vardecl(self):
        #print 'VarDecl'
        self.__output.add_output('VarDecl', self.__current_level)
        self.__current_level += 1
        if self.__expect('VAR'):
            #IdentifierList = identifier {"," identifier}
            current_token = self.__get_next_token()
            while current_token.get_token_name() == 'identifier':
                self.__output.add_output('IdentifierList', self.__current_level)
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                current_token = self.__get_next_token()
                while current_token == ',':
                    self.__expect('identifier')
                self.__current_token_index -= 1
                self.__expect(':')
                self.__type()
                self.__expect(';')
                current_token = self.__get_next_token()
            self.__current_token_index -= 1
        self.__current_level -= 1
              
    #Term = Factor {("*"|"DIV"|"MOD") Factor}
    def __term(self):
        #print 'term'
        self.__output.add_output('Term', self.__current_level)
        self.__current_level += 1
        term_node = self.__factor()
        current_token = self.__get_next_token()
        while current_token.get_token_name() == '*' or current_token.get_token_name() == 'DIV' or current_token.get_token_name() == 'MOD':
            self.__output.add_output(current_token.get_token_name(), self.__current_level)
            current_term_node = self.__factor()
            new_term_node = self.__factory.produce_binary_node(current_token, term_node, current_term_node)
            if new_term_node == None:
                self.__error(self.__factory.get_error_message())
            else:
                term_node = new_term_node
            current_token = self.__get_next_token()
        self.__current_token_index -= 1
        self.__current_level -= 1
        return term_node
        
    #Factor = integer | Designator | "(" Expression ")" | Call
    def __factor(self):
        factor_node = None
        #print 'factor'
        self.__output.add_output('Factor', self.__current_level)
        self.__current_level += 1
        expect_array = ['integer','identifier','(']
        self.__expect_in_array(expect_array)
        current_token = self.__get_current_token()
        if current_token.get_token_name() == 'integer':
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            #create an AST node based on the current token
            factor_node = self.__factory.create_node(current_token)
            #if there exist some errors 
            if factor_node == None:
                self.__error(self.__factory.get_error_message())
                number_entry = Constant(Integer.get_instance(), 0)
                factor_node = self.__factory.produce_number_node(number_entry)

        #Designator = identifier Selector   or 
        #Call = identifier "(" [Actuals] ")" .
        elif current_token.get_token_name() == 'identifier':
            #Call = identifier "(" [Actuals] ")" .  Actuals = ExpressionList
            if type(self.__factory.get_type_object(current_token.get_token_value())) == Procedure:
                start_token = current_token
                self.__output.add_output('Call', self.__current_level)
                self.__current_level += 1 
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                self.__expect('(')
                formal_node_array = self.__expressionlist()
                current_token = self.__get_current_token()
                table_entry = self.__factory.get_type_object(start_token.get_token_value())
                if len(formal_node_array) != table_entry.get_argument_num():
                    self.__error('the number of the actual parameters supplied for a call must match the number of the corresponding formal parameters of' + \
                    'the called procedure at Line: ' + str(start_token.get_line_number()) + ' position: (' + \
                    str(start_token.get_token_start_index()) + ', ' + str(self.get_token_end_index()) + ')')
                factor_node = self.__factory.produce_function_call_node(current_token, formal_node_array, table_entry)
                self.__expect(')')
            
            #Designator = identifier Selector
            else:
                self.__output.add_output('Designator', self.__current_level)
                self.__current_level += 1 
                self.__output.add_output(current_token.get_display_string(), self.__current_level) 
                #create an AST node based on the current token
                factor_node = self.__factory.create_node(current_token)
                #if there exists some errors
                if factor_node == None:
                    self.__error(self.__factory.get_error_message())
                    number_entry = Constant(Integer.get_instance(), 0)
                    factor_node = self.__factory.produce_number_node(number_entry)
                factor_node = self.__selector(factor_node)
            
        #Factor = "(" Expression ")"
        elif current_token.get_token_name() == '(':
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            factor_node = self.__expression()
            self.__expect(')')
        self.__current_level -= 1
        return factor_node
        
    #Instruction = Assign | If | Repeat | While | Read | Write | Call
    def __instruction(self):
        #print 'instruction'
        self.__output.add_output('Instruction', self.__current_level)
        self.__current_level += 1
        expect_array = ['identifier','IF','REPEAT','WHILE','READ','WRITE']
        self.__expect_in_array(expect_array)
        
        current_token = self.__get_current_token()
        if current_token.get_token_name() == 'identifier':
            #Instruction = Call
            #Call = identifier "(" [Actuals] ")" .  
            #Actuals = ExpressionList
            if type(self.__factory.get_type_object(current_token.get_token_value())) == Procedure:
                self.__output.add_output('Call', self.__current_level)
                self.__current_level += 1 
                self.__output.add_output(current_token.get_display_string(), self.__current_level)
                self.__expect('(')
                formal_node_array = self.__expressionlist()
                self.__expect(')')                
                #create a call node in AST
                table_entry = self.__factory.get_type_object(current_token.get_token_value())
                instruction_node = self.__factory.produce_procedure_call_node(current_token, formal_node_array, table_entry)
                self.__current_level -= 1
                
            #Instruction = Assign
            #Assign = Designator ":=" Expression
            #Designator = identifier Selector
            else:
                self.__output.add_output('Assign', self.__current_level) 
                self.__current_level += 1
                self.__output.add_output('Designator', self.__current_level) 
                self.__current_level += 1
                self.__output.add_output(current_token.get_display_string(), self.__current_level) 
                left_location_node = self.__factory.create_node(current_token)
                #if there exist some errors 
                if left_location_node == None:
                    self.__error(self.__factory.get_error_message())
                    number_entry = Constant(Integer.get_instance(), 0)
                    left_location_node = self.__factory.produce_number_node(number_entry)
                
                location_node = self.__selector(left_location_node)
                self.__expect(':=')
                expression_node = self.__expression()
                #create a assign node in AST
                instruction_node = self.__factory.produce_assign_node(location_node, expression_node)
                self.__current_level -= 2
            
        #Instruction = If
        #If = "IF" Condition "THEN" Instructions ["ELSE" Instructions] "END"
        elif current_token.get_token_name() == 'IF':
            self.__output.add_output('If', self.__current_level) 
            self.__current_level += 1
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            condition_node = self.__condition()
            self.__expect('THEN')
            true_instruction_node = self.__instructions()
            current_token = self.__get_next_token()
            false_instruction_node = None
            if current_token.get_token_name() == 'ELSE':
                self.__output.add_output(current_token.get_display_string(), self.__current_level) 
                false_instruction_node = self.__instructions()
            else :
                self.__current_token_index -= 1
            #create a if node in AST
            instruction_node = self.__factory.produce_if_node(condition_node, true_instruction_node, false_instruction_node)
            self.__expect('END')
            self.__current_level -= 1
            
        #Instruction = Repeat
        #Repeat = "REPEAT" Instructions "UNTIL" Condition "END"
        elif current_token.get_token_name() == 'REPEAT':
            self.__output.add_output('Repeat', self.__current_level) 
            self.__current_level += 1
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            instruction_node = self.__instructions()
            self.__expect('UNTIL')
            condition_node = self.__condition()
            #create the repeat node in AST
            instruction_node = self.__factory.produce_repeat_node(condition_node, instruction_node)
            self.__expect('END')
            self.__current_level -= 1
            
        #Instruction = While
        #While = "WHLIE" Condition "DO" Instructions "END"    
        elif current_token.get_token_name() == 'WHILE':
            self.__output.add_output('While', self.__current_level) 
            self.__current_level += 1
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            condition_node = self.__condition()
            self.__expect('DO')
            instruction_node = self.__instructions()
            #we create a repeat node first
            new_condition_node = self.__factory.reverse_condition(condition_node)
            repeat_node = self.__factory.produce_repeat_node(new_condition_node, instruction_node)
            #we create a if node as the parent node of repeat node
            instruction_node = self.__factory.produce_if_node(condition_node, repeat_node, None)
            self.__expect('END')
            self.__current_level -= 1
            
        #Instruction = Read
        #Read = "READ" Designator
        elif current_token.get_token_name() == 'READ':
            self.__output.add_output('Read', self.__current_level) 
            self.__current_level += 1
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            #Designator = identifier Selector
            self.__output.add_output('Designator', self.__current_level) 
            self.__current_level += 1
            self.__expect('identifier')
            current_token = self.__get_current_token()
            location_node = self.__factory.create_node(current_token)
            #if there exist some errors 
            if location_node == None:
                self.__error(self.__factory.get_error_message())
                number_entry = Constant(Integer.get_instance(), 0)
                location_node = self.__factory.produce_number_node(number_entry)
            location_node = self.__selector(location_node)
            #create a read node in AST
            read_node = self.__factory.produce_read_node(location_node)
            if read_node == None:
                self.__error(self.__factory.get_error_message())
                number_entry = Constant(Integer.get_instance(), 0)
                instruction_node = self.__factory.produce_number_node(number_entry)
            else:
                instruction_node = read_node
            self.__current_level -= 2
            
        #Instruction = Write
        #Write = "WRITE" Expression   
        elif current_token.get_token_name() == 'WRITE':
            self.__output.add_output('Write', self.__current_level) 
            self.__current_level += 1
            self.__output.add_output(current_token.get_display_string(), self.__current_level)
            expression_node = self.__expression()
            #create a write node in AST
            write_node = self.__factory.produce_write_node(expression_node)
            if write_node == None:
                self.__error(self.__factory.get_error_message())
                #I just use the integer 0 to replace the expression
                number_entry = Constant(Integer.get_instance(), 0)
                instruction_node = self.__factory.produce_number_node(number_entry)
            else:
                instruction_node = write_node
                
            self.__current_level -= 1
        
        self.__current_level -= 1
        return instruction_node
        
    #Condition = Expression ("="|"#"|"<"|">"|"<="|">=) Expression
    def __condition(self):
        #print 'condition'
        self.__output.add_output('Condition', self.__current_level) 
        self.__current_level += 1
        left_expression_node = self.__expression()
        match_array = ['=','#','<','>','<=','>=']
        self.__expect_in_array(match_array)
        relation_token = self.__get_current_token()
        right_expression_node = self.__expression()
        #create a new condition node
        condition_node = self.__factory.produce_condition_node(relation_token, left_expression_node, right_expression_node)
        self.__current_level -= 1
        return condition_node
        
    #Selector = {"[" ExpressionList "]" | "." identifier}
    def __selector(self, left_location_node):
        #print 'selector'
        self.__output.add_output('Selector', self.__current_level) 
        self.__current_level += 1
        root_node = copy.copy(left_location_node)
        current_token = self.__get_next_token()
        current_token_name = current_token.get_token_name()
        while current_token_name == '[' or current_token_name == '.':
            if current_token_name == '[':
                self.__output.add_output(current_token.get_display_string(), self.__current_level) 
                expression_node_array = self.__expressionlist()
                self.__expect(']')
                #for each expression node, build a new index node as their parent's node in AST
                for expression_node in expression_node_array:
                    root_node = self.__factory.produce_index_node(root_node, expression_node)
                    if root_node == None:
                        self.__error(self.__factory.get_error_message())
                        root_node = copy.copy(left_location_node)
                    
            elif current_token_name == '.':
                self.__expect('identifier')
                #build a variable node first and build a field node as their parent's node in AST
                current_token = self.__get_current_token()
                root_node = self.__factory.produce_field_node(root_node, current_token)
                if root_node == None:
                    self.__error(self.__factory.get_error_message())
                    root_node = copy.copy(left_location_node)
                
            current_token = self.__get_next_token()
            current_token_name = current_token.get_token_name()
        self.__current_token_index -= 1
        self.__current_level -= 1
        return root_node
    
    #ExpressionList = Expression {"," Expression}
    def __expressionlist(self):
        expression_node_array = []
        #print 'expressionList'
        self.__output.add_output('ExpressionList', self.__current_level) 
        self.__current_level += 1
        expression_node_array.append(self.__expression())
        current_token = self.__get_next_token()
        while current_token.get_token_name() == ',':
            self.__output.add_output(current_token.get_display_string(), self.__current_level) 
            expression_node_array.append(self.__expression())
            current_token = self.__get_next_token()
        self.__current_token_index -= 1
        self.__current_level -= 1
        return expression_node_array

    